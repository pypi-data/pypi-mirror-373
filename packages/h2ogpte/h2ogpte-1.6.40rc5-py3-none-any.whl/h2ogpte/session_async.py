import asyncio
import ssl
import sys
import random
import json
import uuid
import websockets.client
from websockets.legacy.client import connect as ws_old_connect
from dataclasses import asdict
from datetime import datetime
from types import TracebackType
from typing import TYPE_CHECKING, Any, Callable, Union, Dict, Type, Optional, List
from urllib.parse import urlparse

from websockets.exceptions import (
    ConnectionClosed,
    ConnectionClosedOK,
    ConnectionClosedError,
    InvalidURI,
    InvalidHandshake,
)

if TYPE_CHECKING:
    from h2ogpte.h2ogpte_async import H2OGPTEAsync

from h2ogpte.types import (
    ChatAcknowledgement,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    SessionError,
)
from h2ogpte.errors import (
    UnauthorizedError,
    ErrorResponse,
)
from h2ogpte.session import deserialize


class SessionAsync:
    """Create and participate in a chat session.
    This is a live connection to the h2oGPTe server contained to a specific
    chat session on top of a single collection of documents. Users will find all
    questions and responses in this session in a single chat history in the
    UI.
    See Also:
        H2OGPTE.connect: To initialize a session on an existing connection.
    Args:
        address:
                Full URL of the h2oGPTe server to connect to.
        api_key:
                API key for authentication to the h2oGPTe server. Users can generate
                a key by accessing the UI and navigating to the Settings.
        chat_session_id:
                The ID of the chat session the queries should be sent to.
        verify:
                Whether to verify the server's TLS/SSL certificate.
                Can be a boolean or a path to a CA bundle. Defaults to True.
    Examples::
        async with h2ogpte.connect(_chat_session_id) as session:
            answer1 = await session.query(
                'How many paper clips were shipped to Scranton?'
            )
            answer2 = await session.query(
                'Did David Brent co-sign the contract with Initech?'
            )
    """

    def __init__(
        self,
        chat_session_id: str,
        client: "H2OGPTEAsync",
        prompt_template_id: Optional[str] = None,
        open_timeout: int = 10,
        close_timeout: int = 10,
        max_connect_retries: int = 10,
        connect_retry_delay: int = 0.5,
        connect_retry_max_delay: int = 60,
    ):
        self._chat_session_id = chat_session_id
        self._client = client
        self._websocket: Optional[websockets.client.WebSocketClientProtocol] = None
        # Keeps track of "in-flight" queries (multiple queries may be fired at the
        # same time):
        self._messages: list["_QueryInfo"] = []
        self._prompt_template_id: Optional[str] = prompt_template_id
        self._prompt_template = None  # created by __enter__
        self._open_timeout = open_timeout
        self._close_timeout = close_timeout
        self._max_connect_retries = max_connect_retries
        self._connect_retry_delay = connect_retry_delay
        self._connect_retry_max_delay = connect_retry_max_delay

    async def query(
        self,
        message: str,
        *,
        system_prompt: Optional[str] = None,
        pre_prompt_query: Optional[str] = None,
        prompt_query: Optional[str] = None,
        image_batch_image_prompt: Optional[str] = None,
        image_batch_final_prompt: Optional[str] = None,
        pre_prompt_summary: Optional[str] = None,
        prompt_summary: Optional[str] = None,
        llm: Union[str, int, None] = None,
        llm_args: Optional[Dict[str, Any]] = None,
        self_reflection_config: Optional[Dict[str, Any]] = None,
        rag_config: Optional[Dict[str, Any]] = None,
        include_chat_history: Optional[Union[bool, str]] = "auto",
        tags: Optional[List[str]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        retries: int = 3,
        callback: Optional[Callable[[ChatMessage], None]] = None,
    ) -> ChatMessage:
        """Retrieval-augmented generation for a query on a collection.
        Finds a collection of chunks relevant to the query using similarity scores.
        Sends these and any additional instructions to an LLM.
        Format of questions or imperatives::
            "{pre_prompt_query}
            \"\"\"
            {similar_context_chunks}
            \"\"\"\
            {prompt_query}{message}"
        Args:
            message:
                Query or instruction from the end user to the LLM.
            system_prompt:
                Text sent to models which support system prompts. Gives the model
                overall context in how to respond. Use `auto` or None for the model
                default. Defaults to '' for no system prompt.
            pre_prompt_query:
                Text that is prepended before the contextual document chunks. The
                default can be customized per environment, but the standard default is
                :code:`"Pay attention and remember the information below, which will
                help to answer the question or imperative after the context ends.\\\\n"`
            prompt_query:
                Text that is appended to the beginning of the user's message. The
                default can be customized per environment, but the standard default is
                "According to only the information in the document sources provided
                within the context above, "
            image_batch_final_prompt:
                Prompt for each image batch for vision models
            image_batch_image_prompt:
                Prompt to reduce all answers each image batch for vision models
            pre_prompt_summary:
                Not used, use H2OGPTE.process_document to summarize.
            prompt_summary:
                Not used, use H2OGPTE.process_document to summarize.
            llm:
                Name or index of LLM to send the query. Use `H2OGPTE.get_llms()` to see
                all available options.
                Use None or "auto" for automatic model routing, set cost_controls for detailed control over automatic routing.
            llm_args:
                Dictionary of kwargs to pass to the llm. Valid keys:
                    temperature (float, default: 0) — The value used to modulate the next token probabilities. Most deterministic: 0, Most creative: 1
                    top_k (int, default: 1) — The number of highest probability vocabulary tokens to keep for top-k-filtering.
                    top_p (float, default: 1.0) — If set to float < 1, only the smallest set of most probable tokens with probabilities that add up to top_p or higher are kept for generation.
                    seed (int, default: 0) — The seed for the random number generator when sampling during generation (if temp>0 or top_k>1 or top_p<1), seed=0 picks a random seed.
                    repetition_penalty (float, default: 1.07) — The parameter for repetition penalty. 1.0 means no penalty.
                    max_new_tokens (int, default: 1024) — Maximum number of new tokens to generate. This limit applies to each (map+reduce) step during summarization and each (map) step during extraction.
                    min_max_new_tokens (int, default: 512) — minimum value for max_new_tokens when auto-adjusting for content of prompt, docs, etc.
                    response_format (str, default: "text") — Output type, one of ["text", "json_object", "json_code"].
                    guided_json (dict, default: None) — If specified, the output will follow the JSON schema.
                    guided_regex (str, default: "") — If specified, the output will follow the regex pattern. Only for models that support guided generation: check output of get_llms() for guided_vllm flag.
                    guided_choice (Optional[List[str]], default: None — If specified, the output will be exactly one of the choices. Only for models that support guided generation: check output of get_llms() for guided_vllm flag.
                    guided_grammar (str, default: "") — If specified, the output will follow the context free grammar. Only for models that support guided generation: check output of get_llms() for guided_vllm flag.
                    guided_whitespace_pattern (str, default: "") — If specified, will override the default whitespace pattern for guided json decoding. Only for models that support guided generation: check output of get_llms() for guided_vllm flag.
                    enable_vision (str, default: "auto") - Controls vision mode, send images to the LLM in addition to text chunks. Only if have models that support vision, use get_vision_capable_llm_names() to see list. One of ["on", "off", "auto"].
                    visible_vision_models (List[str], default: ["auto"]) - Controls which vision model to use when processing images. Use get_vision_capable_llm_names() to see list. Must provide exactly one model. ["auto"] for automatic.
                    images_num_max (int, default: None) — Maximum number of images to process.
                    json_preserve_system_prompt (bool, default: None) — Whether to preserve system prompt in JSON response.
                    client_metadata (str, default: None) — Additional metadata to send with the request.
                    min_chars_per_yield (int, default: 1) — Minimum characters to yield in streaming response.
                    cost_controls: Optional dictionary
                        max_cost (float) - Sets the maximum allowed cost in USD per LLM call when doing Automatic model routing. If the estimated cost based on input and output token counts is higher than this limit, the request will fail as early as possible.
                        max_cost_per_million_tokens (float) - Only consider models that cost less than this value in USD per million tokens when doing automatic routing. Using the max of input and output cost.
                        model (List[str] or None) - Optional subset of models to consider when doing automatic routing. None means consider all models.
                        willingness_to_pay (float) - Controls the willingness to pay extra for a more accurate model for every LLM call when doing automatic routing, in units of USD per +10% increase in accuracy. We start with the least accurate model. For each more accurate model, we accept it if the increase in estimated cost divided by the increase in estimated accuracy is no more than this value divided by 10%, up to the upper limit specified above. Lower values will try to keep the cost as low as possible, higher values will approach the cost limit to increase accuracy. 0 means unlimited.
                        willingness_to_wait (float) - Controls the willingness to wait longer for a more accurate model for every LLM call when doing automatic routing, in units of seconds per +10% increase in accuracy. We start with the least accurate model. For each more accurate model, we accept it if the increase in estimated time divided by the increase in estimated accuracy is no more than this value divided by 10%. Lower values will try to keep the time as low as possible, higher values will take longer to increase accuracy. 0 means unlimited.
                    use_agent (bool, default: False) - If True, use the AI agent (with access to tools) to generate the response.
                    agent_accuracy (str, default: "standard") - Effort level by the agent. Only if use_agent=True. One of ["quick", "basic", "standard", "maximum"].
                    agent_max_turns (Optional[Union[str, int]], default: "auto") - Optional max. number of back-and-forth turns with the agent. Only if use_agent=True. Either "auto" or an integer.
                    agent_tools (Optional[Union[str, List[str]]], default: "auto") - Either "auto", "all", "any" to enable all available tools, or a specific list of tools to use. Only if use_agent=True. Get full list by calling await self._lang("get_agent_tools_options").
                    agent_type (str, default: "auto") — Type of agent to use for task processing.
                    agent_original_files (List[str], default: None) — List of file paths for agent to process.
                    agent_timeout (int, default: None) — Timeout in seconds for each agent turn.
                    agent_total_timeout (int, default: 3600) — Total timeout in seconds for all agent processing.
                    agent_code_writer_system_message (str, default: None) — System message for agent code writer.
                    agent_num_executable_code_blocks_limit (int, default: 1) — Maximum number of executable code blocks.
                    agent_system_site_packages (bool, default: True) — Whether agent has access to system site packages.
                    agent_main_model (Optional[str], default: None) — Main model to use for agent.
                    agent_max_stream_length (Optional[int], default: None) — Maximum stream length for agent response.
                    agent_max_memory_usage (int, default: 16*1024**3) — Maximum memory usage for agent in bytes (16GB default).
                    agent_main_reasoning_effort (Optional[int], default: None) — Effort level for main reasoning.
                    agent_advanced_reasoning_effort (Optional[int], default: None) — Effort level for advanced reasoning.
                    agent_max_confidence_level (Optional[int], default: None) — Maximum confidence level for agent responses.
                    agent_planning_forced_mode (Optional[bool], default: None) — Whether to force planning mode for agent.
                    agent_too_soon_forced_mode (Optional[bool], default: None) — Whether to force "too soon" mode for agent.
                    agent_critique_forced_mode (Optional[int], default: None) — Whether to force critique mode for agent.
                    agent_stream_files (bool, default: True) — Whether to stream files from agent.
            self_reflection_config:
                Dictionary of arguments for self-reflection, can contain the following
                string:string mappings:
                    llm_reflection: str
                        :code:`"gpt-4-0613"`  or :code:`""` to disable reflection
                    prompt_reflection: str
                        'Here\'s the prompt and the response:
                        :code:`\"\"\"Prompt:\\\\n%s\\\\n\"\"\"\\\\n\\\\n\"\"\"
                        Response:\\\\n%s\\\\n\"\"\"\\\\n\\\\nWhat is the quality of the
                        response for the given prompt? Respond with a score ranging
                        from Score: 0/10 (worst) to Score: 10/10 (best), and give a
                        brief explanation why.'`
                    system_prompt_reflection: str
                        :code:`""`
                    llm_args_reflection: str
                        :code:`"{}"`
            rag_config:
                Dictionary of arguments to control RAG (retrieval-augmented-generation)
                types. Can contain the following key/value pairs:
                rag_type: str one of
                    :code:`"auto"` Automatically select the best rag_type.
                    :code:`"llm_only"` LLM Only - Answer the query without any supporting document contexts.
                        Requires 1 LLM or Agent call.
                    :code:`"agent_only"` Agent Only - Answer the query with only original files passed to agent.
                        Requires 1 Agent call.
                    :code:`"rag"` RAG (Retrieval Augmented Generation) - Use supporting document contexts
                        to answer the query. Requires 1 LLM or Agent call.
                    :code:`"hyde1"` LLM Only + RAG composite - HyDE RAG (Hypothetical Document Embedding).
                        Use 'LLM Only' response to find relevant contexts from a collection for generating
                        a response. Requires 2 LLM calls.
                    :code:`"hyde2"` HyDE + RAG composite - Use the 'HyDE RAG' response to find relevant
                        contexts from a collection for generating a response. Requires 3 LLM calls.
                    :code:`"rag+"` Summary RAG - Like RAG, but uses more context and recursive
                        summarization to overcome LLM context limits. Keeps all retrieved chunks, puts
                        them in order, adds neighboring chunks, then uses the summary API to get the
                        answer. Can require several LLM calls.
                    :code:`"all_data"` All Data RAG - Like Summary RAG, but includes all document
                        chunks. Uses recursive summarization to overcome LLM context limits.
                        Can require several LLM calls.
                hyde_no_rag_llm_prompt_extension: str
                    Add this prompt to every user's prompt, when generating answers to be used
                    for subsequent retrieval during HyDE. Only used when rag_type is "hyde1" or "hyde2".
                    example: :code:`'\\\\nKeep the answer brief, and list the 5 most
                    relevant key words at the end.'`
                num_neighbor_chunks_to_include: int
                    Number of neighboring chunks to include for every retrieved relevant chunk. Helps
                    to keep surrounding context together. Only enabled for rag_type "rag+". Defaults to 1.
                meta_data_to_include:
                    A dictionary containing flags that indicate whether each piece of document metadata is to be included as part of the context for a chat with a collection.
                    Default is {
                        "name": True,
                        "text": True,
                        "page": True,
                        "captions": True,
                        "uri": False,
                        "connector": False,
                        "original_mtime": False,
                        "age": False,
                        "score": False,
                    }
                rag_max_chunks:
                    Maximum number of document chunks to retrieve for RAG.
                    If not specified (default: -1), actual number depends on rag_type and admin configuration.
                    Set to >0 values to enable.
                    Can be combined with rag_min_chunk_score.
                rag_min_chunk_score:
                    Minimum score of document chunks to retrieve for RAG.
                    If not specified (default: 0.0), will not filter chunks by score.
                    Set to >0 values to enable.
                    Can be combined with rag_max_chunks.
            include_chat_history:
                Whether to include chat history. Includes previous questions and answers for
                the current chat session for each new chat request. Disable if require deterministic
                answers for a given question.
                Choices are: ["on","off","auto",True,False]
            tags:
                A list of tags from which to pull the context for RAG.
            metadata_filter:
                A dictionary to filter documents by metadata, from which to pull the context for RAG.
            timeout:
                Amount of time in seconds to allow the request to run. The default is
                1000 seconds.
            retries:
                Amount of retries to allow the request to run when hits a network issue. The default is 3.
            callback:
                Function for processing partial messages, used for streaming responses
                to an end user.
        Returns:
            ChatMessage: The response text and details about the response from the LLM.
            For example::
                ChatMessage(
                    id='XXX',
                    content='The information provided in the context...',
                    reply_to='YYY',
                    votes=0,
                    created_at=datetime.datetime(2023, 10, 24, 20, 12, 34, 875026)
                    type_list=[],
                )
        Raises:
            TimeoutError: The request did not complete in time.
        """
        correlation_id = str(uuid.uuid4())
        request = ChatRequest(
            t="cq",
            mode="s",
            session_id=self._chat_session_id,
            correlation_id=correlation_id,
            body=message,
            system_prompt=system_prompt,
            pre_prompt_query=pre_prompt_query,
            prompt_query=prompt_query,
            pre_prompt_summary=pre_prompt_summary,
            prompt_summary=prompt_summary,
            llm=llm,
            llm_args=json.dumps(llm_args),
            self_reflection_config=json.dumps(self_reflection_config),
            rag_config=json.dumps(rag_config),
            include_chat_history=include_chat_history,
            tags=tags,
            metadata_filter=metadata_filter,
            image_batch_image_prompt=image_batch_image_prompt,
            image_batch_final_prompt=image_batch_final_prompt,
        )
        serialized = json.dumps(asdict(request), allow_nan=False, separators=(",", ":"))

        async def send_recv_query() -> ChatMessage:
            await self.websocket.send(serialized)
            info = _QueryInfo(correlation_id=correlation_id, callback=callback)
            self._messages.append(info)
            while not info.done:
                await self._poll()
            del self._messages[self._messages.index(info)]
            assert info.message is not None
            return info.message

        current_retries = 0
        while current_retries < retries:
            try:
                return await asyncio.wait_for(send_recv_query(), timeout=timeout)
            except (ConnectionClosed, ConnectionClosedError) as e:
                current_retries += 1
                if current_retries >= retries:
                    raise e
                print(
                    f"Connection closed with error: {e}, retrying...",
                    file=sys.stderr,
                )
                await asyncio.sleep(0.5)
                await self.connect()

            except ConnectionClosedOK as e:
                current_retries += 1
                if current_retries >= retries:
                    raise e
                print(
                    "Connection closed normally, retrying...",
                    file=sys.stderr,
                )
                await asyncio.sleep(0.5)
                await self.connect()

    async def _poll(self) -> None:
        res = await self.websocket.recv()
        assert isinstance(res, str)
        payloads = res.splitlines()
        for payload in payloads:
            raw = json.loads(payload)
            res = deserialize(payload)

            if res.t == "cr":
                # ignore pre-final in py-client
                continue
            elif res.t == "cx":
                if res.session_id != self._chat_session_id:
                    continue
                self._process_acknowledgment(ChatAcknowledgement(**raw))
            elif res.t == "ce" or res.error:
                if res.session_id != self._chat_session_id:
                    continue
                raise SessionError(ChatResponse(**raw).error)
            elif res.t in ["ca", "cp", "cm"]:
                if res.session_id != self._chat_session_id:
                    continue
                self._process_response_or_partial_response(ChatResponse(**raw))
            else:
                raise SessionError(f"Invalid chat response type: {res.t}")

    def _process_acknowledgment(self, res: ChatAcknowledgement) -> None:
        for msg in self._messages:
            if msg.correlation_id == res.correlation_id:
                msg.query_id = res.message_id
                return
        expected = [msg.correlation_id for msg in self._messages]
        raise SessionError(
            f"Received a response with correlation id `{res.correlation_id}`, "
            f"while expecting any of {expected}"
        )

    def _process_response_or_partial_response(self, res: ChatResponse) -> None:
        info = None
        for msg in self._messages:
            if msg.query_id == res.reply_to_id or msg.message_id == res.message_id:
                info = msg
                break
        if info is None:
            if len(self._messages) == 1:
                info = self._messages[0]
            else:
                raise SessionError(f"Unexpected response {res} without prior ACK")

        info.message_id = res.message_id
        if info.message is None:
            info.message = ChatMessage(
                id=res.message_id,
                content="",
                reply_to=info.query_id,
                votes=0,
                created_at=datetime.now(),
                type_list=[],
            )
        elif not info.message.id:
            info.message.id = info.message_id
        info.message.content = res.body
        if info.callback:
            info.callback(info.message)
        if res.t == "ca":
            info.done = True

    async def connect(self):
        address = self._client._address  # type: ignore[reportPrivateUsage]
        headers = await self._client._get_auth_header()  # type: ignore[reportPrivateUsage]

        url = urlparse(address)
        scheme = "wss" if url.scheme == "https" else "ws"

        if scheme == "wss":
            if isinstance(self._client._verify, str):
                ssl_context = ssl.create_default_context(cafile=self._client._verify)
            elif self._client._verify is True:
                ssl_context = ssl.create_default_context()
            else:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
        else:
            ssl_context = None

        retries = 0
        while retries < self._max_connect_retries:
            try:
                self._websocket = await ws_old_connect(
                    uri=f"{scheme}://{url.netloc}/ws?currentSessionID={self._chat_session_id}",
                    extra_headers=headers,
                    open_timeout=self._open_timeout,
                    close_timeout=self._close_timeout,
                    ssl=ssl_context,
                )
                return self._websocket
            except (ConnectionClosedError, InvalidURI, InvalidHandshake) as e:
                if isinstance(e, InvalidHandshake) and hasattr(e, "response"):
                    status_code = getattr(getattr(e, "response"), "status_code", None)
                    if status_code is not None:
                        self._client._http_code_to_error(
                            status_code, ErrorResponse(error=str(e))
                        )

                retries += 1
                if retries >= self._max_connect_retries:
                    print(
                        f"Failed to connect to {scheme}://{url.netloc}/ws after {self._max_connect_retries} retries.",
                        file=sys.stderr,
                    )
                    raise e
                delay = min(
                    self._connect_retry_max_delay,
                    self._connect_retry_delay * (2**retries),
                ) + random.uniform(0, 1)
                print(
                    f"Connection failed: {e}. Retrying in {delay:.2f} seconds...",
                    file=sys.stderr,
                )
                await asyncio.sleep(delay)

    async def __aenter__(self) -> "SessionAsync":
        await self.connect()

        if self._client and self._prompt_template_id:
            await self._client.set_chat_session_prompt_template(
                self._chat_session_id,
                self._prompt_template_id,
            )
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        await self.websocket.close()

    @property
    def websocket(self) -> websockets.client.WebSocketClientProtocol:
        assert self._websocket is not None
        return self._websocket


class _QueryInfo:
    def __init__(
        self,
        correlation_id: str,
        callback: Optional[Callable[[ChatMessage], None]] = None,
    ):
        self.correlation_id = correlation_id
        self.callback: Optional[Callable[[ChatMessage], None]] = callback
        self.query_id: Optional[str] = None
        self.message_id: Optional[str] = None
        self.done: bool = False
        self.message: Optional[ChatMessage] = None
