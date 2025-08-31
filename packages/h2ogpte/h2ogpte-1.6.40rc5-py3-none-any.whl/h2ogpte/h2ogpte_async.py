import datetime
import os.path
import ast
import io

import aiofiles
import asyncio
import httpx
import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union
from collections import defaultdict
from h2o_authn import AsyncTokenProvider
from urllib.parse import quote
import os

from h2ogpte import rest_async as rest
from h2ogpte.errors import (
    ErrorResponse,
    HTTPError,
    InternalServerError,
    InvalidArgumentError,
    ObjectNotFoundError,
    UnauthorizedError,
    FailedError,
    NotImplementedError,
)

from h2ogpte.session_async import SessionAsync
from h2ogpte.types import (
    Answer,
    ChatMessage,
    ChatMessageFull,
    ChatMessageMeta,
    ChatMessageReference,
    ChatSessionForCollection,
    ChatSessionInfo,
    Chunk,
    Collection,
    CollectionInfo,
    Document,
    DocumentInfo,
    DocumentInfoSummary,
    SuggestedQuestion,
    ExtractionAnswer,
    Identifier,
    Job,
    UserJobs,
    JobKind,
    Meta,
    ObjectCount,
    SharePermission,
    GroupSharePermission,
    QuestionReplyData,
    Result,
    SchedulerStats,
    SearchResult,
    SessionError,
    ShareResponseStatus,
    Tag,
    User,
    LLMUsage,
    LLMUsageLimit,
    PromptTemplate,
    ConfigItem,
    ProcessedDocument,
    DocumentSummary,
    LLMPerformance,
    UserWithLLMUsage,
    LLMWithUserUsage,
    ChatSessionForDocument,
    UserPermission,
    UserRole,
    UserGroup,
    APIKey,
    GlobalConfigItem,
)
from h2ogpte.utils import (
    _process_pdf_with_annotations,
    import_pymupdf,
)
from h2ogpte.connectors import (
    S3Credential,
    GCSServiceAccountCredential,
    AzureKeyCredential,
    AzureSASCredential,
)


class H2OGPTEAsync:
    """
    Connect to and interact with an h2oGPTe server, via an async interface.
    """

    # Timeout for HTTP requests
    TIMEOUT = 3600.0

    INITIAL_WAIT_INTERVAL = 0.1
    MAX_WAIT_INTERVAL = 1.0
    WAIT_BACKOFF_FACTOR = 1.4

    def __init__(
        self,
        address: str,
        api_key: Optional[str] = None,
        token_provider: Optional[AsyncTokenProvider] = None,
        verify: Union[bool, str] = True,
        strict_version_check: bool = False,
    ) -> None:
        """
        Creates a new async H2OGPTE client.
        Args:
            address:
                Full URL of the h2oGPTe server to connect to, e.g.
                "https://h2ogpte.h2o.ai".
            api_key:
                API key for authentication to the h2oGPTe server. Users can generate
                a key by accessing the UI and navigating to the Settings.
            token_provider:
                User's token provider.
            verify:
                Whether to verify the server's TLS/SSL certificate.
                Can be a boolean or a path to a CA bundle. Defaults to True.
            strict_version_check:
                Indicate whether a version check should be enforced.
        """
        self._address = address.rstrip("/ ")
        self._api_key = api_key
        self._verify = verify
        self._token_provider = token_provider
        self._session_id = str(uuid.uuid4())

        if self._api_key is None and self._token_provider is None:
            raise RuntimeError(
                f"Please use either an API key or a Token provider to authenticate."
            )

        if self._api_key is not None and self._token_provider is not None:
            print(
                "Warning: The token_provider parameter will be ignored in favor of the provided api_key"
            )

        self._client = httpx.AsyncClient(
            verify=verify,
        )
        self._strict_version_check = strict_version_check
        self._version_checked = False

    class _RESTClient:
        def __init__(self, h2ogpte):
            self._h2ogpte = h2ogpte
            self._rest_client = None
            self.collection_api = None
            self.document_api = None
            self.model_api = None
            self.chat_api = None
            self.tag_api = None
            self.prompt_template_api = None
            self.ingestion_api = None
            self.job_api = None
            self.model_api = None
            self.system_api = None
            self.permission_api = None
            self.api_keys_api = None
            self.configuration_api = None
            self.agent_api = None
            self.secrets_api = None

        async def __aenter__(self):
            if not self._h2ogpte._version_checked:
                await self._h2ogpte._check_version(
                    self._h2ogpte._strict_version_check
                )  # first time only
                self._h2ogpte._version_checked = True
            verify = (
                self._h2ogpte._verify
                if isinstance(self._h2ogpte._verify, str)
                else None
            )
            configuration = rest.Configuration(
                host=self._h2ogpte._address + "/api/v1", ssl_ca_cert=verify
            )
            if self._h2ogpte._verify in [False]:
                configuration.verify_ssl = False
            self._rest_client = rest.ApiClient(configuration)
            self.collection_api = rest.CollectionsApi(self._rest_client)
            self.document_api = rest.DocumentsApi(self._rest_client)
            self.model_api = rest.ModelsApi(self._rest_client)
            self.chat_api = rest.ChatApi(self._rest_client)
            self.tag_api = rest.TagsApi(self._rest_client)
            self.prompt_template_api = rest.PromptTemplatesApi(self._rest_client)
            self.ingestion_api = rest.DocumentIngestionApi(self._rest_client)
            self.job_api = rest.JobsApi(self._rest_client)
            self.model_api = rest.ModelsApi(self._rest_client)
            self.system_api = rest.SystemApi(self._rest_client)
            self.permission_api = rest.PermissionsApi(self._rest_client)
            self.api_keys_api = rest.APIKeysApi(self._rest_client)
            self.configuration_api = rest.ConfigurationsApi(self._rest_client)
            self.agent_api = rest.AgentsApi(self._rest_client)
            self.secrets_api = rest.SecretsApi(self._rest_client)
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            await self._rest_client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def close(self):
        pass

    async def _get_auth_header(self) -> Dict:
        if self._api_key is not None:
            return {
                "Authorization": f"Bearer {self._api_key}",
            }
        elif self._token_provider is not None:
            token = await self._token_provider.token()
            return {
                "Authorization": f"Bearer-Token {token}",
                "Session-Id": self._session_id,
            }
        else:
            raise Exception(
                "Please provide either an api_key or a token_provider to authenticate."
            )

    async def answer_question(
        self,
        question: str,
        system_prompt: Union[
            str, None
        ] = "",  # "" to disable, 'auto' to use LLMs default, None for h2oGPTe default
        pre_prompt_query: Union[
            str, None
        ] = None,  # "" to disable, None for h2oGPTe default
        prompt_query: Union[
            str, None
        ] = None,  # "" to disable, None for h2oGPTe default
        text_context_list: Optional[List[str]] = None,
        llm: Union[str, int, None] = None,
        llm_args: Optional[Dict[str, Any]] = None,
        chat_conversation: Optional[List[Tuple[str, str]]] = None,
        guardrails_settings: Optional[Dict] = None,
        timeout: Union[float, None] = None,
        **kwargs: Any,
    ) -> Answer:
        """Send a message and get a response from an LLM.

        Note: This method is only recommended if you are passing a chat conversation or for low-volume testing.
        For general chat with an LLM, we recommend session.query() for higher throughput in multi-user environments.
        The following code sample shows the recommended method:

        .. code-block:: python

            # Establish a chat session
            chat_session_id = client.create_chat_session()
            # Connect to the chat session
            with client.connect(chat_session_id) as session:
                # Send a basic query and print the reply
                reply = session.query("Hello", timeout=60)
                print(reply.content)


        Format of inputs content:

            .. code-block::

                {text_context_list}
                \"\"\"\\n{chat_conversation}{question}

        Args:
            question:
                Text query to send to the LLM.
            text_context_list:
                List of raw text strings to be included, will be converted to a string like this: "\n\n".join(text_context_list)
            system_prompt:
                Text sent to models which support system prompts. Gives the model
                overall context in how to respond. Use `auto` for the model default, or None for h2oGPTe default. Defaults
                to '' for no system prompt.
            pre_prompt_query:
                Text that is prepended before the contextual document chunks in text_context_list. Only used if text_context_list is provided.
            prompt_query:
                Text that is appended after the contextual document chunks in text_context_list. Only used if text_context_list is provided.
            llm:
                Name or index of LLM to send the query. Use `H2OGPTE.get_llms()` to see all available options.
                Default value is to use the first model (0th index).
            llm_args:
                Dictionary of kwargs to pass to the llm. Valid keys:
                    temperature (float, default: 0) — The value used to modulate the next token probabilities. Most deterministic: 0, Most creative: 1
                    seed (int, default: 0) — The seed for the random number generator, only used if temperature > 0, seed=0 will pick a random number for each call, seed > 0 will be fixed.
                    top_k (int, default: 1) — The number of highest probability vocabulary tokens to keep for top-k-filtering.
                    top_p (float, default: 1.0) — If set to float < 1, only the smallest set of most probable tokens with probabilities that add up to top_p or higher are kept for generation.
                    repetition_penalty (float, default: 1.07) — The parameter for repetition penalty. 1.0 means no penalty.
                    max_new_tokens (int, default: 1024) — Maximum number of new tokens to generate. This limit applies to each (map+reduce) step during summarization and each (map) step during extraction.
                    min_max_new_tokens (int, default: 512) — minimum value for max_new_tokens when auto-adjusting for content of prompt, docs, etc.
                    response_format (str, default: "text") — Output type, one of ["text", "json_object", "json_code"].
                    guided_json (dict, default: None) — If specified, the output will follow the JSON schema.
                    guided_regex (str, default: "") — If specified, the output will follow the regex pattern. Only for models that support guided generation: check output of get_llms() for guided_vllm flag.
                    guided_choice (Optional[List[str]], default: None — If specified, the output will be exactly one of the choices. Only for models that support guided generation: check output of get_llms() for guided_vllm flag.
                    guided_grammar (str, default: "") — If specified, the output will follow the context free grammar. Only for models that support guided generation: check output of get_llms() for guided_vllm flag.
                    guided_whitespace_pattern (str, default: "") — If specified, will override the default whitespace pattern for guided json decoding. Only for models that support guided generation: check output of get_llms() for guided_vllm flag.
            chat_conversation:
                List of tuples for (human, bot) conversation that will be pre-appended
                to an (question, None) case for a query.
            guardrails_settings:
                Guardrails Settings.
            timeout:
                Timeout in seconds.
            kwargs:
                Dictionary of kwargs to pass to h2oGPT. Not recommended, see https://github.com/h2oai/h2ogpt for source code. Valid keys:
                    h2ogpt_key: str = ""
                    chat_conversation: list[tuple[str, str]] | None = None
                    docs_ordering_type: str | None = "best_near_prompt"
                    max_input_tokens: int = -1
                    docs_token_handling: str = "split_or_merge"
                    docs_joiner: str = "\n\n"
                    image_file: Union[str, list] = None

        Returns:
            Answer: The response text and any errors.
        Raises:
            TimeoutError: If response isn't completed in timeout seconds.
        """

        header = await self._get_auth_header()
        model_name = await self.get_llm_name_for_rest(llm)
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.model_api.answer_question(
                    model_name=model_name,
                    question_request=rest.QuestionRequest(
                        question=question,
                        system_prompt=system_prompt,
                        pre_prompt_query=pre_prompt_query,
                        prompt_query=prompt_query,
                        text_context_list=text_context_list,
                        llm_args=llm_args,
                        chat_conversation=chat_conversation,
                        guardrails_settings=None
                        if guardrails_settings is None
                        else rest.GuardrailsSettings(**guardrails_settings),
                        timeout=timeout,
                        additional_properties=kwargs,
                    ),
                    _headers=header,
                )
            )
        ret = response.to_dict()
        if ret["error"]:
            raise SessionError(ret["error"])
        return Answer(**ret)

    async def get_llm_name_for_rest(self, llm: Union[str, int, None]):
        if llm is None:
            return "auto"
        if isinstance(llm, str):
            return llm
        if isinstance(llm, int):
            llms = await self.get_llms()
            try:
                return llms[llm].get("display_name")
            except IndexError:
                raise IndexError(
                    f"Invalid model index {llm}. Valid range is between 0 and {len(llms)-1}"
                )
        raise ValueError("unexpected type")

    async def summarize_content(
        self,
        text_context_list: Optional[List[str]] = None,
        system_prompt: str = "",  # '' to disable, 'auto' to use LLMs default
        pre_prompt_summary: Optional[str] = None,
        prompt_summary: Optional[str] = None,
        llm: Union[str, int, None] = None,
        llm_args: Optional[Dict[str, Any]] = None,
        guardrails_settings: Optional[Dict] = None,
        timeout: Union[float, None] = None,
        **kwargs: Any,
    ) -> Answer:
        """Summarize one or more contexts using an LLM.

        Effective prompt created (excluding the system prompt):

        .. code-block::

            "{pre_prompt_summary}
            \"\"\"
            {text_context_list}
            \"\"\"
            {prompt_summary}"

        Args:
            text_context_list:
                List of raw text strings to be summarized.
            system_prompt:
                Text sent to models which support system prompts. Gives the model
                overall context in how to respond. Use `auto` for the model default or None for h2oGPTe defaults. Defaults
                to '' for no system prompt.
            pre_prompt_summary:
                Text that is prepended before the list of texts. The default can be
                customized per environment, but the standard default is :code:`"In order to write a concise single-paragraph
                or bulleted list summary, pay attention to the following text:\\\\n"`
            prompt_summary:
                Text that is appended after the list of texts. The default can be customized
                per environment, but the standard default is :code:`"Using only the text above, write a condensed and concise
                summary of key results (preferably as bullet points):\\\\n"`
            llm:
                Name or index of LLM to send the query. Use `H2OGPTE.get_llms()` to see all available options.
                Default value is to use the first model (0th index).
            llm_args:
                Dictionary of kwargs to pass to the llm. Valid keys:
                    temperature (float, default: 0) — The value used to modulate the next token probabilities. Most deterministic: 0, Most creative: 1
                    seed (int, default: 0) — The seed for the random number generator, only used if temperature > 0, seed=0 will pick a random number for each call, seed > 0 will be fixed.
                    top_k (int, default: 1) — The number of highest probability vocabulary tokens to keep for top-k-filtering.
                    top_p (float, default: 1.0) — If set to float < 1, only the smallest set of most probable tokens with probabilities that add up to top_p or higher are kept for generation.
                    repetition_penalty (float, default: 1.07) — The parameter for repetition penalty. 1.0 means no penalty.
                    max_new_tokens (int, default: 1024) — Maximum number of new tokens to generate. This limit applies to each (map+reduce) step during summarization and each (map) step during extraction.
                    min_max_new_tokens (int, default: 512) — minimum value for max_new_tokens when auto-adjusting for content of prompt, docs, etc.
                    response_format (str, default: "text") — Output type, one of ["text", "json_object", "json_code"].
                    guided_json (dict, default: None) — If specified, the output will follow the JSON schema.
                    guided_regex (str, default: "") — If specified, the output will follow the regex pattern. Only for models that support guided generation: check output of get_llms() for guided_vllm flag.
                    guided_choice (Optional[List[str]], default: None — If specified, the output will be exactly one of the choices. Only for models that support guided generation: check output of get_llms() for guided_vllm flag.
                    guided_grammar (str, default: "") — If specified, the output will follow the context free grammar. Only for models that support guided generation: check output of get_llms() for guided_vllm flag.
                    guided_whitespace_pattern (str, default: "") — If specified, will override the default whitespace pattern for guided json decoding. Only for models that support guided generation: check output of get_llms() for guided_vllm flag.
            guardrails_settings:
                Guardrails Settings.
            timeout:
                Timeout in seconds.
            kwargs:
                Dictionary of kwargs to pass to h2oGPT. Not recommended, see https://github.com/h2oai/h2ogpt for source code. Valid keys:
                    h2ogpt_key: str = ""
                    chat_conversation: list[tuple[str, str]] | None = None
                    docs_ordering_type: str | None = "best_near_prompt"
                    max_input_tokens: int = -1
                    docs_token_handling: str = "split_or_merge"
                    docs_joiner: str = "\n\n"
                    image_file: Union[str, list] = None

        Returns:
            Answer: The response text and any errors.
        Raises:
            TimeoutError: If response isn't completed in timeout seconds.
        """
        header = await self._get_auth_header()
        model_name = await self.get_llm_name_for_rest(llm)
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.model_api.summarize_content(
                    model_name=model_name,
                    summarize_request=rest.SummarizeRequest(
                        text_context_list=text_context_list,
                        system_prompt=system_prompt,
                        pre_prompt_summary=pre_prompt_summary,
                        prompt_summary=prompt_summary,
                        llm_args=llm_args,
                        guardrails_settings=None
                        if guardrails_settings is None
                        else rest.GuardrailsSettings(**guardrails_settings),
                        timeout=timeout,
                        additional_properties=kwargs,
                    ),
                    _headers=header,
                )
            )
        ret = response.to_dict()
        if ret["error"]:
            raise SessionError(ret["error"])
        return Answer(**ret)

    async def extract_data(
        self,
        text_context_list: Optional[List[str]] = None,
        system_prompt: str = "",
        pre_prompt_extract: Optional[str] = None,
        prompt_extract: Optional[str] = None,
        llm: Union[str, int, None] = None,
        llm_args: Optional[Dict[str, Any]] = None,
        guardrails_settings: Optional[Dict] = None,
        timeout: Union[float, None] = None,
        **kwargs: Any,
    ) -> ExtractionAnswer:
        """Extract information from one or more contexts using an LLM.

        pre_prompt_extract and prompt_extract variables must be used together. If these
        variables are not set, the inputs texts will be summarized into bullet points.

        Format of extract content:

            .. code-block::

                "{pre_prompt_extract}\"\"\"
                {text_context_list}
                \"\"\"\\n{prompt_extract}"

        Examples:

            .. code-block:: python

                extract = h2ogpte.extract_data(
                    text_context_list=chunks,
                    pre_prompt_extract="Pay attention and look at all people. Your job is to collect their names.\\n",
                    prompt_extract="List all people's names as JSON.",
                )

        Args:
            text_context_list:
                List of raw text strings to extract data from.
            system_prompt:
                Text sent to models which support system prompts. Gives the model
                overall context in how to respond. Use `auto` or None for the model default. Defaults
                to '' for no system prompt.
            pre_prompt_extract:
                Text that is prepended before the list of texts. If not set,
                the inputs will be summarized.
            prompt_extract:
                Text that is appended after the list of texts. If not set, the inputs will be summarized.
            llm:
                Name or index of LLM to send the query. Use `H2OGPTE.get_llms()` to see all available options.
                Default value is to use the first model (0th index).
            llm_args:
                Dictionary of kwargs to pass to the llm. Valid keys:
                    temperature (float, default: 0) — The value used to modulate the next token probabilities. Most deterministic: 0, Most creative: 1
                    seed (int, default: 0) — The seed for the random number generator, only used if temperature > 0, seed=0 will pick a random number for each call, seed > 0 will be fixed.
                    top_k (int, default: 1) — The number of highest probability vocabulary tokens to keep for top-k-filtering.
                    top_p (float, default: 1.0) — If set to float < 1, only the smallest set of most probable tokens with probabilities that add up to top_p or higher are kept for generation.
                    repetition_penalty (float, default: 1.07) — The parameter for repetition penalty. 1.0 means no penalty.
                    max_new_tokens (int, default: 1024) — Maximum number of new tokens to generate. This limit applies to each (map+reduce) step during summarization and each (map) step during extraction.
                    min_max_new_tokens (int, default: 512) — minimum value for max_new_tokens when auto-adjusting for content of prompt, docs, etc.
                    response_format (str, default: "text") — Output type, one of ["text", "json_object", "json_code"].
                    guided_json (dict, default: None) — If specified, the output will follow the JSON schema.
                    guided_regex (str, default: "") — If specified, the output will follow the regex pattern. Only for models that support guided generation: check output of get_llms() for guided_vllm flag.
                    guided_choice (Optional[List[str]], default: None — If specified, the output will be exactly one of the choices. Only for models that support guided generation: check output of get_llms() for guided_vllm flag.
                    guided_grammar (str, default: "") — If specified, the output will follow the context free grammar. Only for models that support guided generation: check output of get_llms() for guided_vllm flag.
                    guided_whitespace_pattern (str, default: "") — If specified, will override the default whitespace pattern for guided json decoding. Only for models that support guided generation: check output of get_llms() for guided_vllm flag.
            guardrails_settings:
                Guardrails Settings.
            timeout:
                Timeout in seconds.
            kwargs:
                Dictionary of kwargs to pass to h2oGPT. Not recommended, see https://github.com/h2oai/h2ogpt for source code. Valid keys:
                    h2ogpt_key: str = ""
                    chat_conversation: list[tuple[str, str]] | None = None
                    docs_ordering_type: str | None = "best_near_prompt"
                    max_input_tokens: int = -1
                    docs_token_handling: str = "split_or_merge"
                    docs_joiner: str = "\n\n"
                    image_file: Union[str, list] = None

        Returns:
            ExtractionAnswer: The list of text responses and any errors.
        Raises:
            TimeoutError: If response isn't completed in timeout seconds.
        """
        header = await self._get_auth_header()
        model_name = await self.get_llm_name_for_rest(llm)
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.model_api.extract_data(
                    model_name=model_name,
                    extraction_request=rest.ExtractionRequest(
                        text_context_list=text_context_list,
                        system_prompt=system_prompt,
                        pre_prompt_extract=pre_prompt_extract,
                        prompt_extract=prompt_extract,
                        llm_args=llm_args,
                        guardrails_settings=None
                        if guardrails_settings is None
                        else rest.GuardrailsSettings(**guardrails_settings),
                        timeout=timeout,
                        additional_properties=kwargs,
                    ),
                    _headers=header,
                )
            )
        ret = response.to_dict()
        if ret["error"]:
            raise SessionError(ret["error"])
        return ExtractionAnswer(**ret)

    async def cancel_job(self, job_id: str) -> Result:
        """Stops a specific job from running on the server.

        Args:
            job_id:
                String id of the job to cancel.

        Returns:
            Result: Status of canceling the job.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.job_api.cancel_job(job_id=job_id, _headers=header)
            )

        return Result(status="completed")

    async def cancel_user_job(self, job_id: str) -> Result:
        """As an admin, stops a specific user job from running on the server.

        Args:
            job_id:
                String id of the job to cancel.

        Returns:
            Result: Status of canceling the job.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.job_api.cancel_user_job(job_id=job_id, _headers=header)
            )

        return Result(status="completed")

    async def count_chat_sessions(self) -> int:
        """Counts number of chat sessions owned by the user.

        Returns:
            int: The count of chat sessions owned by the user.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.chat_api.get_chat_session_count(_headers=header)
            )
        return response.count

    async def count_chat_sessions_for_collection(self, collection_id: str) -> int:
        """Counts number of chat sessions in a specific collection.

        Args:
            collection_id:
                String id of the collection to count chat sessions for.

        Returns:
            int: The count of chat sessions in that collection.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.get_chat_session_count_for_collection(
                    collection_id=collection_id, _headers=header
                )
            )
        return response.count

    async def count_collections(self) -> int:
        """Counts number of collections owned by the user.

        Returns:
            int: The count of collections owned by the user.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.get_collection_count(_headers=header)
            )
        return response.count

    async def count_documents(self) -> int:
        """Counts number of documents accessed by the user.

        Returns:
            int: The count of documents accessed by the user.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.document_api.get_document_count(_headers=header)
            )
        return response.count

    async def count_documents_owned_by_me(self) -> int:
        """Counts number of documents owned by the user.

        Returns:
            int: The count of documents owned by the user.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.document_api.get_document_count(owned=True, _headers=header)
            )
        return response.count

    async def count_documents_in_collection(self, collection_id: str) -> int:
        """Counts the number of documents in a specific collection.

        Args:
            collection_id:
                String id of the collection to count documents for.

        Returns:
            int: The number of documents in that collection.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.get_document_count_for_collection(
                    collection_id=collection_id, _headers=header
                )
            )
        return response.count

    async def count_assets(self) -> ObjectCount:
        """Counts number of objects owned by the user.

        Returns:
            ObjectCount: The count of chat sessions, collections, and documents.
        """
        result = ObjectCount(
            chat_session_count=await self.count_chat_sessions(),
            collection_count=await self.count_collections(),
            document_count=await self.count_documents(),
        )
        return result

    async def create_chat_session(self, collection_id: Optional[str] = None) -> str:
        """Creates a new chat session for asking questions (of documents).

        Args:
            collection_id:
                String id of the collection to chat with.
                If None, chat with LLM directly.

        Returns:
            str: The ID of the newly created chat session.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.chat_api.create_chat_session(
                    collection_id=collection_id, _headers=header
                )
            )
            return response.id

    async def create_chat_session_on_default_collection(self) -> str:
        """Creates a new chat session for asking questions of documents on the default collection.

        Returns:
            str: The ID of the newly created chat session.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.chat_api.create_chat_session(
                    collection_id="default", _headers=header
                )
            )
        return response.id

    async def list_embedding_models(self) -> List[str]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.model_api.list_embedding_models(_headers=header)
            )
        return [m.id for m in response]

    async def run_selftest(self, llm: str, mode: str) -> dict:
        """
        Run a self-test for a given LLM
        Args:
            llm:
                Name of LLM
            mode:
                one of ["quick", "rag", "full", "agent"]
        Returns:
            Dictionary with performance stats. If "error" is filled, the test failed.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.model_api.run_model_self_test(
                    model_name=llm, mode=mode, _headers=header
                )
            )
        return response.to_dict()

    async def get_guardrails_settings(
        self,
        action: str = "redact",
        sensitive: bool = True,
        non_sensitive: bool = True,
        all_guardrails: bool = True,
        guardrails_settings: Union[dict, None] = None,
    ) -> Dict[str, Union[str, List[str]]]:
        """
        Helper to get reasonable (easy to use) defaults for Guardrails/PII settings. To be further customized.
        :param action: what to do when detecting PII, either "redact" or "fail" ("allow" would keep PII intact). Guardrails models always fail upon detecting safety violations.
        :param sensitive: whether to include the most sensitive PII entities like SSN, bank account info
        :param non_sensitive: whether to include all non-sensitive PII entities, such as IP addresses, locations, names, e-mail addresses etc.
        :param all_guardrails: whether to include all possible entities for prompt guard and guardrails models, or just system defaults
        :param guardrails_settings: existing guardrails settings (e.g., from collection settings) to obtain guardrails entities, guardrails_entities_to_flag, column redaction custom_pii_entities, column_redaction_pii_to_flag from instead of system defaults
        :return: dictionary to pass to collection creation or process_document method
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.model_api.create_guardrails_settings(
                    guardrails_settings_create_request=rest.GuardrailsSettingsCreateRequest(
                        action=action,
                        sensitive=sensitive,
                        non_sensitive=non_sensitive,
                        all_guardrails=all_guardrails,
                        guardrails_settings=(
                            None
                            if guardrails_settings is None
                            else rest.GuardrailsSettings(**guardrails_settings)
                        ),
                    ),
                    _headers=header,
                )
            )
        return response.to_dict()

    async def get_agent_tools_dict(self) -> dict:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.agent_api.list_agent_tools(_headers=header)
            )
        return {t.name: t.model_dump(exclude={"name"}) for t in response}

    async def create_collection(
        self,
        name: str,
        description: str,
        embedding_model: Union[str, None] = None,
        prompt_template_id: Union[str, None] = None,
        collection_settings: Union[dict, None] = None,
        thumbnail: Union[Path, None] = None,
        chat_settings: Union[dict, None] = None,
    ) -> str:
        r"""Creates a new collection.

        Args:
            name:
                Name of the collection.
            description:
                Description of the collection
            embedding_model:
                embedding model to use. call list_embedding_models() to list of options.
            prompt_template_id:
                ID of the prompt template to get the prompts from. None to fall back to system defaults.
            collection_settings:
                (Optional) Dictionary with key/value pairs to configure certain collection specific settings
                max_tokens_per_chunk: Approximate max. number of tokens per chunk for text-dominated document pages. For images, chunks can be larger.
                chunk_overlap_tokens: Approximate number of tokens that are overlapping between successive chunks.
                gen_doc_summaries: Whether to auto-generate document summaries (uses LLM)
                gen_doc_questions: Whether to auto-generate sample questions for each document (uses LLM)
                audio_input_language: Language of audio files. Defaults to "auto" language detection. Pass empty string to see choices.
                ocr_model: Which method to use to extract text from images using AI-enabled optical character recognition (OCR) models.
                           Pass empty string to see choices.
                           docTR is best for Latin text, PaddleOCR is best for certain non-Latin languages, Tesseract covers a wide range of languages.
                           Mississippi works well on handwriting.
                           auto - Automatic will auto-select the best OCR model for every page.
                           off - Disable OCR for speed, but all images will then be skipped (also no image captions will be made).
                tesseract_lang: Which language to use when using ocr_model="tesseract". Pass empty string to see choices.
                keep_tables_as_one_chunk: When tables are identified by the table parser the table tokens will be kept in a single chunk.
                chunk_by_page: Each page will be a chunk. `keep_tables_as_one_chunk` will be ignored if this is `true`.
                handwriting_check: Check pages for handwriting. Will use specialized models if handwriting is found.
                follow_links: Whether to import all web pages linked from this URL will be imported. External links will be ignored. Links to other pages on the same domain will be followed as long as they are at the same level or below the URL you specify. Each page will be transformed into a PDF document.
                max_depth: Max depth of recursion when following links, only when follow_links is True. Max_depth of 0 means don't follow any links, max_depth of 1 means follow only top-level links, etc. Use -1 for automatic (system settings).
                max_documents: Max number of documents when following links, only when follow_links is True. Use None for automatic (system defaults). Use -1 for max (system limit).
                root_dir: Root directory for document storage
                copy_document: Whether to copy the document when importing an existing document.
                guardrails_settings itself is a dictionary of the following keys.
                    column_redaction_config: list of list for redacting columns from CSV/TSV files (regex_pattern, fill_value)
                    disallowed_regex_patterns: list of regular expressions that match custom PII
                    presidio_labels_to_flag: list of entities to be flagged as PII by the built-in Presidio model.
                    pii_labels_to_flag: list of entities to be flagged as PII by the built-in PII model.
                    pii_detection_parse_action: what to do when PII is detected during parsing of documents. One of ["allow", "redact", "fail"]. Redact will replace disallowed content in the ingested documents with redaction bars.
                    pii_detection_llm_input_action: what to do when PII is detected in the input to the LLM (document content and user prompts). One of ["allow", "redact", "fail"]. Redact will replace disallowed content with placeholders.
                    pii_detection_llm_output_action: what to do when PII is detected in the output of the LLM. One of ["allow", "redact", "fail"]. Redact will replace disallowed content with placeholders.
                    prompt_guard_labels_to_flag: list of entities to be flagged as safety violations in user prompts by the built-in prompt guard model.
                    guardrails_labels_to_flag: list of entities to be flagged as safety violations in user prompts. Must be a subset of guardrails_entities, if provided.
                    guardrails_safe_category: (Optional) name of the safe category for guardrails. Must be a key in guardrails_entities, if provided. Otherwise uses system defaults.
                    guardrails_entities: (Optional) dictionary of entities and their descriptions for the guardrails model to classify. The first entry is the "safe" class, the rest are "unsafe" classes.
                    column_redaction_custom_entities_to_flag: list of entities to redact in tabular data files. Must be a subset of column_redaction_custom_entities, if provided.
                    column_redaction_custom_entities: (Optional) dictionary of entities and a short description for the LLM to check for and redact columns containing PII in tabular data files.
                    guardrails_llm: LLM to use for guardrails and PII detection. Use "auto" for automatic. Use `H2OGPTE.get_llms()` to see all available options.
                Example:
                    Note: Call client.get_guardrails_settings() to see all options for guardrails_settings.

                    collection_settings=dict(
                        max_tokens_per_chunk=320,
                        chunk_overlap_tokens=0,
                        guardrails_settings=dict(
                            disallowed_regex_patterns=["secret_disallowed_word", r"(?!0{3})(?!6{3})[0-8]\d{2}-(?!0{2})\d{2}-(?!0{4})\d{4}"],
                            presidio_labels_to_flag=["IBAN_CODE", "US_SSN"],
                            pii_labels_to_flag=["IBAN", "SSN"],
                            pii_detection_parse_action="redact",
                            pii_detection_llm_input_action="redact",
                            pii_detection_llm_output_action="allow",
                            prompt_guard_labels_to_flag=["JAILBREAK"],
                            guardrails_labels_to_flag=[
                                "Violent Crimes",
                                "Non-Violent Crimes",
                                "Intellectual Property",
                                "Code Interpreter Abuse",
                            ],
                            guardrails_safe_category="Safe",
                            guardrails_entities={
                                "Safe": "Messages that do not contain any of the following unsafe content",
                                "Violent Crimes": "Messages that enable, encourage, or endorse the commission of violent crimes, including: (1) unlawful violence toward people (ex: terrorism, genocide, murder, hate-motivated violent crimes, child abuse, assault, battery, kidnapping) and (2) unlawful violence toward animals (ex: animal abuse)",
                                "Non-Violent Crimes": "Messages that enable, encourage, or endorse the commission of non-violent crimes, including: (1) personal crimes (ex: labor trafficking, threats, intimidation, hate-motivated non-violent crimes), (2) financial crimes (ex: fraud, scams, money laundering), (3) property crimes (ex: theft, arson, vandalism), (4) drug crimes (ex: creating or using regulated substances), (5) weapons crimes (ex: producing unlicensed firearms), and (6) cyber crimes (ex: hacking)",
                                "Defamation": "Messages that are both verifiably false and likely to injure a living person’s reputation",
                                "Specialized Advice": "Messages that contain specialized financial, medical, or legal advice, or that indicate dangerous activities or objects are safe",
                                "Intellectual Property": "Messages that may violate the intellectual property rights of any third party",
                                "Code Interpreter Abuse": "Messages that seek to abuse code interpreters, including those that enable denial of service attacks, container escapes or privilege escalation exploits",
                            },
                            column_redaction_custom_entities_to_flag=[
                                "Mother's Maiden Name"
                            ],
                            column_redaction_custom_entities={
                                "Mother's Maiden Name": "Mother's maiden name."
                            },
                            guardrails_llm="meta-llama/Llama-3.3-70B-Instruct",
                        ),
                    )
            thumbnail:
                (Optional) Path to the thumbnail image for the collection. Must include appropriate file extension.
            chat_settings:
                (Optional) Dictionary with key/value pairs to configure the default values for certain chat specific settings
                The following keys are supported, see the client.session() documentation for more details.
                llm: str
                llm_args: dict
                self_reflection_config: dict
                rag_config: dict
                include_chat_history: bool
                tags: list[str]
        Returns:
            str: The ID of the newly created collection.
        """
        headers = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            request = rest.CollectionCreateRequest(
                name=name,
                description=description,
                embedding_model=embedding_model,
                collection_settings=rest.CollectionSettings.from_dict(
                    collection_settings
                ),
                chat_settings=rest.ChatSettings.from_dict(chat_settings),
            )
            collection = await _rest_to_client_exceptions(
                rest_client.collection_api.create_collection(request, _headers=headers)
            )

        if prompt_template_id is not None:
            await self.set_collection_prompt_template(collection.id, prompt_template_id)
        if thumbnail is not None:
            await self.set_collection_thumbnail(collection.id, thumbnail)
        return collection.id

    async def set_collection_thumbnail(
        self, collection_id: str, file_path: Path, timeout: Union[float, None] = None
    ):
        """Upload an image file to be set as a collection's thumbnail.

        The image file will not be considered as a collection document.
        Acceptable image file types include: .png, .jpg, .jpeg, .svg

        Args:
            collection_id:
                Collection you want to add the thumbnail to.
            file_path:
                Path to the image file. Must include appropriate file extension.
            timeout:
                Amount of time in seconds to allow the request to run.

        Raises:
            ValueError: The file is invalid.
            Exception: The upload request was unsuccessful.
        """
        async with self._RESTClient(self) as rest_client:
            size = os.stat(file_path).st_size
            if size >= 5242880:
                raise ValueError(
                    "File is too large. Please use an image smaller than 5MB"
                )

            header = await self._get_auth_header()
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.create_update_collection_thumbnail_job(
                    collection_id=collection_id,
                    file=str(file_path),
                    timeout=timeout,
                    _headers=header,
                )
            )
        return await self._wait_for_completion(response.id, timeout=timeout)

    async def remove_collection_thumbnail(
        self, collection_id: str, timeout: Union[float, None] = None
    ):
        """Remove a thumbnail from a collection.

        Args:
            collection_id:
                Collection you want to remove the thumbnail from.
            timeout:
                Amount of time in seconds to allow the request to run. The default is 86400 seconds.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.create_delete_collection_thumbnail_job(
                    collection_id=collection_id, _headers=header
                )
            )
        return await self._wait_for_completion(response.id, timeout=timeout)

    async def create_topic_model(
        self,
        collection_id: str,
        timeout: Union[float, None] = None,
    ) -> Job:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.model_api.create_topic_model_job(
                    create_topic_model_job_request=rest.CreateTopicModelJobRequest(
                        collection_id=collection_id,
                    ),
                    timeout=timeout,
                    _headers=header,
                )
            )
        return await self._wait_for_completion(response.id, timeout=timeout)

    async def delete_chat_sessions(
        self,
        chat_session_ids: Iterable[str],
        timeout: Union[float, None] = None,
    ) -> Job:
        """Deletes chat sessions and related messages.

        Args:
            chat_session_ids:
                List of string ids of chat sessions to delete from the system.
            timeout:
                Timeout in seconds.

        Returns:
            Result: The delete job.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.chat_api.create_delete_chat_session_job(
                    delete_chat_sessions_job_request=rest.DeleteChatSessionsJobRequest(
                        session_ids=chat_session_ids
                    ),
                    _headers=header,
                )
            )
        return await self._wait_for_completion(response.id, timeout=timeout)

    async def delete_chat_messages(self, chat_message_ids: Iterable[str]) -> Result:
        """Deletes specific chat messages.

        Args:
            chat_message_ids:
                List of string ids of chat messages to delete from the system.

        Returns:
            Result: Status of the delete job.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_result(
                _rest_to_client_exceptions(
                    rest_client.chat_api.delete_messages(
                        message_ids=chat_message_ids, _headers=header
                    )
                )
            )
        return result

    async def delete_document_summaries(self, summaries_ids: Iterable[str]) -> Result:
        """Deletes document summaries.

        Args:
            summaries_ids:
                List of string ids of a document summary to delete from the system.

        Returns:
            Result: Status of the delete job.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_result(
                _rest_to_client_exceptions(
                    rest_client.document_api.delete_document_summaries(
                        summary_ids=summaries_ids, _headers=header
                    )
                )
            )
        return result

    async def get_collection_questions(
        self, collection_id: str, limit: int
    ) -> List[SuggestedQuestion]:
        """List suggested questions

        Args:
            collection_id:
                A collection ID of which to return the suggested questions
            limit:
                How many questions to return.

        Returns:
            List: A list of questions.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.list_questions_for_collection(
                    collection_id=collection_id, limit=limit, _headers=header
                )
            )
        return [SuggestedQuestion(**d.to_dict()) for d in response]

    async def get_chat_session_questions(
        self, chat_session_id: str, limit: int
    ) -> List[SuggestedQuestion]:
        """List suggested questions

        Args:
            chat_session_id:
                A chat session ID of which to return the suggested questions
            limit:
                How many questions to return.

        Returns:
            List: A list of questions.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.chat_api.list_questions_for_chat_session(
                    session_id=chat_session_id, limit=limit, _headers=header
                )
            )
        return [SuggestedQuestion(**d.to_dict()) for d in response]

    async def set_collection_expiry_date(
        self, collection_id: str, expiry_date: str, timezone: Optional[str] = None
    ) -> str:
        """Set an expiry date for a collection.

        Args:
            collection_id:
                ID of the collection to update.
            expiry_date:
                The expiry date as a string in 'YYYY-MM-DD' format.
            timezone:
                Optional timezone to associate with expiry date (with IANA timezone support).
        """
        try:
            datetime.datetime.strptime(expiry_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                "Invalid date. Please enter a valid date that follows the 'YYYY-MM-DD' format."
            )

        if timezone is None:
            from tzlocal import get_localzone

            timezone = str(get_localzone())

        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.collection_api.update_collection_expiry_date(
                    collection_id=collection_id,
                    update_collection_expiry_date_request=rest.UpdateCollectionExpiryDateRequest(
                        expiry_date=expiry_date,
                        timezone=timezone,
                    ),
                    _headers=header,
                )
            )
        return collection_id

    async def remove_collection_expiry_date(self, collection_id: str) -> str:
        """Remove an expiry date from a collection.

        Args:
            collection_id:
                ID of the collection to update.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.collection_api.delete_collection_expiry_date(
                    collection_id=collection_id, _headers=header
                )
            )
        return collection_id

    async def set_collection_inactivity_interval(
        self, collection_id: str, inactivity_interval: int
    ) -> str:
        """Set an inactivity interval for a collection.

        Args:
            collection_id:
                ID of the collection to update.
            inactivity_interval:
                The inactivity interval as an integer number of days.
        """
        if not inactivity_interval and (
            inactivity_interval <= 0 or inactivity_interval > 36500
        ):
            raise ValueError(
                "Inactivity interval must be a positive integer and no larger than 36500 days."
            )

        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.collection_api.update_collection_inactivity_interval(
                    collection_id=collection_id,
                    update_collection_inactivity_interval_request=rest.UpdateCollectionInactivityIntervalRequest(
                        inactivity_interval=inactivity_interval
                    ),
                    _headers=header,
                )
            )
        return collection_id

    async def remove_collection_inactivity_interval(self, collection_id: str) -> str:
        """Remove an inactivity interval for a collection.

        Args:
            collection_id:
                ID of the collection to update.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.collection_api.delete_collection_inactivity_interval(
                    collection_id=collection_id, _headers=header
                )
            )
        return collection_id

    async def set_collection_size_limit(
        self, collection_id: str, limit: Union[int, str]
    ) -> str:
        """Set a maximum limit on the total size of documents (sum) added to a collection.
        The limit is measured in bytes.

        Args:
            collection_id:
                ID of the collection to update.
            limit:
                The bytes limit, possible values follow the format: 12345, "1GB", or "1GiB".
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.collection_api.set_collection_size_limit(
                    collection_id=collection_id,
                    set_collection_size_limit_request=rest.SetCollectionSizeLimitRequest(
                        size_limit=str(limit)
                    ),
                    _headers=header,
                )
            )
        return collection_id

    async def remove_collection_size_limit(self, collection_id: str) -> str:
        """Remove a size limit for a collection.

        Args:
            collection_id:
                ID of the collection to update.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.collection_api.remove_collection_size_limit(
                    collection_id=collection_id,
                    _headers=header,
                )
            )
        return collection_id

    async def unarchive_collection(self, collection_id: str) -> str:
        """Restore an archived collection to an active status.

        Args:
            collection_id:
                ID of the collection to restore.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.collection_api.unarchive_collection(
                    collection_id=collection_id, _headers=header
                )
            )
        return collection_id

    async def archive_collection(self, collection_id: str) -> str:
        """Archive a collection along with its associated data.

        Args:
            collection_id:
                ID of the collection to archive.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.collection_api.archive_collection(
                    collection_id=collection_id, _headers=header
                )
            )
        return collection_id

    async def delete_collections(
        self,
        collection_ids: Iterable[str],
        timeout: Union[float, None] = None,
    ) -> Job:
        """Deletes collections from the environment.

        Documents in the collection that are owned by other users will not be deleted.

        Args:
            collection_ids:
                List of string ids of collections to delete from the system.
            timeout:
                Timeout in seconds.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.create_delete_collection_job(
                    rest.DeleteCollectionsJobRequest(collection_ids=collection_ids),
                    _headers=header,
                )
            )
        return await self._wait_for_completion(response.id, timeout=timeout)

    async def delete_collections_as_admin(
        self,
        collection_ids: Iterable[str],
        timeout: Union[float, None] = None,
    ) -> Job:
        """Deletes collections and their associated data from the environment (needs appropriate permission).

        Args:
            collection_ids:
                List of string ids of collections to delete from the system.
            timeout:
                Timeout in seconds.
        """
        ret = await self._job(
            "q:crawl_quick.DeleteCollectionsAsAdminJob", collection_ids=collection_ids
        )
        return await self._wait_for_completion(_to_id(ret), timeout=timeout)

    async def delete_documents(
        self,
        document_ids: Iterable[str],
        timeout: Union[float, None] = None,
    ) -> Job:
        """Deletes documents from the system.

        Args:
            document_ids:
                List of string ids to delete from the system and all collections.
            timeout:
                Timeout in seconds.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.document_api.create_delete_document_job(
                    rest.DeleteDocumentsJobRequest(document_ids=document_ids),
                    _headers=header,
                )
            )
        return await self._wait_for_completion(response.id, timeout=timeout)

    async def delete_documents_from_collection(
        self,
        collection_id: str,
        document_ids: Iterable[str],
        timeout: Union[float, None] = None,
    ) -> Job:
        """Removes documents from a collection.

        See Also: H2OGPTE.delete_documents for completely removing the document from the environment.

        Args:
            collection_id:
                String of the collection to remove documents from.
            document_ids:
                List of string ids to remove from the collection.
            timeout:
                Timeout in seconds.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.create_delete_document_from_collection_job(
                    collection_id=collection_id,
                    delete_documents_job_request=rest.DeleteDocumentsJobRequest(
                        document_ids=document_ids
                    ),
                    _headers=header,
                )
            )
        return await self._wait_for_completion(response.id, timeout=timeout)

    async def import_collection_into_collection(
        self,
        collection_id: str,
        src_collection_id: str,
        gen_doc_summaries: Union[bool, None] = None,
        gen_doc_questions: Union[bool, None] = None,
        copy_document: Union[bool, None] = None,
        ocr_model: Union[str, None] = None,
        tesseract_lang: Union[str, None] = None,
        keep_tables_as_one_chunk: Union[bool, None] = None,
        chunk_by_page: Union[bool, None] = None,
        handwriting_check: Union[bool, None] = None,
        timeout: Union[float, None] = None,
        ingest_mode: Union[str, None] = None,
    ):
        """Import all documents from a collection into an existing collection

        Args:
            collection_id:
                Collection ID to add documents to.
            src_collection_id:
                Collection ID to import documents from.
            gen_doc_summaries:
                Whether to auto-generate document summaries (uses LLM)
            gen_doc_questions:
                Whether to auto-generate sample questions for each document (uses LLM)
            copy_document:
                Whether to save a new copy of the document
            ocr_model:
                Which method to use to extract text from images using AI-enabled optical character recognition (OCR) models.
                Pass empty string to see choices.
                docTR is best for Latin text, PaddleOCR is best for certain non-Latin languages, Tesseract covers a wide range of languages.
                Mississippi works well on handwriting.
                "auto" - Automatic will auto-select the best OCR model for every page.
                "off" - Disable OCR for speed, but all images will then be skipped (also no image captions will be made).
            tesseract_lang:
                Which language to use when using ocr_model="tesseract". Pass empty string to see choices.
            keep_tables_as_one_chunk:
                When tables are identified by the table parser the table tokens will be kept in a single chunk.
            chunk_by_page:
                Each page will be a chunk. `keep_tables_as_one_chunk` will be ignored if this is True.
            handwriting_check:
                Check pages for handwriting. Will use specialized models if handwriting is found.
            timeout:
                Timeout in seconds.
            ingest_mode:
                Ingest mode to use.
                "standard" - Files will be ingested for use with RAG
                "lite" - Files will be ingested for use with RAG, but minimal processing will be done, favoring ingest speed over accuracy
                "agent_only" - Bypasses standard ingestion. Files can only be used with agents.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.create_import_collection_to_collection_job(
                    collection_id=collection_id,
                    create_import_collection_to_collection_job_request=rest.CreateImportCollectionToCollectionJobRequest(
                        source_collection_id=src_collection_id,
                    ),
                    gen_doc_summaries=gen_doc_summaries,
                    gen_doc_questions=gen_doc_questions,
                    copy_document=copy_document,
                    ocr_model=ocr_model,
                    tesseract_lang=tesseract_lang,
                    keep_tables_as_one_chunk=keep_tables_as_one_chunk,
                    chunk_by_page=chunk_by_page,
                    handwriting_check=handwriting_check,
                    ingest_mode=ingest_mode,
                    timeout=timeout,
                    _headers=header,
                )
            )
        return await self._wait_for_completion(response.id, timeout=timeout)

    async def import_document_into_collection(
        self,
        collection_id: str,
        document_id: str,
        gen_doc_summaries: Union[bool, None] = None,
        gen_doc_questions: Union[bool, None] = None,
        copy_document: Union[bool, None] = None,
        ocr_model: Union[str, None] = None,
        tesseract_lang: Union[str, None] = None,
        keep_tables_as_one_chunk: Union[bool, None] = None,
        chunk_by_page: Union[bool, None] = None,
        handwriting_check: Union[bool, None] = None,
        timeout: Union[float, None] = None,
        ingest_mode: Union[str, None] = None,
    ):
        """Import an already stored document to an existing collection

        Args:
            collection_id:
                Collection ID to add documents to.
            document_id:
                Document ID to add.
            gen_doc_summaries:
                Whether to auto-generate document summaries (uses LLM)
            gen_doc_questions:
                Whether to auto-generate sample questions for each document (uses LLM)
            copy_document:
                Whether to save a new copy of the document
            ocr_model:
                Which method to use to extract text from images using AI-enabled optical character recognition (OCR) models.
                Pass empty string to see choices.
                docTR is best for Latin text, PaddleOCR is best for certain non-Latin languages, Tesseract covers a wide range of languages.
                Mississippi works well on handwriting.
                "auto" - Automatic will auto-select the best OCR model for every page.
                "off" - Disable OCR for speed, but all images will then be skipped (also no image captions will be made).
            tesseract_lang:
                Which language to use when using ocr_model="tesseract". Pass empty string to see choices.
            keep_tables_as_one_chunk:
                When tables are identified by the table parser the table tokens will be kept in a single chunk.
            chunk_by_page:
                Each page will be a chunk. `keep_tables_as_one_chunk` will be ignored if this is True.
            handwriting_check:
                Check pages for handwriting. Will use specialized models if handwriting is found.
            timeout:
                Timeout in seconds.
            ingest_mode:
                Ingest mode to use.
                "standard" - Files will be ingested for use with RAG
                "lite" - Files will be ingested for use with RAG, but minimal processing will be done, favoring ingest speed over accuracy
                "agent_only" - Bypasses standard ingestion. Files can only be used with agents.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.create_insert_document_to_collection_job(
                    collection_id=collection_id,
                    create_insert_document_to_collection_job_request=rest.CreateInsertDocumentToCollectionJobRequest(
                        document_id=document_id,
                    ),
                    gen_doc_summaries=gen_doc_summaries,
                    gen_doc_questions=gen_doc_questions,
                    copy_document=copy_document,
                    ocr_model=ocr_model,
                    tesseract_lang=tesseract_lang,
                    keep_tables_as_one_chunk=keep_tables_as_one_chunk,
                    chunk_by_page=chunk_by_page,
                    handwriting_check=handwriting_check,
                    ingest_mode=ingest_mode,
                    timeout=timeout,
                    _headers=header,
                )
            )
        return await self._wait_for_completion(response.id, timeout=timeout)

    async def summarize_document(self, *args, **kwargs) -> DocumentSummary:
        assert not kwargs.get("keep_intermediate_results", False), (
            "Must not set keep_intermediate_results for summarize_document to preserve backward compatibility. "
            "Use process_document instead."
        )
        ret = await self.process_document(*args, **kwargs)
        return DocumentSummary(**ret.model_dump())

    async def process_document(
        self,
        document_id: str,
        system_prompt: Union[str, None] = None,
        pre_prompt_summary: Union[str, None] = None,
        prompt_summary: Union[str, None] = None,
        image_batch_image_prompt: Optional[str] = None,
        image_batch_final_prompt: Optional[str] = None,
        llm: Union[str, int, None] = None,
        llm_args: Optional[Dict[str, Any]] = None,
        max_num_chunks: Union[int, None] = None,
        sampling_strategy: Union[str, None] = None,
        pages: Union[List[int], None] = None,
        schema: Union[Dict[str, Any], None] = None,
        keep_intermediate_results: Union[bool, None] = None,
        guardrails_settings: Optional[Dict] = None,
        meta_data_to_include: Optional[Dict[str, bool]] = None,
        timeout: Optional[float] = None,
    ) -> ProcessedDocument:
        """Processes a document to either create a global or piecewise summary/extraction/transformation of a document.

        Effective prompt created (excluding the system prompt):

        .. code-block::

            "{pre_prompt_summary}
            \"\"\"
            {text from document}
            \"\"\"
            {prompt_summary}"

        Args:
            document_id:
                String id of the document to create a summary from.
            system_prompt:
                System Prompt
            pre_prompt_summary:
                Prompt that goes before each large piece of text to summarize
            prompt_summary:
                Prompt that goes after each large piece of text to summarize
            image_batch_final_prompt:
                Prompt for each image batch for vision models
            image_batch_image_prompt:
                Prompt to reduce all answers each image batch for vision models
            llm:
                LLM to use
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
            max_num_chunks:
                Max limit of chunks to send to the summarizer
            sampling_strategy:
                How to sample if the document has more chunks than max_num_chunks.
                Options are "auto", "uniform", "first", "first+last", default is "auto" (a hybrid of them all).
            pages:
                List of specific pages (of the ingested document in PDF form) to use from the document. 1-based indexing.
            schema:
                Optional JSON schema to use for guided json generation.
            keep_intermediate_results:
                Whether to keep intermediate results. Default: disabled.
                If disabled, further LLM calls are applied to the intermediate results until one global summary is obtained: map+reduce (i.e., summary).
                If enabled, the results' content will be a list of strings (the results of applying the LLM to different pieces of document context): map (i.e., extract).
            guardrails_settings:
                Guardrails Settings.
            meta_data_to_include:
                A dictionary containing flags that indicate whether each piece of document metadata is to be included as part of the context given to the LLM. Only used if enable_vision is disabled.
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
            timeout:
                Amount of time in seconds to allow the request to run. The default is 86400 seconds.

        Returns:
            ProcessedDocument: Processed document. The content is either a string (keep_intermediate_results=False) or a list of strings (keep_intermediate_results=True).

        Raises:
            TimeoutError: The request did not complete in time.
            SessionError: No summary or extraction created. Document wasn't part of a collection, or LLM timed out, etc.
        """
        if isinstance(llm, int):
            names = await self.get_llm_names()
            llm = names[llm]

        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            summary_id = str(uuid.uuid4())
            response = await _rest_to_client_exceptions(
                rest_client.document_api.create_process_document_job(
                    process_document_job_request=rest.ProcessDocumentJobRequest(
                        summary_id=summary_id,
                        document_id=document_id,
                        system_prompt=system_prompt,
                        pre_prompt_summary=pre_prompt_summary,
                        prompt_summary=prompt_summary,
                        llm=llm,
                        llm_args=llm_args,
                        max_num_chunks=max_num_chunks,
                        sampling_strategy=sampling_strategy,
                        pages=pages,
                        keep_intermediate_results=keep_intermediate_results,
                        schema=schema,
                        guardrails_settings=guardrails_settings,
                        meta_data_to_include=meta_data_to_include,
                        timeout=int(timeout) if timeout is not None else None,
                        image_batch_image_prompt=image_batch_image_prompt,
                        image_batch_final_prompt=image_batch_final_prompt,
                    ),
                    _headers=header,
                )
            )
            process_job = await self._wait_for_completion(response.id, timeout=timeout)

            if process_job.failed:
                raise SessionError(str(process_job.errors))

            summary = await _rest_to_client_exceptions(
                rest_client.document_api.get_document_summary(
                    summary_id=summary_id, _headers=header
                )
            )

        if summary.error:
            raise SessionError(summary.error)
        ret = ProcessedDocument(**summary.to_dict())
        if keep_intermediate_results:
            ret.content = ast.literal_eval(summary.content)
        return ret

    async def list_recent_document_summaries(
        self, document_id: str, offset: int, limit: int
    ) -> List[ProcessedDocument]:
        """Fetches recent document summaries/extractions/transformations

        Args:
            document_id:
                document ID for which to return summaries
            offset:
                How many summaries to skip before returning summaries.
            limit:
                How many summaries to return.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.document_api.list_document_summaries(
                    document_id=document_id,
                    offset=offset,
                    limit=limit,
                    _headers=header,
                )
            )

        ret = [ProcessedDocument(**d.to_dict()) for d in response]
        for r in ret:
            kwargs = json.loads(r.kwargs)
            if kwargs.get("keep_intermedidate_results"):
                r.content = ast.literal_eval(r.content)
        return ret

    async def encode_for_retrieval(
        self, chunks: Iterable[str], embedding_model: Union[str, None] = None
    ) -> List[List[float]]:
        """Encode texts for semantic searching.

        See Also: H2OGPTE.match for getting a list of chunks that semantically match
        each encoded text.

        Args:
            chunks:
                List of strings of texts to be encoded.
            embedding_model:
                embedding model to use. call list_embedding_models() to list of options.

        Returns:
            List of list of floats: Each list in the list is the encoded original text.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            if embedding_model is None:
                rest_embedding_model = await _rest_to_client_exceptions(
                    rest_client.model_api.get_default_embedding_model(_headers=header)
                )
                embedding_model = rest_embedding_model.id
            result = await _rest_to_client_exceptions(
                rest_client.model_api.encode_chunks_for_retrieval(
                    encode_chunks_for_retrieval_request=rest.EncodeChunksForRetrievalRequest(
                        chunks=chunks
                    ),
                    model_id=embedding_model,
                    _headers=header,
                )
            )
        return result

    async def get_chunks(
        self, collection_id: str, chunk_ids: Iterable[int]
    ) -> List[Chunk]:
        """Get the text of specific chunks in a collection.

        Args:
            collection_id:
                String id of the collection to search in.
            chunk_ids:
                List of ints for the chunks to return. Chunks are indexed starting at 1.

        Returns:
            Chunk: The text of the chunk.

        Raises:
            Exception: One or more chunks could not be found.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            rest_chunks = await _rest_to_client_exceptions(
                rest_client.collection_api.get_collection_chunks(
                    collection_id=collection_id, chunk_ids=chunk_ids, _headers=header
                )
            )
        return [Chunk(**c.to_dict()) for c in rest_chunks]

    async def get_collection(self, collection_id: str) -> Collection:
        """Get metadata about a collection.

        Args:
            collection_id:
                String id of the collection to search for.

        Returns:
            Collection: Metadata about the collection.

        Raises:
            KeyError: The collection was not found.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            rest_collection = await _rest_to_client_exceptions(
                rest_client.collection_api.get_collection(
                    collection_id=collection_id, _headers=header
                )
            )
            collection = Collection(**rest_collection.to_dict())

            rest_settings = await _rest_to_client_exceptions(
                rest_client.collection_api.get_collection_settings(
                    collection_id=collection_id, _headers=header
                )
            )
            collection.collection_settings = rest_settings.to_dict()

            rest_chat_settings = await _rest_to_client_exceptions(
                rest_client.collection_api.get_collection_chat_settings(
                    collection_id=collection_id, _headers=header
                )
            )
            collection.chat_settings = rest_chat_settings.to_dict()

            metadata = await _rest_to_client_exceptions(
                rest_client.collection_api.get_collection_metadata(
                    collection_id=collection_id, _headers=header
                )
            )
            if metadata != {}:
                collection.metadata_dict = metadata

        return collection

    async def get_collection_for_chat_session(self, chat_session_id: str) -> Collection:
        """Get metadata about the collection of a chat session.

        Args:
            chat_session_id:
                String id of the chat session to search for.

        Returns:
            Collection: Metadata about the collection.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            chat_session = await _rest_to_client_exceptions(
                rest_client.chat_api.get_chat_session(chat_session_id, _headers=header)
            )
        if chat_session.collection_id is None:
            raise ObjectNotFoundError({"error": "Collection not found"})
        return await self.get_collection(chat_session.collection_id)

    async def get_document(
        self, document_id: str, include_layout: bool = False
    ) -> Document:
        """Fetches information about a specific document.

        Args:
            document_id:
                String id of the document.
            include_layout:
                Include the layout prediction results.

        Returns:
            Document: Metadata about the Document.

        Raises:
            KeyError: The document was not found.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            rest_document = await _rest_to_client_exceptions(
                rest_client.document_api.get_document(
                    document_id=document_id, _headers=header
                )
            )
            document = Document(**rest_document.to_dict())

            if include_layout:
                document.page_layout_dict = await _rest_to_client_exceptions(
                    rest_client.document_api.get_document_page_layout(
                        document_id=document_id, _headers=header
                    )
                )

            document.meta_data_dict = await _rest_to_client_exceptions(
                rest_client.document_api.get_document_internal_metadata(
                    document_id=document_id, _headers=header
                )
            )
            document.user_source_file = await _rest_to_client_exceptions(
                rest_client.document_api.get_document_user_source_file(
                    document_id=document_id, _headers=header
                )
            )
            document.page_ocr_model_dict = await _rest_to_client_exceptions(
                rest_client.document_api.get_document_page_ocr_model(
                    document_id=document_id, _headers=header
                )
            )
            rest_guardrails_settings = await _rest_to_client_exceptions(
                rest_client.document_api.get_document_guardrails_settings(
                    document_id=document_id, _headers=header
                )
            )
            if rest_guardrails_settings is not None:
                document.guardrails_settings = rest_guardrails_settings.to_dict()

        return document

    async def get_job(self, job_id: str) -> Job:
        """Fetches information about a specific job.

        Args:
            job_id:
                String id of the job.

        Returns:
            Job: Metadata about the Job.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            rest_job = await _rest_to_client_exceptions(
                rest_client.job_api.get_job(job_id=job_id, _headers=header)
            )
        return _convert_rest_job(rest_job)

    async def get_meta(self) -> Meta:
        """Returns information about the environment and the user.

        Returns:
            Meta: Details about the version and license of the environment and
            the user's name and email.
        """
        response = await self._get("/rpc/meta")
        return Meta(**response)

    async def get_llm_usage_24h(self) -> float:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.model_api.get_usage_stats(
                    interval="24 hours", _headers=header
                )
            )
        return response.current

    async def get_llm_usage_24h_by_llm(self) -> List[LLMUsage]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.model_api.get_usage_stats_by_model(
                    interval="24 hours", _headers=header
                )
            )
        return [LLMUsage(**d.to_dict()) for d in response]

    async def get_llm_usage_24h_with_limits(self) -> LLMUsageLimit:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            usage = await _rest_to_client_exceptions(
                rest_client.model_api.get_usage_stats(
                    interval="24 hours", _headers=header
                )
            )
        return LLMUsageLimit(**usage.to_dict())

    async def get_llm_usage_6h(self) -> float:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.model_api.get_usage_stats(
                    interval="6 hours", _headers=header
                )
            )
        return response.current

    async def get_llm_usage_6h_by_llm(self) -> List[LLMUsage]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.model_api.get_usage_stats_by_model(
                    interval="6 hours", _headers=header
                )
            )
        return [LLMUsage(**d.to_dict()) for d in response]

    async def get_llm_usage_with_limits(self, interval: str) -> LLMUsageLimit:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            usage = await _rest_to_client_exceptions(
                rest_client.model_api.get_usage_stats(
                    interval=interval, _headers=header
                )
            )
        return LLMUsageLimit(**usage.to_dict())

    async def get_llm_usage_by_llm(self, interval: str) -> List[LLMUsage]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.model_api.get_usage_stats_by_model(
                    interval=interval, _headers=header
                )
            )
        return [LLMUsage(**d.to_dict()) for d in response]

    async def get_llm_usage_by_user(self, interval: str) -> List[UserWithLLMUsage]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.model_api.get_usage_stats_by_user(
                    interval=interval, _headers=header
                )
            )
        return [UserWithLLMUsage(**d.to_dict()) for d in response]

    async def get_llm_usage_by_llm_and_user(
        self, interval: str
    ) -> List[LLMWithUserUsage]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.model_api.get_usage_stats_by_model_and_user(
                    interval=interval, _headers=header
                )
            )
        return [LLMWithUserUsage(**d.to_dict()) for d in response]

    async def get_llm_performance_by_llm(self, interval: str) -> List[LLMPerformance]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.model_api.get_performance_stats_by_model(
                    interval=interval, _headers=header
                )
            )
        return [LLMPerformance(**d.to_dict()) for d in response]

    async def get_scheduler_stats(self) -> SchedulerStats:
        """Count the number of global, pending jobs on the server.

        Returns:
            SchedulerStats: The queue length for number of jobs.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            rest_stats = await _rest_to_client_exceptions(
                rest_client.job_api.count_pending_jobs(_headers=header)
            )
        stats_dict = rest_stats.to_dict()
        stats_dict["queue_length"] = stats_dict["count"]
        return SchedulerStats(**stats_dict)

    async def ingest_from_file_system(
        self,
        collection_id: str,
        root_dir: str,
        glob: str,
        gen_doc_summaries: Union[bool, None] = None,
        gen_doc_questions: Union[bool, None] = None,
        audio_input_language: Union[str, None] = None,
        ocr_model: Union[str, None] = None,
        tesseract_lang: Union[str, None] = None,
        keep_tables_as_one_chunk: Union[bool, None] = None,
        chunk_by_page: Union[bool, None] = None,
        handwriting_check: Union[bool, None] = None,
        timeout: Union[float, None] = None,
        ingest_mode: Union[str, None] = None,
    ) -> Job:
        """Add files from the local system into a collection.

        Args:
            collection_id:
                String id of the collection to add the ingested documents into.
            root_dir:
                String path of where to look for files.
            glob:
                String of the glob pattern used to match files in the root directory.
            gen_doc_summaries:
                Whether to auto-generate document summaries (uses LLM)
            gen_doc_questions:
                Whether to auto-generate sample questions for each document (uses LLM)
            audio_input_language:
                Language of audio files. Defaults to "auto" language detection. Pass empty string to see choices.
            ocr_model:
                Which method to use to extract text from images using AI-enabled optical character recognition (OCR) models.
                Pass empty string to see choices.
                docTR is best for Latin text, PaddleOCR is best for certain non-Latin languages, Tesseract covers a wide range of languages.
                Mississippi works well on handwriting.
                "auto" - Automatic will auto-select the best OCR model for every page.
                "off" - Disable OCR for speed, but all images will then be skipped (also no image captions will be made).
            tesseract_lang:
                Which language to use when using ocr_model="tesseract". Pass empty string to see choices.
            keep_tables_as_one_chunk:
                When tables are identified by the table parser the table tokens will be kept in a single chunk.
            chunk_by_page:
                Each page will be a chunk. `keep_tables_as_one_chunk` will be ignored if this is True.
            handwriting_check:
                Check pages for handwriting. Will use specialized models if handwriting is found.
            timeout:
                Timeout in seconds.
            ingest_mode:
                Ingest mode to use.
                "standard" - Files will be ingested for use with RAG
                "lite" - Files will be ingested for use with RAG, but minimal processing will be done, favoring ingest speed over accuracy
                "agent_only" - Bypasses standard ingestion. Files can only be used with agents.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.ingestion_api.create_ingest_from_file_system_job(
                    collection_id=collection_id,
                    ingest_from_file_system_body=rest.IngestFromFileSystemBody(
                        root_dir=root_dir, glob=glob
                    ),
                    gen_doc_summaries=gen_doc_summaries,
                    gen_doc_questions=gen_doc_questions,
                    audio_input_language=audio_input_language,
                    ocr_model=ocr_model,
                    tesseract_lang=tesseract_lang,
                    keep_tables_as_one_chunk=keep_tables_as_one_chunk,
                    chunk_by_page=chunk_by_page,
                    handwriting_check=handwriting_check,
                    ingest_mode=ingest_mode,
                    timeout=timeout,
                    _headers=header,
                )
            )
        return await self._wait_for_completion(response.id, timeout=timeout)

    async def ingest_from_plain_text(
        self,
        collection_id: str,
        plain_text: str,
        file_name: str,
        gen_doc_summaries: Union[bool, None] = None,
        gen_doc_questions: Union[bool, None] = None,
        metadata: Union[Dict[str, Any], None] = None,
        timeout: Union[float, None] = None,
    ):
        """Add plain text to a collection.

        Args:
            collection_id:
                String id of the collection to add the ingested documents into.
            plain_text:
                String of the plain text to ingest.
            file_name:
                String of the file name to use for the document.
            gen_doc_summaries:
                Whether to auto-generate document summaries (uses LLM)
            gen_doc_questions:
                Whether to auto-generate sample questions for each document (uses LLM)
            metadata:
                Dictionary of metadata to add to the document.
            timeout:
                Timeout in seconds
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.ingestion_api.create_ingest_from_plain_text_job(
                    collection_id=collection_id,
                    body=plain_text,
                    file_name=file_name,
                    gen_doc_summaries=gen_doc_summaries,
                    gen_doc_questions=gen_doc_questions,
                    timeout=timeout,
                    metadata=None if metadata is None else json.dumps(metadata),
                    _headers=header,
                )
            )
        return await self._wait_for_completion(response.id, timeout=timeout)

    async def ingest_from_s3(
        self,
        collection_id: str,
        url: Union[str, List[str]],
        region: str = "us-east-1",
        credentials: Union[S3Credential, None] = None,
        gen_doc_summaries: Union[bool, None] = None,
        gen_doc_questions: Union[bool, None] = None,
        audio_input_language: Union[str, None] = None,
        ocr_model: Union[str, None] = None,
        tesseract_lang: Union[str, None] = None,
        keep_tables_as_one_chunk: Union[bool, None] = None,
        chunk_by_page: Union[bool, None] = None,
        handwriting_check: Union[bool, None] = None,
        metadata: Union[Dict[str, Any], None] = None,
        timeout: Union[float, None] = None,
        ingest_mode: Union[str, None] = None,
    ):
        """Add files from the AWS S3 storage into a collection.

        Args:
            collection_id:
                String id of the collection to add the ingested documents into.
            url:
                The path or list of paths of S3 files or directories. Examples: s3://bucket/file, s3://bucket/../dir/
            region:
                The name of the region used for interaction with AWS services.
            credentials:
                The object with S3 credentials. If the object is not provided, only public buckets will be accessible.
            gen_doc_summaries:
                Whether to auto-generate document summaries (uses LLM)
            gen_doc_questions:
                Whether to auto-generate sample questions for each document (uses LLM)
            audio_input_language:
                Language of audio files. Defaults to "auto" language detection. Pass empty string to see choices.
            ocr_model:
                Which method to use to extract text from images using AI-enabled optical character recognition (OCR) models.
                Pass empty string to see choices.
                docTR is best for Latin text, PaddleOCR is best for certain non-Latin languages, Tesseract covers a wide range of languages.
                Mississippi works well on handwriting.
                "auto" - Automatic will auto-select the best OCR model for every page.
                "off" - Disable OCR for speed, but all images will then be skipped (also no image captions will be made).
            tesseract_lang:
                Which language to use when using ocr_model="tesseract". Pass empty string to see choices.
            keep_tables_as_one_chunk:
                When tables are identified by the table parser the table tokens will be kept in a single chunk.
            chunk_by_page:
                Each page will be a chunk. `keep_tables_as_one_chunk` will be ignored if this is True.
            handwriting_check:
                Check pages for handwriting. Will use specialized models if handwriting is found.
            metadata:
                Dictionary of metadata to add to the document.
            timeout:
                Timeout in seconds.
            ingest_mode:
                Ingest mode to use.
                "standard" - Files will be ingested for use with RAG
                "lite" - Files will be ingested for use with RAG, but minimal processing will be done, favoring ingest speed over accuracy
                "agent_only" - Bypasses standard ingestion. Files can only be used with agents.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.ingestion_api.create_ingest_from_s3_job(
                    collection_id=collection_id,
                    ingest_from_s3_body=rest.IngestFromS3Body(
                        urls=[url] if isinstance(url, str) else url,
                        region=region,
                        credentials=None
                        if credentials is None
                        else rest.S3Credentials(**credentials.__dict__),
                        metadata=metadata,
                    ),
                    gen_doc_summaries=gen_doc_summaries,
                    gen_doc_questions=gen_doc_questions,
                    audio_input_language=audio_input_language,
                    ocr_model=ocr_model,
                    tesseract_lang=tesseract_lang,
                    keep_tables_as_one_chunk=keep_tables_as_one_chunk,
                    chunk_by_page=chunk_by_page,
                    handwriting_check=handwriting_check,
                    ingest_mode=ingest_mode,
                    timeout=timeout,
                    _headers=header,
                )
            )
        return await self._wait_for_completion(response.id, timeout=timeout)

    async def ingest_from_gcs(
        self,
        collection_id: str,
        url: Union[str, List[str]],
        credentials: Union[GCSServiceAccountCredential, None] = None,
        gen_doc_summaries: Union[bool, None] = None,
        gen_doc_questions: Union[bool, None] = None,
        audio_input_language: Union[str, None] = None,
        ocr_model: Union[str, None] = None,
        tesseract_lang: Union[str, None] = None,
        keep_tables_as_one_chunk: Union[bool, None] = None,
        chunk_by_page: Union[bool, None] = None,
        handwriting_check: Union[bool, None] = None,
        metadata: Union[Dict[str, Any], None] = None,
        timeout: Union[float, None] = None,
        ingest_mode: Union[str, None] = None,
    ):
        """Add files from the Google Cloud Storage into a collection.

        Args:
            collection_id:
                String id of the collection to add the ingested documents into.
            url:
                The path or list of paths of GCS files or directories. Examples: gs://bucket/file, gs://bucket/../dir/
            credentials:
                The object holding a path to a JSON key of Google Cloud service account. If the object is not provided,
                only public buckets will be accessible.
            gen_doc_summaries:
                Whether to auto-generate document summaries (uses LLM)
            gen_doc_questions:
                Whether to auto-generate sample questions for each document (uses LLM)
            audio_input_language:
                Language of audio files. Defaults to "auto" language detection. Pass empty string to see choices.
            ocr_model:
                Which method to use to extract text from images using AI-enabled optical character recognition (OCR) models.
                Pass empty string to see choices.
                docTR is best for Latin text, PaddleOCR is best for certain non-Latin languages, Tesseract covers a wide range of languages.
                Mississippi works well on handwriting.
                "auto" - Automatic will auto-select the best OCR model for every page.
                "off" - Disable OCR for speed, but all images will then be skipped (also no image captions will be made).
            tesseract_lang:
                Which language to use when using ocr_model="tesseract". Pass empty string to see choices.
            keep_tables_as_one_chunk:
                When tables are identified by the table parser the table tokens will be kept in a single chunk.
            chunk_by_page:
                Each page will be a chunk. `keep_tables_as_one_chunk` will be ignored if this is True.
            handwriting_check:
                Check pages for handwriting. Will use specialized models if handwriting is found.
            metadata:
                Dictionary of metadata to add to the document.
            timeout:
                Timeout in seconds.
            ingest_mode:
                Ingest mode to use.
                "standard" - Files will be ingested for use with RAG
                "lite" - Files will be ingested for use with RAG, but minimal processing will be done, favoring ingest speed over accuracy
                "agent_only" - Bypasses standard ingestion. Files can only be used with agents.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.ingestion_api.create_ingest_from_gcs_job(
                    collection_id=collection_id,
                    ingest_from_gcs_body=rest.IngestFromGcsBody(
                        urls=[url] if isinstance(url, str) else url,
                        credentials=None
                        if credentials is None
                        else rest.GCSCredentials(
                            service_account_json_key=credentials.load_key_as_string()
                        ),
                        metadata=metadata,
                    ),
                    gen_doc_summaries=gen_doc_summaries,
                    gen_doc_questions=gen_doc_questions,
                    audio_input_language=audio_input_language,
                    ocr_model=ocr_model,
                    tesseract_lang=tesseract_lang,
                    keep_tables_as_one_chunk=keep_tables_as_one_chunk,
                    chunk_by_page=chunk_by_page,
                    handwriting_check=handwriting_check,
                    ingest_mode=ingest_mode,
                    timeout=timeout,
                    _headers=header,
                )
            )
        return await self._wait_for_completion(response.id, timeout=timeout)

    async def ingest_from_azure_blob_storage(
        self,
        collection_id: str,
        container: str,
        path: Union[str, List[str]],
        account_name: str,
        credentials: Union[AzureKeyCredential, AzureSASCredential, None] = None,
        gen_doc_summaries: Union[bool, None] = None,
        gen_doc_questions: Union[bool, None] = None,
        audio_input_language: Union[str, None] = None,
        ocr_model: Union[str, None] = None,
        tesseract_lang: Union[str, None] = None,
        keep_tables_as_one_chunk: Union[bool, None] = None,
        chunk_by_page: Union[bool, None] = None,
        handwriting_check: Union[bool, None] = None,
        metadata: Union[Dict[str, Any], None] = None,
        timeout: Union[float, None] = None,
        ingest_mode: Union[str, None] = None,
    ):
        """Add files from the Azure Blob Storage into a collection.

        Args:
            collection_id:
                String id of the collection to add the ingested documents into.
            container:
                Name of the Azure Blob Storage container.
            path:
                Path or list of paths to files or directories within an Azure Blob Storage container.
                Examples: file1, dir1/file2, dir3/dir4/
            account_name:
                Name of a storage account
            credentials:
                The object with Azure credentials. If the object is not provided,
                only a public container will be accessible.
            gen_doc_summaries:
                Whether to auto-generate document summaries (uses LLM)
            gen_doc_questions:
                Whether to auto-generate sample questions for each document (uses LLM)
            audio_input_language:
                Language of audio files. Defaults to "auto" language detection. Pass empty string to see choices.
            ocr_model:
                Which method to use to extract text from images using AI-enabled optical character recognition (OCR) models.
                Pass empty string to see choices.
                docTR is best for Latin text, PaddleOCR is best for certain non-Latin languages, Tesseract covers a wide range of languages.
                Mississippi works well on handwriting.
                "auto" - Automatic will auto-select the best OCR model for every page.
                "off" - Disable OCR for speed, but all images will then be skipped (also no image captions will be made).
            tesseract_lang:
                Which language to use when using ocr_model="tesseract". Pass empty string to see choices.
            keep_tables_as_one_chunk:
                When tables are identified by the table parser the table tokens will be kept in a single chunk.
            chunk_by_page:
                Each page will be a chunk. `keep_tables_as_one_chunk` will be ignored if this is True.
            handwriting_check:
                Check pages for handwriting. Will use specialized models if handwriting is found.
            metadata:
                Metadata to be associated with the document.
            timeout:
                Timeout in seconds.
            ingest_mode:
                Ingest mode to use.
                "standard" - Files will be ingested for use with RAG
                "lite" - Files will be ingested for use with RAG, but minimal processing will be done, favoring ingest speed over accuracy
                "agent_only" - Bypasses standard ingestion. Files can only be used with agents.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.ingestion_api.create_ingest_from_azure_blob_storage_job(
                    collection_id=collection_id,
                    ingest_from_azure_blob_storage_body=rest.IngestFromAzureBlobStorageBody(
                        container=container,
                        paths=[path] if isinstance(path, str) else path,
                        account_name=account_name,
                        credentials=None
                        if credentials is None
                        else rest.AzureCredentials(**credentials.__dict__),
                        metadata=metadata,
                    ),
                    gen_doc_summaries=gen_doc_summaries,
                    gen_doc_questions=gen_doc_questions,
                    audio_input_language=audio_input_language,
                    ocr_model=ocr_model,
                    tesseract_lang=tesseract_lang,
                    keep_tables_as_one_chunk=keep_tables_as_one_chunk,
                    chunk_by_page=chunk_by_page,
                    handwriting_check=handwriting_check,
                    ingest_mode=ingest_mode,
                    timeout=timeout,
                    _headers=header,
                )
            )
        return await self._wait_for_completion(response.id, timeout=timeout)

    async def list_secret_ids(self, connector_type: Optional[str] = None) -> List[str]:
        """
        List available secret IDs from the SecureStore for cloud storage connectors.

        Args:
            connector_type: Type of connector ('s3', 'gcs', 'azure_key', 'azure_sas')
                           If None, returns secrets for all connector types.

        Returns:
            List of secret IDs available for the specified connector type
        """
        await self._init_rest()
        header = await self._get_auth_header()
        response = await _rest_to_client_exceptions(
            self._secrets_api.list_secret_ids(
                connector_type=connector_type, _headers=header
            )
        )
        return response.ids

    async def get_secret(self, secret_id: str) -> Union[Dict[str, Any], None]:
        """Get a secret from the SecureStore by its ID.

        Args:
            secret_id: The ID of the secret to retrieve.

        Returns:
            The secret object corresponding to the provided ID.
        """
        await self._init_rest()
        header = await self._get_auth_header()
        response = await _rest_to_client_exceptions(
            self._secrets_api.get_secret(secret_id=secret_id, _headers=header)
        )
        return response.to_dict()

    async def get_secret_value(self, secret_id: str) -> Union[str, None]:
        """Get the value of a secret from the SecureStore by its ID.

        Args:
            secret_id: The ID of the secret to retrieve.

        Returns:
            The value of the secret corresponding to the provided ID.
        """
        await self._init_rest()
        header = await self._get_auth_header()
        response = await _rest_to_client_exceptions(
            self._secrets_api.get_secret_value(secret_id=secret_id, _headers=header)
        )
        return response.value if response else None

    async def create_secret(self, secret: Dict[str, Any]) -> None:
        """Create a new secret in the SecureStore.

        Args:
            secret: A dictionary containing the secret data to be stored.

        Returns:
            The ID of the newly created secret.
        """
        await self._init_rest()
        header = await self._get_auth_header()
        response = await _rest_to_client_exceptions(
            self._secrets_api.create_secret(secret=secret, _headers=header)
        )
        return response.id

    async def update_secret(self, secret_id: str, secret: Dict[str, Any]) -> None:
        """Update an existing secret in the SecureStore.

        Args:
            secret_id: The ID of the secret to update.
            secret: A dictionary containing the updated secret data.

        Returns:
            None
        """
        await self._init_rest()
        header = await self._get_auth_header()
        await _rest_to_client_exceptions(
            self._secrets_api.update_secret(
                secret_id=secret_id, secret=secret, _headers=header
            )
        )

    async def delete_secret(self, secret_id: str) -> None:
        """Delete a secret from the SecureStore by its ID.

        Args:
            secret_id: The ID of the secret to delete.

        Returns:
            None
        """
        await self._init_rest()
        header = await self._get_auth_header()
        await _rest_to_client_exceptions(
            self._secrets_api.delete_secret(secret_id=secret_id, _headers=header)
        )

    async def ingest_uploads(
        self,
        collection_id: str,
        upload_ids: Iterable[str],
        gen_doc_summaries: Union[bool, None] = None,
        gen_doc_questions: Union[bool, None] = None,
        audio_input_language: Union[str, None] = None,
        ocr_model: Union[str, None] = None,
        restricted: bool = False,
        permissions: Union[List[SharePermission], None] = None,
        tesseract_lang: Union[str, None] = None,
        keep_tables_as_one_chunk: Union[bool, None] = None,
        chunk_by_page: Union[bool, None] = None,
        handwriting_check: Union[bool, None] = None,
        metadata: Union[Dict[str, Any], None] = None,
        timeout: Union[float, None] = None,
        ingest_mode: Union[str, None] = None,
    ) -> Job:
        """Add uploaded documents into a specific collection.

        See Also:
            upload: Upload the files into the system to then be ingested into a collection.
            delete_upload: Delete uploaded file

        Args:
            collection_id:
                String id of the collection to add the ingested documents into.
            upload_ids:
                List of string ids of each uploaded document to add to the collection.
            gen_doc_summaries:
                Whether to auto-generate document summaries (uses LLM)
            gen_doc_questions:
                Whether to auto-generate sample questions for each document (uses LLM)
            audio_input_language:
                Language of audio files. Defaults to "auto" language detection. Pass empty string to see choices.
            ocr_model:
                Which method to use to extract text from images using AI-enabled optical character recognition (OCR) models.
                Pass empty string to see choices.
                docTR is best for Latin text, PaddleOCR is best for certain non-Latin languages, Tesseract covers a wide range of languages.
                Mississippi works well on handwriting.
                "auto" - Automatic will auto-select the best OCR model for every page.
                "off" - Disable OCR for speed, but all images will then be skipped (also no image captions will be made).
            restricted:
                Whether the document should be restricted only to certain users.
            permissions:
                List of permissions. Each permission is a SharePermission object.
            tesseract_lang:
                Which language to use when using ocr_model="tesseract". Pass empty string to see choices.
            keep_tables_as_one_chunk:
                When tables are identified by the table parser the table tokens will be kept in a single chunk.
            chunk_by_page:
                Each page will be a chunk. `keep_tables_as_one_chunk` will be ignored if this is True.
            handwriting_check:
                Check pages for handwriting. Will use specialized models if handwriting is found.
            metadata:
                Metadata to be associated with the document.
            timeout:
                Timeout in seconds.
            ingest_mode:
                Ingest mode to use.
                "standard" - Files will be ingested for use with RAG
                "lite" - Files will be ingested for use with RAG, but minimal processing will be done, favoring ingest speed over accuracy
                "agent_only" - Bypasses standard ingestion. Files can only be used with agents.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.ingestion_api.create_ingest_upload_job(
                    collection_id=collection_id,
                    ingest_upload_body=rest.IngestUploadBody(metadata=metadata),
                    upload_ids=upload_ids,
                    gen_doc_summaries=gen_doc_summaries,
                    gen_doc_questions=gen_doc_questions,
                    audio_input_language=audio_input_language,
                    ocr_model=ocr_model,
                    tesseract_lang=tesseract_lang,
                    keep_tables_as_one_chunk=keep_tables_as_one_chunk,
                    chunk_by_page=chunk_by_page,
                    handwriting_check=handwriting_check,
                    ingest_mode=ingest_mode,
                    timeout=timeout,
                    restricted=restricted,
                    permissions=(
                        [permission.username for permission in permissions]
                        if permissions
                        else None
                    ),
                    _headers=header,
                )
            )
        return await self._wait_for_completion(response.id, timeout=timeout)

    async def ingest_website(
        self,
        collection_id: str,
        url: str,
        gen_doc_summaries: Union[bool, None] = None,
        gen_doc_questions: Union[bool, None] = None,
        follow_links: Union[bool, None] = None,
        max_depth: Union[int, None] = None,
        max_documents: Union[int, None] = None,
        audio_input_language: Union[str, None] = None,
        ocr_model: Union[str, None] = None,
        tesseract_lang: Union[str, None] = None,
        keep_tables_as_one_chunk: Union[bool, None] = None,
        chunk_by_page: Union[bool, None] = None,
        handwriting_check: Union[bool, None] = None,
        timeout: Union[float, None] = None,
        ingest_mode: Union[str, None] = None,
    ) -> Job:
        """Crawl and ingest a URL into a collection.

        The web page or document linked from this URL will be imported.

        Args:
            collection_id:
                String id of the collection to add the ingested documents into.
            url:
                String of the url to crawl.
            gen_doc_summaries:
                Whether to auto-generate document summaries (uses LLM)
            gen_doc_questions:
                Whether to auto-generate sample questions for each document (uses LLM)
            follow_links:
                Whether to import all web pages linked from this URL will be imported.
                External links will be ignored. Links to other pages on the same domain will
                be followed as long as they are at the same level or below the URL you specify.
                Each page will be transformed into a PDF document.
            max_depth:
                Max depth of recursion when following links, only when follow_links is True.
                Max_depth of 0 means don't follow any links, max_depth of 1 means follow only top-level links, etc.
                Use -1 for automatic (system settings).
            max_documents:
                Max number of documents when following links, only when follow_links is True.
                Use None for automatic (system defaults).
                Use -1 for max (system limit).
            audio_input_language:
                Language of audio files. Defaults to "auto" language detection. Pass empty string to see choices.
            ocr_model:
                Which method to use to extract text from images using AI-enabled optical character recognition (OCR) models.
                Pass empty string to see choices.
                docTR is best for Latin text, PaddleOCR is best for certain non-Latin languages, Tesseract covers a wide range of languages.
                Mississippi works well on handwriting.
                "auto" - Automatic will auto-select the best OCR model for every page.
                "off" - Disable OCR for speed, but all images will then be skipped (also no image captions will be made).
            tesseract_lang:
                Which language to use when using ocr_model="tesseract". Pass empty string to see choices.
            keep_tables_as_one_chunk:
                When tables are identified by the table parser the table tokens will be kept in a single chunk.
            chunk_by_page:
                Each page will be a chunk. `keep_tables_as_one_chunk` will be ignored if this is True.
            handwriting_check:
                Check pages for handwriting. Will use specialized models if handwriting is found.
            timeout:
                Timeout in seconds.
            ingest_mode:
                Ingest mode to use.
                "standard" - Files will be ingested for use with RAG
                "lite" - Files will be ingested for use with RAG, but minimal processing will be done, favoring ingest speed over accuracy
                "agent_only" - Bypasses standard ingestion. Files can only be used with agents.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.ingestion_api.create_ingest_from_website_job(
                    collection_id=collection_id,
                    ingest_from_website_body=rest.IngestFromWebsiteBody(url=url),
                    gen_doc_summaries=gen_doc_summaries,
                    gen_doc_questions=gen_doc_questions,
                    follow_links=follow_links,
                    max_depth=max_depth,
                    max_documents=max_documents,
                    audio_input_language=audio_input_language,
                    ocr_model=ocr_model,
                    tesseract_lang=tesseract_lang,
                    keep_tables_as_one_chunk=keep_tables_as_one_chunk,
                    chunk_by_page=chunk_by_page,
                    handwriting_check=handwriting_check,
                    ingest_mode=ingest_mode,
                    timeout=timeout,
                    _headers=header,
                )
            )
        return await self._wait_for_completion(response.id, timeout=timeout)

    async def ingest_agent_only_to_standard(
        self,
        collection_id: str,
        document_id: str,
        gen_doc_summaries: Union[bool, None] = None,
        gen_doc_questions: Union[bool, None] = None,
        audio_input_language: Union[str, None] = None,
        ocr_model: Union[str, None] = None,
        restricted: bool = False,
        permissions: Union[List[SharePermission], None] = None,
        tesseract_lang: Union[str, None] = None,
        keep_tables_as_one_chunk: Union[bool, None] = None,
        chunk_by_page: Union[bool, None] = None,
        handwriting_check: Union[bool, None] = None,
        timeout: Union[float, None] = None,
    ):
        """For files uploaded in "agent_only" ingest mode, convert to PDF and parse

        See Also:
            upload: Upload the files into the system to then be ingested into a collection.
            delete_upload: Delete uploaded file

        Args:
            collection_id:
                String id of the collection to add the ingested documents into.
            document_id:
                ID of document to be parsed.
            gen_doc_summaries:
                Whether to auto-generate document summaries (uses LLM)
            gen_doc_questions:
                Whether to auto-generate sample questions for each document (uses LLM)
            audio_input_language:
                Language of audio files. Defaults to "auto" language detection. Pass empty string to see choices.
            ocr_model:
                Which method to use to extract text from images using AI-enabled optical character recognition (OCR) models.
                Pass empty string to see choices.
                docTR is best for Latin text, PaddleOCR is best for certain non-Latin languages, Tesseract covers a wide range of languages.
                Mississippi works well on handwriting.
                "auto" - Automatic will auto-select the best OCR model for every page.
                "off" - Disable OCR for speed, but all images will then be skipped (also no image captions will be made).
            restricted:
                Whether the document should be restricted only to certain users.
            permissions:
                List of permissions. Each permission is a SharePermission object.
            tesseract_lang:
                Which language to use when using ocr_model="tesseract". Pass empty string to see choices.
            keep_tables_as_one_chunk:
                When tables are identified by the table parser the table tokens will be kept in a single chunk.
            chunk_by_page:
                Each page will be a chunk. `keep_tables_as_one_chunk` will be ignored if this is True.
            handwriting_check:
                Check pages for handwriting. Will use specialized models if handwriting is found.
            timeout:
                Timeout in seconds.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.ingestion_api.create_ingest_agent_only_to_standard_job(
                    collection_id=collection_id,
                    document_id=document_id,
                    gen_doc_summaries=gen_doc_summaries,
                    gen_doc_questions=gen_doc_questions,
                    audio_input_language=audio_input_language,
                    ocr_model=ocr_model,
                    tesseract_lang=tesseract_lang,
                    keep_tables_as_one_chunk=keep_tables_as_one_chunk,
                    chunk_by_page=chunk_by_page,
                    handwriting_check=handwriting_check,
                    restricted=restricted,
                    permissions=(
                        [permission.username for permission in permissions]
                        if permissions
                        else None
                    ),
                    timeout=timeout,
                    _headers=header,
                )
            )
        return await self._wait_for_completion(response.id, timeout=timeout)

    async def list_chat_messages(
        self, chat_session_id: str, offset: int, limit: int
    ) -> List[ChatMessage]:
        """Fetch chat message and metadata for messages in a chat session.

        Messages without a `reply_to` are from the end user, messages with a `reply_to`
        are from an LLM and a response to a specific user message.

        Args:
            chat_session_id:
                String id of the chat session to filter by.
            offset:
                How many chat messages to skip before returning.
            limit:
                How many chat messages to return.

        Returns:
            list of ChatMessage: Text and metadata for chat messages.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.chat_api.get_chat_session_messages(
                    session_id=chat_session_id,
                    offset=offset,
                    limit=limit,
                    _headers=header,
                )
            )

        data = [d.to_dict() for d in response]
        for d in data:
            value = d.get("type_list")
            if value == [None]:
                continue
            if value:
                d["type_list"] = [json.dumps(v) for v in value]

        return [ChatMessage(**d) for d in data]

    async def list_chat_message_references(
        self, message_id: str, limit: Optional[int] = None
    ) -> List[ChatMessageReference]:
        """Fetch metadata for references of a chat message.

        References are only available for messages sent from an LLM, an empty list will be returned
        for messages sent by the user.

        Args:
            message_id:
                String id of the message to get references for.
            limit:
                The number of references to consider based on the highest confidence scores.

        Returns:
            list of ChatMessageReference: Metadata including the document name, polygon information,
            and score.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.chat_api.get_message_references(
                    message_id=message_id, limit=limit, _headers=header
                )
            )
        return [ChatMessageReference(**d.to_dict()) for d in response]

    async def list_list_chat_message_meta(
        self, message_id: str
    ) -> List[ChatMessageMeta]:
        """Fetch chat message meta information.

        Args:
            message_id:
                Message id to which the metadata should be pulled.

        Returns:
            list of ChatMessageMeta: Metadata about the chat message.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.chat_api.get_message_meta(
                    message_id=message_id, _headers=header
                )
            )
        return [ChatMessageMeta(**d.to_dict()) for d in response]

    async def list_chat_message_meta_part(
        self, message_id: str, info_type: str
    ) -> ChatMessageMeta:
        """Fetch one chat message meta information.

        Args:
            message_id:
                Message id to which the metadata should be pulled.
            info_type:
                Metadata type to fetch.
                Valid choices are: "self_reflection", "usage_stats", "prompt_raw", "llm_only", "hyde1", "py_client_code"

        Returns:
            ChatMessageMeta: Metadata information about the chat message.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.chat_api.get_message_meta(
                    message_id=message_id, info_type=info_type, _headers=header
                )
            )

        if len(response) == 0:
            raise ObjectNotFoundError(
                {"error": f"Chat meta type not found for {info_type}"}
            )

        return ChatMessageMeta(**response[0].to_dict())

    async def list_chat_messages_full(
        self, chat_session_id: str, offset: int, limit: int
    ) -> List[ChatMessageFull]:
        """Fetch chat message and metadata for messages in a chat session.

        Messages without a `reply_to` are from the end user, messages with a `reply_to`
        are from an LLM and a response to a specific user message.

        Args:
            chat_session_id:
                String id of the chat session to filter by.
            offset:
                How many chat messages to skip before returning.
            limit:
                How many chat messages to return.

        Returns:
            list of ChatMessageFull: Text and metadata for chat messages.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.chat_api.get_chat_session_messages(
                    session_id=chat_session_id,
                    offset=offset,
                    limit=limit,
                    _headers=header,
                )
            )

        data = [d.to_dict() for d in response]
        for d in data:
            value = d.get("type_list")
            if value == [None]:
                continue
            if value:
                d["type_list"] = [ChatMessageMeta(**v) for v in value]

        return [ChatMessageFull(**d) for d in data]

    async def list_chat_sessions_for_collection(
        self, collection_id: str, offset: int, limit: int
    ) -> List[ChatSessionForCollection]:
        """Fetch chat session metadata for chat sessions in a collection.

        Args:
            collection_id:
                String id of the collection to filter by.
            offset:
                How many chat sessions to skip before returning.
            limit:
                How many chat sessions to return.

        Returns:
            list of ChatSessionForCollection: Metadata about each chat session including the
            latest message.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.list_chat_sessions_for_collection(
                    collection_id=collection_id,
                    offset=offset,
                    limit=limit,
                    _headers=header,
                )
            )
        return [ChatSessionForCollection(**d.to_dict()) for d in response]

    async def list_chat_sessions_for_document(
        self, document_id: str, offset: int, limit: int
    ) -> List[ChatSessionForDocument]:
        """Fetch chat session metadata for chat session that produced a specific document (typically through agents).

        Args:
            document_id:
                String id of the document to filter by.
            offset:
                How many chat sessions to skip before returning.
            limit:
                How many chat sessions to return.

        Returns:
            list of ChatSessionForDocument: Metadata about each chat session including the
            latest message.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.document_api.list_chat_sessions_for_document(
                    document_id=document_id, offset=offset, limit=limit, _headers=header
                )
            )
        return [ChatSessionForDocument(**d.to_dict()) for d in response]

    async def rename_chat_session(self, chat_session_id: str, name: str):
        """Update a chat session name

        Args:
            chat_session_id:
                String id of the document to search for.
            name:
                The new chat session name.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.chat_api.update_chat_session(
                    session_id=chat_session_id,
                    chat_session_update_request=rest.ChatSessionUpdateRequest(
                        name=name
                    ),
                    _headers=header,
                )
            )

    async def list_collections_for_document(
        self, document_id: str, offset: int, limit: int
    ) -> List[CollectionInfo]:
        """Fetch metadata about each collection the document is a part of.

        At this time, each document will only be available in a single collection.

        Args:
            document_id:
                String id of the document to search for.
            offset:
                How many collections to skip before returning.
            limit:
                How many collections to return.

        Returns:
            list of CollectionInfo: Metadata about each collection.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.document_api.list_collections_for_document(
                    document_id=document_id, offset=offset, limit=limit, _headers=header
                )
            )
        return [CollectionInfo(**d.to_dict()) for d in response]

    async def get_default_collection(self) -> CollectionInfo:
        """Get the default collection, to be used for collection API-keys.

        Returns:
            CollectionInfo: Default collection info.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            rest_collection = await _rest_to_client_exceptions(
                rest_client.collection_api.get_collection(
                    collection_id="default", _headers=header
                )
            )
            collection = CollectionInfo(**rest_collection.to_dict())
            metadata = await _rest_to_client_exceptions(
                rest_client.collection_api.get_collection_metadata(
                    collection_id=rest_collection.id, _headers=header
                )
            )
            if metadata != {}:
                collection.metadata_dict = metadata

        return collection

    async def list_documents_in_collection(
        self, collection_id: str, offset: int, limit: int, metadata_filter: dict = {}
    ) -> List[DocumentInfo]:
        """Fetch document metadata for documents in a collection.

        Args:
            collection_id:
                String id of the collection to filter by.
            offset:
                How many documents to skip before returning.
            limit:
                How many documents to return.
            metadata_filter:
                Metadata filter to apply to the documents.

        Returns:
            list of DocumentInfo: Metadata about each document.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            metadata_filter_json = None
            if metadata_filter and len(metadata_filter) > 0:
                metadata_filter_json = json.dumps(metadata_filter)
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.list_documents_for_collection(
                    collection_id=collection_id,
                    offset=offset,
                    limit=limit,
                    metadata_filter=metadata_filter_json,
                    _headers=header,
                )
            )

        dicts = [document.to_dict() for document in response]
        for d in dicts:
            unmarshal_dict(d)

        return [DocumentInfo(**d) for d in dicts]

    async def list_jobs(self) -> List[Job]:
        """List the user's jobs.

        Returns:
            list of Job:
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.job_api.list_jobs(_headers=header)
            )

        return [_convert_rest_job(d) for d in response if d.kind in JobKind.__members__]

    async def list_all_jobs(self) -> List[UserJobs]:
        """List all jobs (to be used by admins only).

        Returns:
            list of UserJobs
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.job_api.list_user_jobs(_headers=header)
            )

        def _convert_rest_user_job(user_jobs: rest.UserJobDetails) -> UserJobs:
            jobs = [_convert_rest_job(d) for d in user_jobs.jobs]
            return UserJobs(
                username=user_jobs.username,
                user_id=user_jobs.user_id,
                jobs=jobs,
            )

        return [_convert_rest_user_job(d) for d in response]

    async def list_recent_chat_sessions(
        self, offset: int, limit: int
    ) -> List[ChatSessionInfo]:
        """Fetch user's chat session metadata sorted by last update time.

        Chats across all collections will be accessed.

        Args:
            offset:
                How many chat sessions to skip before returning.
            limit:
                How many chat sessions to return.

        Returns:
            list of ChatSessionInfo: Metadata about each chat session including the
            latest message.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.chat_api.list_chat_sessions(
                    offset=offset, limit=limit, _headers=header
                )
            )
        return [ChatSessionInfo(**d.to_dict()) for d in response]

    async def list_question_reply_feedback_data(
        self, offset: int, limit: int
    ) -> List[QuestionReplyData]:
        """Fetch user's questions and answers that have a feedback.

        Questions and answers with metadata and feedback information.

        Args:
            offset:
                How many conversations to skip before returning.
            limit:
                How many conversations to return.

        Returns:
            list of QuestionReplyData: Metadata about questions and answers.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.chat_api.list_question_answer_feedbacks(
                    offset=offset, limit=limit, _headers=header
                )
            )
        return [QuestionReplyData(**d.to_dict()) for d in response]

    async def update_question_reply_feedback(
        self, reply_id: str, expected_answer: str, user_comment: str
    ):
        """Update feedback for a specific answer to a question.

        Args:
            reply_id:
                UUID of the reply.
            expected_answer:
                Expected answer.
            user_comment:
                User comment.

        Returns:
            None
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.chat_api.update_question_answer_feedback(
                    answer_id=reply_id,
                    update_qa_feedback_request=rest.UpdateQAFeedbackRequest(
                        expected_answer=expected_answer,
                        user_comment=user_comment,
                    ),
                    _headers=header,
                )
            )

    async def count_question_reply_feedback(self) -> int:
        """Fetch user's questions and answers with feedback count.

        Returns:
            int: the count of questions and replies that have a user feedback.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.chat_api.get_question_answer_feedback_count(_headers=header)
            )
        return response.count

    async def list_recent_collections(
        self, offset: int, limit: int
    ) -> List[CollectionInfo]:
        """Fetch user's collection metadata sorted by last update time.

        Args:
            offset:
                How many collections to skip before returning.
            limit:
                How many collections to return.

        Returns:
            list of CollectionInfo: Metadata about each collection.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.list_collections(
                    offset=offset, limit=limit, _headers=header
                )
            )
        return [CollectionInfo(**collection.to_dict()) for collection in response]

    async def list_recent_collections_sort(
        self, offset: int, limit: int, sort_column: str, ascending: bool
    ) -> List[CollectionInfo]:
        """Fetch user's collection metadata sorted by last update time.

        Args:
            offset:
                How many collections to skip before returning.
            limit:
                How many collections to return.
            sort_column:
                Sort column.
            ascending:
                When True, return sorted by sort_column in ascending order.

        Returns:
            list of CollectionInfo: Metadata about each collection.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.list_collections(
                    offset=offset,
                    limit=limit,
                    sort_column=sort_column,
                    ascending=ascending,
                    _headers=header,
                )
            )
        return [CollectionInfo(**collection.to_dict()) for collection in response]

    async def list_recent_collections_filter(
        self,
        offset: int,
        limit: int,
        current_user_only: bool = False,
        name_filter: str = "",
    ) -> List[CollectionInfo]:
        """Fetch user's collection metadata sorted by last update time with filter options.

        Args:
            offset:
                How many collections to skip before returning.
            limit:
                How many collections to return.
            current_user_only:
                When true, will only return the user owned collections.
            name_filter:
                Only returns collections with names matching this filter.

        Returns:
            list of CollectionInfo: Metadata about each collection.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.list_collections(
                    offset=offset,
                    limit=limit,
                    name_filter=name_filter,
                    current_user_only=current_user_only,
                    _headers=header,
                )
            )
        return [CollectionInfo(**d.to_dict()) for d in response]

    async def list_recent_collections_metadata_filter(
        self, offset: int, limit: int, current_user_only: bool, metadata_filter: dict
    ) -> List[CollectionInfo]:
        """Fetch user's collection metadata sorted by last update time with a filter on metadata.

        Args:
            offset:
                How many collections to skip before returning.
            limit:
                How many collections to return.
            current_user_only:
                When true, will only return the user owned collections.
            metadata_filter:
                Only returns collections with metadata matching this filter.

        Returns:
            list of CollectionInfo: Metadata about each collection.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.list_collections(
                    offset=offset,
                    limit=limit,
                    metadata_filter=json.dumps(metadata_filter),
                    current_user_only=current_user_only,
                    _headers=header,
                )
            )
        return [CollectionInfo(**d.to_dict()) for d in response]

    async def list_all_collections_sort(
        self, offset: int, limit: int, sort_column: str, ascending: bool
    ) -> List[CollectionInfo]:
        """Fetch all users' collection metadata sorted by last update time.

        This is for admin use only and includes private, public, and shared collections in the result.

        Args:
            offset:
                How many collections to skip before returning.
            limit:
                How many collections to return.
            sort_column:
                Sort column.
            ascending:
                When True, return sorted by sort_column in ascending order.

        Returns:
            list of CollectionInfo: Metadata about each collection.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.list_all_collections(
                    offset=offset,
                    limit=limit,
                    sort_column=sort_column,
                    ascending=ascending,
                    _headers=header,
                )
            )
        return [CollectionInfo(**d.to_dict()) for d in response]

    async def list_collection_permissions(
        self, collection_id: str
    ) -> List[SharePermission]:
        """Returns a list of access permissions for a given collection.

        The returned list of permissions denotes who has access to
        the collection and their access level.

        Args:
            collection_id:
                ID of the collection to inspect.

        Returns:
            list of SharePermission: Sharing permissions list for the given collection.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.get_collection_permissions(
                    collection_id=collection_id,
                    _headers=header,
                )
            )
        return [SharePermission(**d.to_dict()) for d in response]

    async def list_collection_group_permissions(
        self, collection_id: str
    ) -> List[GroupSharePermission]:
        """Returns a list of group access permissions for a given collection.

        The returned list of group permissions denoting which groups have access to
        the collection and their access level.

        Args:
            collection_id:
                ID of the collection to inspect.

        Returns:
            list of GroupSharePermission: Group sharing permissions list for the given collection.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.get_collection_group_permissions(
                    collection_id=collection_id,
                    _headers=header,
                )
            )
        return [GroupSharePermission(**d.to_dict()) for d in response]

    async def list_users(self, offset: int, limit: int) -> List[User]:
        """List system users.

        Returns a list of all registered users fo the system, a registered user,
        is a users that has logged in at least once.

        Args:
            offset:
                How many users to skip before returning.
            limit:
                How many users to return.

        Returns:
            list of User: Metadata about each user.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.permission_api.list_users(
                    offset=offset,
                    limit=limit,
                    _headers=header,
                )
            )
        return [User(**d.to_dict()) for d in response]

    async def request_current_user_deletion(
        self,
    ) -> str:
        """Request deletion of the current user account.

        This creates a deletion request and returns a delete ID that must be used
        to confirm the deletion within 5 minutes.

        Returns:
            str: Delete ID that must be used to confirm deletion.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.permission_api.request_current_user_deletion(
                    _headers=header,
                )
            )
        return response.delete_id

    async def confirm_current_user_deletion(
        self,
        delete_id: str,
        timeout: Union[float, None] = None,
    ) -> None:
        """Confirm deletion of the current user data.

        Args:
            delete_id:
                The delete ID returned from request_current_user_deletion().
            timeout:
                Timeout in seconds. Default is 300 seconds.
        """
        header = await self._get_auth_header()
        if timeout is None:
            timeout = 300.0

        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.permission_api.confirm_current_user_deletion(
                    confirm_user_deletion_request=rest.ConfirmUserDeletionRequest(
                        delete_id=delete_id,
                    ),
                    timeout=timeout,
                    _headers=header,
                )
            )

    async def share_collection(
        self, collection_id: str, permission: SharePermission
    ) -> ShareResponseStatus:
        """Share a collection to a user.

        The permission attribute defined the level of access,
        and who can access the collection, the collection_id attribute
        denotes the collection to be shared.

        Args:
            collection_id:
                ID of the collection to share.
            permission:
                Defines the rule for sharing, i.e. permission level.

        Returns:
            ShareResponseStatus: Status of share request.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_share_permission_status(
                _rest_to_client_exceptions(
                    rest_client.collection_api.share_collection(
                        collection_id=collection_id,
                        username=permission.username,
                        share_collection_request=rest.ShareCollectionRequest(
                            permissions=permission.permissions
                        ),
                        _headers=header,
                    )
                )
            )
        return result

    async def unshare_collection(
        self, collection_id: str, permission: SharePermission
    ) -> ShareResponseStatus:
        """Remove sharing of a collection to a user.

        The permission attribute defined the level of access,
        and who can access the collection, the collection_id attribute
        denotes the collection to be shared.

        In case of un-sharing, the SharePermission's user is sufficient.

        Args:
            collection_id:
                ID of the collection to un-share.
            permission:
                Defines the user for which collection access is revoked.

        ShareResponseStatus: Status of share request.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_share_permission_status(
                _rest_to_client_exceptions(
                    rest_client.collection_api.unshare_collection(
                        collection_id=collection_id,
                        username=permission.username,
                        _headers=header,
                    )
                )
            )
        return result

    async def unshare_collection_for_all(
        self, collection_id: str
    ) -> ShareResponseStatus:
        """Remove sharing of a collection to all other users but the original owner.

        Args:
            collection_id:
                ID of the collection to un-share.

        ShareResponseStatus: Status of share request.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_share_permission_status(
                _rest_to_client_exceptions(
                    rest_client.collection_api.unshare_collection_for_all(
                        collection_id=collection_id,
                        _headers=header,
                    )
                )
            )
        return result

    async def make_collection_public(self, collection_id: str):
        """Make a collection public

        Once a collection is public, it will be accessible to all
        authenticated users of the system.

        Args:
            collection_id:
                ID of the collection to make public.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.collection_api.update_collection_privacy(
                    collection_id=collection_id,
                    update_collection_privacy_request=rest.UpdateCollectionPrivacyRequest(
                        is_public=True
                    ),
                    _headers=header,
                )
            )

    async def make_collection_private(self, collection_id: str):
        """Make a collection private

        Once a collection is private, other users will no longer
        be able to access chat history or documents related to
        the collection.

        Args:
            collection_id:
                ID of the collection to make private.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.collection_api.update_collection_privacy(
                    collection_id=collection_id,
                    update_collection_privacy_request=rest.UpdateCollectionPrivacyRequest(
                        is_public=False
                    ),
                    _headers=header,
                )
            )

    async def share_collection_with_group(
        self, collection_id: str, permission: GroupSharePermission
    ) -> ShareResponseStatus:
        """Share a collection to a group.

        The permission attribute defines the level of access,
        and which group can access the collection, the collection_id attribute
        denotes the collection to be shared.

        Args:
            collection_id:
                ID of the collection to share.
            permission:
                Defines the rule for sharing, i.e. permission level and group.

        Returns:
            ShareResponseStatus: Status of share request.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_share_permission_status(
                _rest_to_client_exceptions(
                    rest_client.collection_api.share_collection_with_group(
                        collection_id=collection_id,
                        group_id=permission.group_id,
                        share_collection_request=rest.ShareCollectionRequest(
                            permissions=permission.permissions
                        ),
                        _headers=header,
                    )
                )
            )
        return result

    async def unshare_collection_from_group(
        self, collection_id: str, permission: GroupSharePermission
    ) -> ShareResponseStatus:
        """Remove sharing of a collection from a group.

        The permission attribute defines which group to remove access from,
        the collection_id attribute denotes the collection to be unshared.
        In case of un-sharing, the GroupSharePermission's group_id is sufficient.

        Args:
            collection_id:
                ID of the collection to un-share.
            permission:
                Defines the group for which collection access is revoked.

        Returns:
            ShareResponseStatus: Status of share request.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_share_permission_status(
                _rest_to_client_exceptions(
                    rest_client.collection_api.unshare_collection_from_group(
                        collection_id=collection_id,
                        group_id=permission.group_id,
                        _headers=header,
                    )
                )
            )
        return result

    async def list_recent_documents(
        self, offset: int, limit: int, metadata_filter: dict = {}
    ) -> List[DocumentInfo]:
        """Fetch user's document metadata sorted by last update time.

        All documents owned by the user, regardless of collection, are accessed.

        Args:
            offset:
                How many documents to skip before returning.
            limit:
                How many documents to return.
            metadata_filter:
                Metadata filter to apply to the documents.

        Returns:
            list of DocumentInfo: Metadata about each document.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            metadata_filter_json = None
            if metadata_filter and len(metadata_filter) > 0:
                metadata_filter_json = json.dumps(metadata_filter)
            response = await _rest_to_client_exceptions(
                rest_client.document_api.list_documents(
                    offset=offset,
                    limit=limit,
                    metadata_filter=metadata_filter_json,
                    _headers=header,
                )
            )

        dicts = [document.to_dict() for document in response]
        for d in dicts:
            unmarshal_dict(d)

        return [DocumentInfo(**d) for d in dicts]

    async def list_recent_documents_with_summaries(
        self, offset: int, limit: int
    ) -> List[DocumentInfoSummary]:
        """Fetch user's document metadata sorted by last update time, including the latest document summary.

        All documents owned by the user, regardless of collection, are accessed.

        Args:
            offset:
                How many documents to skip before returning.
            limit:
                How many documents to return.

        Returns:
            list of DocumentInfoSummary: Metadata about each document.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.document_api.list_documents(
                    offset=offset, limit=limit, with_summaries=True, _headers=header
                )
            )

        dicts = [document.to_dict() for document in response]
        for d in dicts:
            unmarshal_dict(d)

        return [DocumentInfoSummary(**d) for d in dicts]

    async def list_recent_documents_with_summaries_sort(
        self, offset: int, limit: int, sort_column: str, ascending: bool
    ) -> List[DocumentInfoSummary]:
        """Fetch user's document metadata sorted by last update time, including the latest document summary.

        All documents owned by the user, regardless of collection, are accessed.

        Args:
            offset:
                How many documents to skip before returning.
            limit:
                How many documents to return.
            sort_column:
                Sort column.
            ascending:
                When True, return sorted by sort_column in ascending order.

        Returns:
            list of DocumentInfoSummary: Metadata about each document.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.document_api.list_documents(
                    offset=offset,
                    limit=limit,
                    with_summaries=True,
                    sort_column=sort_column,
                    ascending=ascending,
                    _headers=header,
                )
            )

        dicts = [document.to_dict() for document in response]
        for d in dicts:
            unmarshal_dict(d)

        return [DocumentInfoSummary(**d) for d in dicts]

    async def match_chunks(
        self,
        collection_id: str,
        vectors: List[List[float]],
        topics: List[str],
        offset: int,
        limit: int,
        cut_off: float = 0,
        width: int = 0,
    ) -> List[SearchResult]:
        """Find chunks related to a message using semantic search.

        Chunks are sorted by relevance and similarity score to the message.

        See Also: H2OGPTE.encode_for_retrieval to create vectors from messages.

        Args:
            collection_id:
                ID of the collection to search within.
            vectors:
                A list of vectorized message for running semantic search.
            topics:
                A list of document_ids used to filter which documents in the collection to search.
            offset:
                How many chunks to skip before returning chunks.
            limit:
                How many chunks to return.
            cut_off:
                Exclude matches with distances higher than this cut off.
            width:
                How many chunks before and after a match to return - not implemented.

        Returns:
            list of SearchResult: The document, text, score and related information of
            the chunk.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.match_collection_chunks(
                    collection_id=collection_id,
                    match_collection_chunks_request=rest.MatchCollectionChunksRequest(
                        vectors=vectors,
                        topics=topics,
                        offset=offset,
                        limit=limit,
                        cut_off=cut_off,
                    ),
                    _headers=header,
                )
            )
        return [SearchResult(**c.to_dict()) for c in response]

    async def search_chunks(
        self, collection_id: str, query: str, topics: List[str], offset: int, limit: int
    ) -> List[SearchResult]:
        """Find chunks related to a message using lexical search.

        Chunks are sorted by relevance and similarity score to the message.

        Args:
            collection_id:
                ID of the collection to search within.
            query:
                Question or imperative from the end user to search a collection for.
            topics:
                A list of document_ids used to filter which documents in the collection to search.
            offset:
                How many chunks to skip before returning chunks.
            limit:
                How many chunks to return.

        Returns:
            list of SearchResult: The document, text, score and related information of the chunk.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.collection_api.search_collection_chunks(
                    collection_id=collection_id,
                    search_collection_chunks_request=rest.SearchCollectionChunksRequest(
                        query=query,
                        topics=topics,
                        offset=offset,
                        limit=limit,
                    ),
                    _headers=header,
                )
            )
        return [SearchResult(**c.to_dict()) for c in response]

    async def list_document_chunks(
        self, document_id: str, collection_id: Optional[str] = None
    ) -> List[SearchResult]:
        """Returns all chunks for a specific document.

        Args:
            document_id:
                ID of the document.
            collection_id:
                ID of the collection the document belongs to. If not specified, an arbitrary collections containing
                the document is chosen.
        Returns:
            list of SearchResult: The document, text, score and related information of the chunk.
        """
        if collection_id is None:
            collections = await self.list_collections_for_document(document_id, 0, 1)
            if len(collections) == 0:
                raise ValueError(
                    "The specified document is not associated with any collection."
                )
            collection_id = collections[0].id

        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.document_api.list_document_chunks(
                    collection_id=collection_id,
                    document_id=document_id,
                    _headers=header,
                )
            )
        return [SearchResult(**c.to_dict()) for c in response]

    async def set_chat_message_votes(self, chat_message_id: str, votes: int) -> Result:
        """Change the vote value of a chat message.

        Set the exact value of a vote for a chat message. Any message type can
        be updated, but only LLM response votes will be visible in the UI.
        The expectation is 0: unvoted, -1: dislike, 1 like. Values outside of this will
        not be viewable in the UI.

        Args:
            chat_message_id:
                ID of a chat message, any message can be used but only
                LLM responses will be visible in the UI.
            votes:
                Integer value for the message. Only -1 and 1 will be visible in the
                UI as dislike and like respectively.

        Returns:
            Result: The status of the update.

        Raises:
            Exception: The upload request was unsuccessful.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_result(
                _rest_to_client_exceptions(
                    rest_client.chat_api.set_message_votes(
                        message_id=chat_message_id,
                        message_vote_update_request=rest.MessageVoteUpdateRequest(
                            votes=votes
                        ),
                        _headers=header,
                    )
                )
            )
        return result

    async def update_collection(
        self, collection_id: str, name: str, description: str
    ) -> str:
        """Update the metadata for a given collection.

        All variables are required. You can use `h2ogpte.get_collection(<id>).name` or
        description to get the existing values if you only want to change one or the other.

        Args:
            collection_id:
                ID of the collection to update.
            name:
                New name of the collection, this is required.
            description:
                New description of the collection, this is required.

        Returns:
            str: ID of the updated collection.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            collection = await _rest_to_client_exceptions(
                rest_client.collection_api.update_collection(
                    collection_id=collection_id,
                    collection_update_request=rest.CollectionUpdateRequest(
                        name=name, description=description
                    ),
                    _headers=header,
                )
            )
        return collection.id

    async def update_collection_rag_type(
        self, collection_id: str, name: str, description: str, rag_type
    ) -> str:
        """Update the metadata for a given collection.

        All variables are required. You can use `h2ogpte.get_collection(<id>).name` or
        description to get the existing values if you only want to change one or the other.

        Args:
            collection_id:
                ID of the collection to update.
            name:
                New name of the collection, this is required.
            description:
                New description of the collection, this is required.
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

        Returns:
            str: ID of the updated collection.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            collection = await _rest_to_client_exceptions(
                rest_client.collection_api.update_collection(
                    collection_id=collection_id,
                    collection_update_request=rest.CollectionUpdateRequest(
                        name=name, description=description, rag_type=rag_type
                    ),
                    _headers=header,
                )
            )
        return collection.id

    async def reset_collection_prompt_settings(self, collection_id: str) -> str:
        """Reset the prompt settings for a given collection.

        Args:
            collection_id:
                ID of the collection to update.

        Returns:
            str: ID of the updated collection.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.collection_api.reset_collection_prompt_settings(
                    collection_id=collection_id,
                    _headers=header,
                )
            )
        return collection_id

    async def update_collection_settings(
        self, collection_id: str, collection_settings: dict
    ) -> str:
        """
        Set the new collection settings, must be complete.
        Be careful not to delete any settings you want to keep.

        Args:
            collection_id:
                ID of the collection to update.
            collection_settings:
                Dictionary containing the new collection settings.

        Returns:
            str: ID of the updated collection.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.collection_api.update_collection_settings(
                    collection_id=collection_id,
                    collection_settings=rest.CollectionSettings.from_dict(
                        collection_settings
                    ),
                    _headers=header,
                )
            )
        return collection_id

    async def update_collection_metadata(
        self, collection_id: str, collection_metadata: dict
    ) -> str:
        """
        Set the new collection metadata overwriting the existing metadata.
        Be careful not to delete any settings you want to keep.

        Args:
            collection_id:
                ID of the collection to update.
            collection_metadata:
                Dictionary containing the new collection metadata.

        Returns:
            str: ID of the updated collection.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.collection_api.update_collection_metadata(
                    collection_id=collection_id,
                    request_body=collection_metadata,
                    _headers=header,
                )
            )
        return collection_id

    async def update_document_name(self, document_id: str, name: str) -> str:
        """Update the name metadata for a given document.

        Args:
            document_id:
                ID of the document to update.
            name:
                New name of the document, must include file extension.

        Returns:
            str: ID of the updated document.
        """
        if not name.strip():
            raise ValueError("The new name of the document cannot be empty.")

        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            document = await _rest_to_client_exceptions(
                rest_client.document_api.update_document(
                    document_id=document_id,
                    document_update_request=rest.DocumentUpdateRequest(
                        name=name.strip()
                    ),
                    _headers=header,
                )
            )
        return document.id

    async def update_document_metadata(
        self, document_id: str, document_metadata: dict
    ) -> str:
        """
        Set the new document metadata overwriting the existing metadata.
        Be careful not to delete any settings you want to keep.

        Args:
            document_id:
                ID of the document to update.
            document_metadata:
                Dictionary containing the new document metadata.

        Returns:
            str: ID of the updated document.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.document_api.update_document_metadata(
                    document_id=document_id,
                    request_body=document_metadata,
                    _headers=header,
                )
            )
        return document_id

    async def update_document_uri(self, document_id: str, uri: str) -> str:
        """Update the URI metadata for a given document.

        Args:
            document_id:
                ID of the document to update.
            uri:
                New URI of the document, this is required.

        Returns:
            str: ID of the updated document.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            document = await _rest_to_client_exceptions(
                rest_client.document_api.update_document(
                    document_id=document_id,
                    document_update_request=rest.DocumentUpdateRequest(uri=uri.strip()),
                    _headers=header,
                )
            )
        return document.id

    async def upload(self, file_name: str, file: Any, uri: Optional[str] = None) -> str:
        """Upload a file to the H2OGPTE backend.

        Uploaded files are not yet accessible and need to be ingested into a collection.

        See Also:
            ingest_uploads: Add the uploaded files to a collection.
            delete_upload: Delete uploaded file

        Args:
            file_name:
                What to name the file on the server, must include file extension.
            file:
                File object to upload, often an opened file from `with open(...) as f`.
            uri:
                Optional - URI you would like to associate with the file.

        Returns:
            str: The upload id to be used in ingest jobs.

        Raises:
            Exception: The upload request was unsuccessful.
        """
        mtime = ""
        try:
            mtime = str(
                int(Path(file.name).stat().st_mtime) * 1000
            )  # millis since Epoch
        except:
            pass

        if isinstance(file, io.StringIO) or isinstance(file, io.TextIOBase):
            file = io.BytesIO(file.read().encode("utf8"))

        files_data = {
            "file": (file_name, file),
            "mtime": (None, mtime),
            "uri": (None, uri or ""),
        }

        res = await self._put("/rpc/fs", files=files_data)
        self._raise_error_if_any(res)
        return _to_id(json.loads(res.text))

    async def list_upload(self) -> List[str]:
        """List pending file uploads to the H2OGPTE backend.

        Uploaded files are not yet accessible and need to be ingested into a collection.

        See Also:
            upload: Upload the files into the system to then be ingested into a collection.
            ingest_uploads: Add the uploaded files to a collection.
            delete_upload: Delete uploaded file

        Returns:
            List[str]: The pending upload ids to be used in ingest jobs.

        Raises:
            Exception: The upload list request was unsuccessful.
        """
        res = await self._get("/rpc/fs")
        self._raise_error_if_any(res)
        return json.loads(res.text)

    async def delete_upload(self, upload_id: str) -> str:
        """Delete a file previously uploaded with the "upload" method.

        See Also:
            upload: Upload the files into the system to then be ingested into a collection.
            ingest_uploads: Add the uploaded files to a collection.

        Args:
            upload_id:
                ID of a file to remove

        Returns:
            upload_id: The upload id of the removed.

        Raises:
            Exception: The delete upload request was unsuccessful.
        """
        res = await self._delete(f"/rpc/fs?id={upload_id}")
        return _to_id(res)

    def connect(
        self,
        chat_session_id: str,
        prompt_template_id: Optional[str] = None,
        open_timeout: int = 10,
        close_timeout: int = 10,
        max_connect_retries: int = 10,
        connect_retry_delay: int = 0.5,
        connect_retry_max_delay: int = 60,
    ) -> SessionAsync:
        """Create and participate in a chat session.
        This is a live connection to the H2OGPTE server contained to a specific
        chat session on top of a single collection of documents. Users will find all
        questions and responses in this session in a single chat history in the UI.

        Args:
            chat_session_id:
                ID of the chat session to connect to.
            prompt_template_id:
                ID of the prompt template to use.
            open_timeout:
                Timeout in seconds for opening the connection.
            close_timeout:
                Timeout in seconds for closing the connection.
            max_connect_retries:
                Maximum number of connection retry attempts.
            connect_retry_delay:
                Initial delay in seconds between connection retries.
            connect_retry_max_delay:
                Maximum delay in seconds between connection retries.

        Returns:
            Session: Live chat session connection with an LLM.
        """
        return SessionAsync(
            chat_session_id=chat_session_id,
            client=self,
            prompt_template_id=prompt_template_id,
            open_timeout=open_timeout,
            close_timeout=close_timeout,
            max_connect_retries=max_connect_retries,
            connect_retry_delay=connect_retry_delay,
            connect_retry_max_delay=connect_retry_max_delay,
        )

    async def get_llms(self) -> List[Dict[str, Any]]:
        """Lists metadata information about available LLMs in the environment.

        Returns:
            list of dict (string, ANY): Name and details about each available model.

        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            models = await _rest_to_client_exceptions(
                rest_client.model_api.list_models(_headers=header)
            )
        return [m.to_dict() for m in models]

    async def get_llm_names(self) -> List[str]:
        """Lists names of available LLMs in the environment.

        Returns:
            list of string: Name of each available model.

        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            models = await _rest_to_client_exceptions(
                rest_client.model_api.list_models(_headers=header)
            )
        return [m.display_name for m in models]

    async def get_vision_capable_llm_names(self) -> List[str]:
        """Lists names of available vision-capable multi-modal LLMs (that can natively handle images as input) in the environment.

        Returns:
            list of string: Name of each available model.

        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.model_api.get_vision_capable_model_names(_headers=header)
            )
        return response

    async def get_llm_and_auto_vision_llm_names(self) -> Dict[str, str]:
        """
        Get mapping of llm to its vision_model when ["auto"] is passed as visible_vision_models

        Returns:
            dictionary {'llm1': 'llm1_vision_llm', etc.}
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.model_api.get_model_to_vision_model_mapping(_headers=header)
            )
        return response

    async def get_reasoning_capable_llm_names(self) -> List[str]:
        """Lists names of available reasoning-capable (that can natively reason) in the environment.

        Returns:
            list of string: Name of each available model.

        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.model_api.get_reasoning_capable_model_names(_headers=header)
            )
        return response

    async def get_llm_and_auto_reasoning_llm_names(self) -> Dict[str, str]:
        """
        Get mapping of llm to its reasoning_model when ["auto"] is passed as visible_reasoning_models

        Returns:
            dictionary {'llm1': 'llm1_reasoning_llm', etc.}
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.model_api.get_model_to_reasoning_model_mapping(
                    _headers=header
                )
            )
        return response

    async def download_document(
        self,
        destination_directory: Union[str, Path],
        destination_file_name: str,
        document_id: str,
    ) -> Path:
        """Downloads a document to a local system directory.

        Args:
            destination_directory:
                Destination directory to save file into.
            destination_file_name:
                Destination file name.
            document_id:
                Document ID.

        Returns:
            Path: Path of downloaded document
        """
        destination_directory = Path(destination_directory)
        destination_file = destination_directory / destination_file_name
        if not destination_directory.is_dir():
            raise FileNotFoundError("Destination directory does not exist")
        if destination_file.exists():
            raise FileExistsError(f"File {destination_file} already exists")

        res = await self._get(
            f"/file?id={document_id}&name={quote(destination_file_name)}", as_json=False
        )
        self._raise_error_if_any(res)

        async with aiofiles.open(destination_file, "wb") as f:
            await f.write(res.content)
        return destination_file

    async def get_document_content(self, file_name: str, document_id: str) -> bytes:
        """Downloads a document and return its content as a byte array.

        Args:
            file_name:
                File name.
            document_id:
                Document ID.

        Returns:
            Path: File content

        """
        res = await self._get(
            f"/file?id={document_id}&name={quote(file_name)}", as_json=False
        )
        self._raise_error_if_any(res)

        return res.content

    async def list_recent_prompt_templates(
        self, offset: int, limit: int
    ) -> List[PromptTemplate]:
        """Fetch user's prompt templates sorted by last update time.

        Args:
            offset:
                How many prompt templates to skip before returning.
            limit:
                How many prompt templates to return.

        Returns:
            list of PromptTemplate: set of prompts
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.prompt_template_api.list_prompt_templates(
                    offset=offset,
                    limit=limit,
                    _headers=header,
                )
            )
        return [PromptTemplate(**d.to_dict()) for d in response]

    async def list_recent_prompt_templates_sort(
        self,
        offset: int,
        limit: int,
        sort_column: str,
        ascending: bool,
        template_type: str = "all",
        filter: str = "",
    ) -> List[PromptTemplate]:
        """Fetch user's prompt templates sorted by last update time.

        Args:
            offset:
                How many prompt templates to skip before returning.
            limit:
                How many prompt templates to return.
            sort_column:
                Sort column.
            ascending:
                When True, return sorted by sort_column in ascending order.
            template_type:
                When set, will be used as a type filter, possible values are: all, user, system.
            filter:
                When set, will be used as a filter on some prompt template columns.

        Returns:
            list of PromptTemplate: set of prompts
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.prompt_template_api.list_prompt_templates(
                    offset=offset,
                    limit=limit,
                    sort_column=sort_column,
                    ascending=ascending,
                    template_type=template_type,
                    filter=filter,
                    _headers=header,
                )
            )
        return [PromptTemplate(**d.to_dict()) for d in response]

    async def list_all_recent_prompt_templates(
        self, offset: int, limit: int
    ) -> List[PromptTemplate]:
        """Fetch user's prompt templates sorted by last update time.

        Note: Users with permission to manage prompt templates can use this to list hidden default prompt templates.

        Args:
            offset:
                How many prompt templates to skip before returning.
            limit:
                How many prompt templates to return.

        Returns:
            list of PromptTemplate: set of prompts
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.prompt_template_api.list_all_prompt_templates(
                    offset=offset,
                    limit=limit,
                    _headers=header,
                )
            )
        return [PromptTemplate(**d.to_dict()) for d in response]

    async def list_all_recent_prompt_templates_sort(
        self,
        offset: int,
        limit: int,
        sort_column: str,
        ascending: bool,
        template_type: str = "all",
        filter: str = "",
    ) -> List[PromptTemplate]:
        """Fetch user's prompt templates sorted by last update time.

        Note: Users with permission to manage prompt templates can use this to list hidden default prompt templates.

        Args:
            offset:
                How many prompt templates to skip before returning.
            limit:
                How many prompt templates to return.
            sort_column:
                Sort column.
            ascending:
                When True, return sorted by sort_column in ascending order.
            template_type:
                When set, will be used as a type filter, possible values are: all, user, system.
            filter:
                When set, will be used as a filter on some prompt template columns.

        Returns:
            list of PromptTemplate: set of prompts
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.prompt_template_api.list_all_prompt_templates(
                    offset=offset,
                    limit=limit,
                    sort_column=sort_column,
                    ascending=ascending,
                    template_type=template_type,
                    filter=filter,
                    _headers=header,
                )
            )
        return [PromptTemplate(**d.to_dict()) for d in response]

    async def get_prompt_template(self, id: Optional[str] = None) -> PromptTemplate:
        """Get a prompt template

        Args:
            id:
                String id of the prompt template to retrieve or None for default

        Returns:
            PromptTemplate: prompts

        Raises:
            KeyError: The prompt template was not found.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            if id is None:
                response = await _rest_to_client_exceptions(
                    rest_client.prompt_template_api.get_default_prompt_template(
                        _headers=header
                    )
                )
            else:
                response = await _rest_to_client_exceptions(
                    rest_client.prompt_template_api.get_prompt_template(
                        prompt_template_id=id, _headers=header
                    )
                )
        return PromptTemplate(**response.to_dict())

    async def delete_prompt_templates(self, ids: Iterable[str]) -> Result:
        """Deletes prompt templates

        Args:
            ids:
                List of string ids of prompte templates to delete from the system.

        Returns:
            Result: Status of the delete job.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_result(
                _rest_to_client_exceptions(
                    rest_client.prompt_template_api.delete_prompt_template(
                        prompt_template_id=ids, _headers=header
                    )
                )
            )
        return result

    async def update_prompt_template(
        self,
        id: str,
        name: str,
        description: Union[str, None] = None,
        lang: Union[str, None] = None,
        system_prompt: Union[str, None] = None,
        pre_prompt_query: Union[str, None] = None,
        prompt_query: Union[str, None] = None,
        hyde_no_rag_llm_prompt_extension: Union[str, None] = None,
        pre_prompt_summary: Union[str, None] = None,
        prompt_summary: Union[str, None] = None,
        system_prompt_reflection: Union[str, None] = None,
        pre_prompt_reflection: Union[str, None] = None,
        prompt_reflection: Union[str, None] = None,
        auto_gen_description_prompt: Union[str, None] = None,
        auto_gen_document_summary_pre_prompt_summary: Union[str, None] = None,
        auto_gen_document_summary_prompt_summary: Union[str, None] = None,
        auto_gen_document_sample_questions_prompt: Union[str, None] = None,
        default_sample_questions: Union[List[str], None] = None,
        image_batch_image_prompt: Union[str, None] = None,
        image_batch_final_prompt: Union[str, None] = None,
    ) -> str:
        """
        Update a prompt template

        Args:
            id:
                String ID of the prompt template to update
            name:
                Name of the prompt template
            description:
                Description of the prompt template
            lang:
                Language code
            system_prompt:
                System Prompt
            pre_prompt_query:
                Text that is prepended before the contextual document chunks.
            prompt_query:
                Text that is appended to the beginning of the user's message.
            hyde_no_rag_llm_prompt_extension:
                LLM prompt extension.
            pre_prompt_summary:
                Prompt that goes before each large piece of text to summarize
            prompt_summary:
                Prompt that goes after each large piece of text to summarize
            system_prompt_reflection:
                System Prompt for self-reflection
            pre_prompt_reflection:
                Deprecated - ignored
            prompt_reflection:
                Template for self-reflection, must contain two occurrences of %s for full previous prompt (including system prompt, document related context and prompts if applicable, and user prompts) and answer
            auto_gen_description_prompt:
                prompt to create a description of the collection.
            auto_gen_document_summary_pre_prompt_summary:
                pre_prompt_summary for summary of a freshly imported document (if enabled).
            auto_gen_document_summary_prompt_summary:
                prompt_summary for summary of a freshly imported document (if enabled).
            auto_gen_document_sample_questions_prompt:
                prompt to create sample questions for a freshly imported document (if enabled).
            default_sample_questions:
                default sample questions in case there are no auto-generated sample questions.
            image_batch_final_prompt:
                Prompt for each image batch for vision models
            image_batch_image_prompt:
                Prompt to reduce all answers each image batch for vision models

        Returns:
            str: The ID of the updated prompt template.
        """
        if prompt_reflection is not None:
            assert prompt_reflection.count("%s") == 2, (
                "prompt reflection must contain exactly two occurrences of %s "
                "(one for the full previous prompt including system prompt, document related context and prompts if applicable, and user prompts and one for the response)"
            )
        if pre_prompt_reflection:
            raise DeprecationWarning(
                "pre_prompt_reflection is no longer used, can be added to the beginning of prompt_reflection."
            )

        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.prompt_template_api.update_prompt_template(
                    prompt_template_id=id,
                    body=rest.PromptTemplateBase(
                        name=name,
                        description=description,
                        lang=lang,
                        system_prompt=system_prompt,
                        pre_prompt_query=pre_prompt_query,
                        prompt_query=prompt_query,
                        hyde_no_rag_llm_prompt_extension=hyde_no_rag_llm_prompt_extension,
                        pre_prompt_summary=pre_prompt_summary,
                        prompt_summary=prompt_summary,
                        system_prompt_reflection=system_prompt_reflection,
                        prompt_reflection=prompt_reflection,
                        auto_gen_description_prompt=auto_gen_description_prompt,
                        auto_gen_document_summary_pre_prompt_summary=auto_gen_document_summary_pre_prompt_summary,
                        auto_gen_document_summary_prompt_summary=auto_gen_document_summary_prompt_summary,
                        auto_gen_document_sample_questions_prompt=auto_gen_document_sample_questions_prompt,
                        default_sample_questions=default_sample_questions,
                        image_batch_image_prompt=image_batch_image_prompt,
                        image_batch_final_prompt=image_batch_final_prompt,
                    ),
                    _headers=header,
                )
            )

        return response.id

    async def create_prompt_template(
        self,
        name: str,
        description: Union[str, None] = None,
        lang: Union[str, None] = None,
        system_prompt: Union[str, None] = None,
        pre_prompt_query: Union[str, None] = None,
        prompt_query: Union[str, None] = None,
        hyde_no_rag_llm_prompt_extension: Union[str, None] = None,
        pre_prompt_summary: Union[str, None] = None,
        prompt_summary: Union[str, None] = None,
        system_prompt_reflection: Union[str, None] = None,
        pre_prompt_reflection: Union[str, None] = None,
        prompt_reflection: Union[str, None] = None,
        auto_gen_description_prompt: Union[str, None] = None,
        auto_gen_document_summary_pre_prompt_summary: Union[str, None] = None,
        auto_gen_document_summary_prompt_summary: Union[str, None] = None,
        auto_gen_document_sample_questions_prompt: Union[str, None] = None,
        default_sample_questions: Union[List[str], None] = None,
        image_batch_image_prompt: Union[str, None] = None,
        image_batch_final_prompt: Union[str, None] = None,
    ) -> str:
        """
        Create a new prompt template

        Args:
            name:
                Name of the prompt template
            description:
                Description of the prompt template
            lang:
                Language code
            system_prompt:
                System Prompt
            pre_prompt_query:
                Text that is prepended before the contextual document chunks.
            prompt_query:
                Text that is appended to the beginning of the user's message.
            hyde_no_rag_llm_prompt_extension:
                LLM prompt extension.
            pre_prompt_summary:
                Prompt that goes before each large piece of text to summarize
            prompt_summary:
                Prompt that goes after each large piece of text to summarize
            system_prompt_reflection:
                System Prompt for self-reflection
            pre_prompt_reflection:
                Deprecated - ignored
            prompt_reflection:
                Template for self-reflection, must contain two occurrences of %s for full previous prompt (including system prompt, document related context and prompts if applicable, and user prompts) and answer
            auto_gen_description_prompt:
                prompt to create a description of the collection.
            auto_gen_document_summary_pre_prompt_summary:
                pre_prompt_summary for summary of a freshly imported document (if enabled).
            auto_gen_document_summary_prompt_summary:
                prompt_summary for summary of a freshly imported document (if enabled).
            auto_gen_document_sample_questions_prompt:
                prompt to create sample questions for a freshly imported document (if enabled).
            default_sample_questions:
                default sample questions in case there are no auto-generated sample questions.
            image_batch_final_prompt:
                Prompt for each image batch for vision models
            image_batch_image_prompt:
                Prompt to reduce all answers each image batch for vision models

        Returns:
            str: The ID of the newly created prompt template.
        """
        if prompt_reflection is not None:
            assert prompt_reflection.count("%s") == 2, (
                "prompt reflection must contain exactly two occurrences of %s "
                "(one for the full previous prompt including system prompt, document related context and prompts if applicable, and user prompts and one for the response)"
            )
        if pre_prompt_reflection:
            raise DeprecationWarning(
                "pre_prompt_reflection is no longer used, can be added to the beginning of prompt_reflection."
            )

        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.prompt_template_api.create_prompt_template(
                    prompt_template_create_request=rest.PromptTemplateCreateRequest(
                        name=name,
                        description=description,
                        lang=lang,
                        system_prompt=system_prompt,
                        pre_prompt_query=pre_prompt_query,
                        prompt_query=prompt_query,
                        hyde_no_rag_llm_prompt_extension=hyde_no_rag_llm_prompt_extension,
                        pre_prompt_summary=pre_prompt_summary,
                        prompt_summary=prompt_summary,
                        system_prompt_reflection=system_prompt_reflection,
                        prompt_reflection=prompt_reflection,
                        auto_gen_description_prompt=auto_gen_description_prompt,
                        auto_gen_document_summary_pre_prompt_summary=auto_gen_document_summary_pre_prompt_summary,
                        auto_gen_document_summary_prompt_summary=auto_gen_document_summary_prompt_summary,
                        auto_gen_document_sample_questions_prompt=auto_gen_document_sample_questions_prompt,
                        default_sample_questions=default_sample_questions,
                        image_batch_image_prompt=image_batch_image_prompt,
                        image_batch_final_prompt=image_batch_final_prompt,
                    ),
                    _headers=header,
                )
            )
        return response.id

    async def count_prompt_templates(self) -> int:
        """Counts number of prompt templates

        Returns:
            int: The count of prompt templates
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.prompt_template_api.get_prompt_template_count(
                    _headers=header
                )
            )
        return response.count

    async def share_prompt(
        self, prompt_id: str, permission: SharePermission
    ) -> ShareResponseStatus:
        """Share a prompt template to a user.

        Args:
            prompt_id:
                ID of the prompt template to share.
            permission:
                Defines the rule for sharing, i.e. permission level.

        Returns:
            ShareResponseStatus: Status of share request.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_share_permission_status(
                _rest_to_client_exceptions(
                    rest_client.prompt_template_api.share_prompt_template(
                        prompt_template_id=prompt_id,
                        username=permission.username,
                        _headers=header,
                    )
                )
            )
        return result

    async def unshare_prompt(
        self, prompt_id: str, permission: SharePermission
    ) -> ShareResponseStatus:
        """Remove sharing of a prompt template to a user.

        Args:
            prompt_id:
                ID of the prompt template to un-share.
            permission:
                Defines the user for which collection access is revoked.

        ShareResponseStatus: Status of share request.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_share_permission_status(
                _rest_to_client_exceptions(
                    rest_client.prompt_template_api.unshare_prompt_template(
                        prompt_template_id=prompt_id,
                        username=permission.username,
                        _headers=header,
                    )
                )
            )
        return result

    async def share_prompt_with_group(
        self, prompt_id: str, permission: GroupSharePermission
    ) -> ShareResponseStatus:
        """Share a prompt to a group.

        Args:
            prompt_id:
                ID of the prompt to share.
            permission:
                Specific permissions for a group.

        Returns:
            ShareResponseStatus: Status of share request.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_share_permission_status(
                _rest_to_client_exceptions(
                    rest_client.prompt_template_api.share_prompt_template_with_group(
                        prompt_template_id=prompt_id,
                        group_id=permission.group_id,
                        _headers=header,
                    )
                )
            )
        return result

    async def unshare_prompt_from_group(
        self, prompt_id: str, permission: GroupSharePermission
    ) -> ShareResponseStatus:
        """Unshare a prompt from a group.

        Args:
            prompt_id:
                ID of the prompt to un-share.
            permission:
                Specific permissions for a group.

        Returns:
            ShareResponseStatus: Status of share request.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_share_permission_status(
                _rest_to_client_exceptions(
                    rest_client.prompt_template_api.unshare_prompt_template_from_group(
                        prompt_template_id=prompt_id,
                        group_id=permission.group_id,
                        _headers=header,
                    )
                )
            )
        return result

    async def reset_and_share_prompt_template_with_groups(
        self, prompt_id: str, new_groups: List[str]
    ) -> ShareResponseStatus:
        """Remove all groups who have access to a prompt template and share it with the provided list of new group ids.

        Args:
            prompt_id:
                ID of the prompt template to un-share.
            new_groups:
                The list of group ids this prompt template will be shared with.

        ShareResponseStatus: Status of share request.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_share_permission_status(
                _rest_to_client_exceptions(
                    rest_client.prompt_template_api.reset_and_share_prompt_template_with_groups(
                        prompt_template_id=prompt_id,
                        reset_and_share_prompt_template_with_groups_request=rest.ResetAndSharePromptTemplateWithGroupsRequest(
                            groups=new_groups,
                        ),
                        _headers=header,
                    )
                )
            )
        return result

    async def unshare_prompt_for_all(self, prompt_id: str) -> ShareResponseStatus:
        """Remove sharing of a prompt template to all other users but the original owner (owner action only).

        Args:
            prompt_id:
                ID of the prompt template to un-share.

        ShareResponseStatus: Status of share request.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_share_permission_status(
                _rest_to_client_exceptions(
                    rest_client.prompt_template_api.unshare_prompt_template_for_all(
                        prompt_template_id=prompt_id, _headers=header
                    )
                )
            )
        return result

    async def reset_and_share_prompt_template(
        self, prompt_id: str, new_usernames: List[str]
    ) -> ShareResponseStatus:
        """Remove all users who have access to a prompt template (except for the owner) and share it with the provided list of new users.

        Args:
            prompt_id:
                ID of the prompt template to un-share.
            new_usernames:
                The list of usernames belonging to the users this prompt template will be shared with.

        ShareResponseStatus: Status of share request.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_share_permission_status(
                _rest_to_client_exceptions(
                    rest_client.prompt_template_api.reset_and_share_prompt_template(
                        prompt_template_id=prompt_id,
                        reset_and_share_prompt_template_request=rest.ResetAndSharePromptTemplateRequest(
                            usernames=new_usernames,
                        ),
                        _headers=header,
                    )
                )
            )
        return result

    async def make_prompt_template_public(self, prompt_template_id: str):
        """Make a prompt template public

        Once a prompt template is public, it can be seen and used by all users.

        Args:
            prompt_template_id:
                ID of the prompt template to make public.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.prompt_template_api.update_prompt_template_privacy(
                    prompt_template_id=prompt_template_id,
                    update_prompt_template_privacy_request=rest.UpdatePromptTemplatePrivacyRequest(
                        is_public=True
                    ),
                    _headers=header,
                )
            )

    async def make_prompt_template_private(self, prompt_template_id: str):
        """Make a prompt template private

        Once a prompt template is private, other users will no longer
        be able to see or use it unless it has been shared individually or by group.

        Args:
            prompt_template_id:
                ID of the prompt template to make private.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.prompt_template_api.update_prompt_template_privacy(
                    prompt_template_id=prompt_template_id,
                    update_prompt_template_privacy_request=rest.UpdatePromptTemplatePrivacyRequest(
                        is_public=False
                    ),
                    _headers=header,
                )
            )

    async def list_prompt_permissions(self, prompt_id: str) -> List[SharePermission]:
        """Returns a list of access permissions for a given prompt template.

        The returned list of permissions denotes who has access to
        the prompt template and their access level.

        Args:
            prompt_id:
                ID of the prompt template to inspect.

        Returns:
            list of SharePermission: Sharing permissions list for the given prompt template.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.prompt_template_api.get_prompt_template_permissions(
                    prompt_template_id=prompt_id, _headers=header
                )
            )
        return [SharePermission(**d.to_dict()) for d in response]

    async def list_prompt_group_permissions(
        self, prompt_id: str
    ) -> List[GroupSharePermission]:
        """Returns a list of group access permissions for a given prompt template.

        The returned list of group permissions denoting which groups have access to
        the prompt template.

        Args:
            prompt_id:
                ID of the prompt template to inspect.

        Returns:
            list of GroupSharePermission: Group sharing permissions list for the given prompt template.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.prompt_template_api.get_prompt_template_group_permissions(
                    prompt_template_id=prompt_id, _headers=header
                )
            )
        return [GroupSharePermission(**d.to_dict()) for d in response]

    async def set_default_prompt_template_visibility(
        self, prompt_id: str, is_visible: bool
    ):
        """
        Updates a flag specifying whether a default prompt template is visible or hidden to users.

        Once you hide a default prompt template, users will no longer be able to use this prompt template.
        This will also affect collections and chats that have this as a default prompt template.
        Once you show a default prompt template, all users will be able to see and use this prompt template.

        Args:
            prompt_id:
                ID of the default prompt template you would like to change the visibility of.
            is_visible:
                Whether the default prompt template should be visible.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.prompt_template_api.update_default_prompt_template_visibility(
                    prompt_template_id=prompt_id,
                    update_default_prompt_template_visibility_request=rest.UpdateDefaultPromptTemplateVisibilityRequest(
                        is_visible=is_visible
                    ),
                    _headers=header,
                )
            )

    async def set_collection_prompt_template(
        self,
        collection_id: str,
        prompt_template_id: Union[str, None],
        strict_check: bool = False,
    ) -> str:
        """Set the prompt template for a collection

        Args:
            collection_id:
                ID of the collection to update.
            prompt_template_id:
                ID of the prompt template to get the prompts from. None to delete and fall back to system defaults.
            strict_check:
                whether to check that the collection's embedding model and the prompt template are optimally compatible

        Returns:
            str: ID of the updated collection.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            if prompt_template_id is None:
                response = await _rest_to_client_exceptions(
                    rest_client.collection_api.delete_collection_prompt_template(
                        collection_id=collection_id, _headers=header
                    )
                )
            else:
                prompt_template = await self.get_prompt_template(prompt_template_id)
                embedding_model = (
                    await self.get_collection(collection_id)
                ).embedding_model
                if embedding_model:
                    all_embedding_models = await _rest_to_client_exceptions(
                        rest_client.model_api.list_embedding_models(_headers=header)
                    )
                    relevant_embedding_models = [
                        m for m in all_embedding_models if m.id == embedding_model
                    ]
                    if len(relevant_embedding_models) > 0:
                        langs = relevant_embedding_models[0].languages
                        if (
                            langs
                            and prompt_template.lang
                            and prompt_template.lang not in langs
                        ):
                            msg = (
                                f"Warning: The embedding model only supports the following languages: {langs}, "
                                f"but the prompt template specifies the following language: {prompt_template.lang}. "
                                f"Retrieval performance may not be ideal."
                            )
                            print(msg)
                            if strict_check:
                                raise RuntimeError(msg)
                response = await _rest_to_client_exceptions(
                    rest_client.collection_api.update_collection_prompt_template(
                        collection_id=collection_id,
                        prompt_template_change_request=rest.PromptTemplateChangeRequest(
                            prompt_template_id=prompt_template_id,
                        ),
                        _headers=header,
                    )
                )
        return response.id

    async def get_collection_prompt_template(
        self, collection_id: str
    ) -> Union[PromptTemplate, None]:
        """Get the prompt template for a collection

        Args:
            collection_id:
                ID of the collection

        Returns:
            str: ID of the prompt template.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            rest_collection = await _rest_to_client_exceptions(
                rest_client.collection_api.get_collection(
                    collection_id=collection_id, _headers=header
                )
            )
        if rest_collection.prompt_template_id is None:
            return None
        return await self.get_prompt_template(rest_collection.prompt_template_id)

    async def set_chat_session_prompt_template(
        self, chat_session_id: str, prompt_template_id: Union[str, None]
    ) -> str:
        """Set the prompt template for a chat_session

        Args:
            chat_session_id:
                ID of the chat session
            prompt_template_id:
                ID of the prompt template to get the prompts from. None to delete and fall back to system defaults.

        Returns:
            str: ID of the updated chat session
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            if prompt_template_id is None:
                response = await _rest_to_client_exceptions(
                    rest_client.chat_api.delete_chat_session_prompt_template(
                        session_id=chat_session_id,
                        _headers=header,
                    )
                )
            else:
                response = await _rest_to_client_exceptions(
                    rest_client.chat_api.update_chat_session_prompt_template(
                        session_id=chat_session_id,
                        prompt_template_change_request=rest.PromptTemplateChangeRequest(
                            prompt_template_id=prompt_template_id,
                        ),
                        _headers=header,
                    )
                )
        return response.id

    async def get_chat_session_prompt_template(
        self, chat_session_id: str
    ) -> Union[PromptTemplate, None]:
        """Get the prompt template for a chat_session

        Args:
            chat_session_id:
                ID of the chat session

        Returns:
            str: ID of the prompt template.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            rest_session = await _rest_to_client_exceptions(
                rest_client.chat_api.get_chat_session(
                    session_id=chat_session_id,
                    _headers=header,
                )
            )

        if rest_session.prompt_template_id is None:
            return None

        return await self.get_prompt_template(rest_session.prompt_template_id)

    async def set_chat_session_collection(
        self, chat_session_id: str, collection_id: Union[str, None]
    ) -> str:
        """Set the collection for a chat_session

        Args:
            chat_session_id:
                ID of the chat session
            collection_id:
                ID of the collection, or None to chat with the LLM only.

        Returns:
            str: ID of the updated chat session
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            if collection_id is None:
                response = await _rest_to_client_exceptions(
                    rest_client.chat_api.delete_chat_session_collection(
                        session_id=chat_session_id, _headers=header
                    )
                )
            else:
                response = await _rest_to_client_exceptions(
                    rest_client.chat_api.update_chat_session_collection(
                        session_id=chat_session_id,
                        collection_change_request=rest.CollectionChangeRequest(
                            collection_id=collection_id
                        ),
                        _headers=header,
                    )
                )
        return response.id

    async def download_reference_highlighting(
        self,
        message_id: str,
        destination_directory: str,
        output_type: str = "combined",
        limit: Optional[int] = None,
    ) -> list:
        """Get PDFs with reference highlighting

        Args:
            message_id:
                ID of the message to get references from
            destination_directory:
                Destination directory to save files into.
            output_type: str one of
                :code:`"combined"` Generates a PDF file for each source document, with all relevant chunks highlighted
                in each respective file. This option consolidates all highlights for each source document into a single
                PDF, making it easy to view all highlights related to that document at once.
                :code:`"split"` Generates a separate PDF file for each chunk, with only the relevant chunk highlighted
                in each file. This option is useful for focusing on individual sections without interference from other
                parts of the text. The output files names will be in the format "{document_id}_{chunk_id}.pdf"
            limit:
                The number of references to consider based on the highest confidence scores.

        Returns:
            list[Path]: List of paths of downloaded documents with highlighting

        """
        if not os.path.exists(destination_directory) or not os.path.isdir(
            destination_directory
        ):
            raise FileNotFoundError("Destination directory does not exist")

        chat_references = await self.list_chat_message_references(message_id, limit)
        doc_chat_references = defaultdict(list)
        for chat_ref in chat_references:
            doc_chat_references[(chat_ref.document_id, chat_ref.document_name)].append(
                chat_ref
            )

        files_list = []
        for (document_id, document_name), chat_refs in doc_chat_references.items():
            res = await self._get(f"/file?id={document_id}&name={quote(document_name)}")
            if res.status_code != 200:
                print(
                    f"Warning: HTTP error: {res.status_code}. document_id={document_id}"
                )
                continue

            if not res.content:
                print(f"Warning: received an empty response. document_id={document_id}")
                continue

            pymupdf = import_pymupdf()
            pdf_document = pymupdf.open("pdf", res.content)
            markers = []

            for ref in chat_refs:
                markers.append(ref.model_dump_json())

            filepaths = _process_pdf_with_annotations(
                pdf_document, markers, destination_directory, document_id, output_type
            )
            files_list.extend(filepaths)

        return files_list

    async def tag_document(self, document_id: str, tag_name: str) -> str:
        """Adds a tag to a document.

        Args:
            document_id:
                String id of the document to attach the tag to.
            tag_name:
                String representing the tag to attach.

        Returns:
            String: The id of the newly created tag.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.document_api.create_tag_on_document(
                    document_id=document_id,
                    tag_create_request=rest.TagCreateRequest(name=tag_name),
                    _headers=header,
                )
            )
        return response.id

    async def untag_document(self, document_id: str, tag_name: str) -> str:
        """Removes an existing tag from a document.

        Args:
            document_id:
                String id of the document to remove the tag from.
            tag_name:
                String representing the tag to remove.

        Returns:
            String: The id of the removed tag.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.document_api.delete_tag_from_document(
                    document_id=document_id, tag_name=tag_name, _headers=header
                )
            )
        return response.tag_id

    async def get_tag(self, tag_name: str) -> Tag:
        """Returns an existing tag.

        Args:
            tag_name:
                String The name of the tag to retrieve.

        Returns:
            Tag: The requested tag.

        Raises:
            KeyError: The tag was not found.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.tag_api.get_tag(tag_name=tag_name, _headers=header)
            )
        return Tag(**response.to_dict())

    async def create_tag(self, tag_name: str) -> str:
        """Creates a new tag.

        Args:
            tag_name:
                String representing the tag to create.

        Returns:
            String: The id of the created tag.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.tag_api.create_tag(
                    tag_create_request=rest.TagCreateRequest(name=tag_name),
                    _headers=header,
                )
            )
        return response.id

    async def update_tag(self, tag_name: str, description: str, format: str) -> str:
        """Updates a  tag.

        Args:
            tag_name:
                String representing the tag to update.
            description:
                String describing the tag.
            format:
                String representing the format of the tag.

        Returns:
            String: The id of the updated tag.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.tag_api.update_tag(
                    tag_name=tag_name,
                    tag_update_request=rest.TagUpdateRequest(
                        description=description, format=format
                    ),
                    _headers=header,
                )
            )
        return response.id

    async def list_all_tags(self) -> List[Tag]:
        """Lists all existing tags.

        Returns:
            List of Tags: List of existing tags.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.tag_api.list_tags(_headers=header)
            )
        return [Tag(**d.to_dict()) for d in response]

    async def list_documents_from_tags(
        self, collection_id: str, tags: List[str]
    ) -> List[Document]:
        """Lists documents that have the specified set of tags within a collection.
        Args:
            collection_id:
                String The id of the collection to find documents in.
            tags:
                List of Strings representing the tags to retrieve documents for.

        Returns:
            List of Documents: All the documents with the specified tags.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.tag_api.list_documents_for_tags(
                    collection_id=collection_id, tag_names=tags, _headers=header
                )
            )
        return [Document(**d.to_dict()) for d in response]

    async def add_user_document_permission(
        self, user_id: str, document_id: str
    ) -> [str, str]:
        """Associates a user with a document they have permission on.
        Args:
            user_id:
                String The id of the user that has the permission.
            document_id:
                String The id of the document that the permission is for.

        Returns:
            [user_id, document_id]: A tuple containing the user_id and document_id.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.permission_api.add_user_document_permission(
                    document_id=document_id,
                    user_id=user_id,
                    _headers=header,
                )
            )
        return [user_id, document_id]

    async def list_system_permissions(self) -> List[UserPermission]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            rest_permissions = await _rest_to_client_exceptions(
                rest_client.permission_api.list_permissions(_headers=header)
            )
        return [UserPermission(**p.to_dict()) for p in rest_permissions]

    async def list_system_roles(self) -> List[UserRole]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            rest_roles = await _rest_to_client_exceptions(
                rest_client.permission_api.list_roles(_headers=header)
            )
        return [UserRole(**r.to_dict()) for r in rest_roles]

    async def list_system_groups(self) -> List[UserGroup]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            rest_groups = await _rest_to_client_exceptions(
                rest_client.permission_api.list_groups(_headers=header)
            )
        return [UserGroup(**r.to_dict()) for r in rest_groups]

    async def list_user_roles(self, user_id: Optional[str] = None) -> List[UserRole]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            if user_id:
                rest_roles = await _rest_to_client_exceptions(
                    rest_client.permission_api.get_user_roles(
                        user_id=user_id, _headers=header
                    )
                )
            else:
                rest_roles = await _rest_to_client_exceptions(
                    rest_client.permission_api.get_current_user_roles(_headers=header)
                )
        return [UserRole(**r.to_dict()) for r in rest_roles]

    async def list_group_roles(self, group_id: str) -> List[UserRole]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            rest_roles = await _rest_to_client_exceptions(
                rest_client.permission_api.get_group_roles(
                    group_id=group_id, _headers=header
                )
            )
        return [UserRole(**r.to_dict()) for r in rest_roles]

    async def list_user_permissions(
        self, user_id: Optional[str] = None
    ) -> List[UserPermission]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            if user_id:
                rest_permissions = await _rest_to_client_exceptions(
                    rest_client.permission_api.get_user_permissions(
                        user_id=user_id, _headers=header
                    )
                )
            else:
                rest_permissions = await _rest_to_client_exceptions(
                    rest_client.permission_api.get_current_user_permissions(
                        _headers=header
                    )
                )
        return [UserPermission(**p.to_dict()) for p in rest_permissions]

    async def list_group_permissions(self, group_id: str) -> List[UserPermission]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            rest_permissions = await _rest_to_client_exceptions(
                rest_client.permission_api.get_group_permissions(
                    group_id=group_id, _headers=header
                )
            )
        return [UserPermission(**p.to_dict()) for p in rest_permissions]

    async def list_group_permissions_by_name(
        self, group_names: List[str]
    ) -> List[UserPermission]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            rest_permissions = await _rest_to_client_exceptions(
                rest_client.permission_api.list_permissions(
                    group_names=group_names, _headers=header
                )
            )
        return [UserPermission(**p.to_dict()) for p in rest_permissions]

    async def list_user_role_permissions(
        self, roles: List[str]
    ) -> List[UserPermission]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            rest_permissions = await _rest_to_client_exceptions(
                rest_client.permission_api.list_permissions(
                    role_names=roles, _headers=header
                )
            )
        return [UserPermission(**p.to_dict()) for p in rest_permissions]

    async def add_role_to_user(self, user_id: str, roles: List[str]) -> List[UserRole]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.permission_api.assign_roles_to_user(
                    user_id=user_id, role_names=roles, _headers=header
                )
            )
        return await self.list_user_roles(user_id=user_id)

    async def reset_roles_for_user(
        self, user_id: str, roles: List[str]
    ) -> List[UserRole]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.permission_api.reset_user_roles(
                    user_id=user_id,
                    roles_reset_request=rest.RolesResetRequest(new_roles=roles),
                    _headers=header,
                )
            )
        return await self.list_user_roles(user_id=user_id)

    async def remove_role_from_user(
        self, user_id: str, roles: List[str]
    ) -> List[UserRole]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.permission_api.remove_roles_from_user(
                    user_id=user_id, role_names=roles, _headers=header
                )
            )
        return await self.list_user_roles(user_id=user_id)

    async def add_role_to_group(
        self, group_id: str, roles: List[str]
    ) -> List[UserRole]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.permission_api.assign_roles_to_group(
                    group_id=group_id, role_names=roles, _headers=header
                )
            )
        return await self.list_group_roles(group_id=group_id)

    async def reset_roles_for_group(
        self, group_id: str, roles: List[str]
    ) -> List[UserRole]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.permission_api.reset_group_roles(
                    group_id=group_id,
                    roles_reset_request=rest.RolesResetRequest(new_roles=roles),
                    _headers=header,
                )
            )
        return await self.list_group_roles(group_id=group_id)

    async def remove_role_from_group(
        self, group_id: str, roles: List[str]
    ) -> List[UserRole]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.permission_api.remove_roles_from_group(
                    group_id=group_id, role_names=roles, _headers=header
                )
            )
        return await self.list_group_roles(group_id=group_id)

    async def is_permission_granted(self, permission: str) -> bool:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _rest_to_client_exceptions(
                rest_client.permission_api.is_permission_granted(
                    permission_check_request=rest.PermissionCheckRequest(
                        permission=permission
                    ),
                    _headers=header,
                )
            )
        return result

    async def is_collection_permission_granted(
        self, collection_id: str, permission: str
    ) -> bool:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _rest_to_client_exceptions(
                rest_client.permission_api.is_collection_permission_granted(
                    collection_id=collection_id,
                    permission_check_request=rest.PermissionCheckRequest(
                        permission=permission
                    ),
                    _headers=header,
                )
            )
        return result

    async def create_user_role(self, name: str, description: str) -> UserRole:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.permission_api.create_role(
                    role_create_request=rest.RoleCreateRequest(
                        name=name,
                        description=description,
                    ),
                    _headers=header,
                )
            )
        return UserRole(**response.to_dict())

    async def create_user_group(self, name: str, description: str) -> UserGroup:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.permission_api.create_group(
                    group_create_request=rest.GroupCreateRequest(
                        name=name,
                        description=description,
                    ),
                    _headers=header,
                )
            )
        return UserGroup(**response.to_dict())

    async def delete_user_roles_by_ids(self, roles_ids: Iterable[str]) -> Result:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_result(
                _rest_to_client_exceptions(
                    rest_client.permission_api.delete_roles(
                        role_ids=roles_ids,
                        _headers=header,
                    )
                )
            )
        return result

    async def delete_user_roles_by_names(self, roles_names: Iterable[str]) -> Result:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_result(
                _rest_to_client_exceptions(
                    rest_client.permission_api.delete_roles_by_names(
                        names=roles_names,
                        _headers=header,
                    )
                )
            )
        return result

    async def delete_user_groups_by_ids(self, groups_ids: Iterable[str]) -> Result:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_result(
                _rest_to_client_exceptions(
                    rest_client.permission_api.delete_groups(
                        group_ids=groups_ids,
                        _headers=header,
                    )
                )
            )
        return result

    async def delete_user_groups_by_names(self, groups_names: Iterable[str]) -> Result:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_result(
                _rest_to_client_exceptions(
                    rest_client.permission_api.delete_groups_by_names(
                        names=groups_names,
                        _headers=header,
                    )
                )
            )
        return result

    async def assign_permissions_to_role(
        self, role_name: str, permission_names: Iterable[str]
    ) -> Result:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_result(
                _rest_to_client_exceptions(
                    rest_client.permission_api.set_role_permissions(
                        role_id=role_name,
                        permission_reset_request=rest.PermissionResetRequest(
                            new_permissions=permission_names
                        ),
                        _headers=header,
                    )
                )
            )
        return result

    async def set_global_configuration(
        self,
        key_name: str,
        string_value: str,
        can_overwrite: bool,
        is_public: bool,
        value_type: str = None,
    ) -> List[GlobalConfigItem]:
        """Set a global configuration.

        Note: Both default collection size limit and inactivity interval can be disabled. To do so, pass '-1' as the string_value.

        Args:
            key_name:
                The name of the global config key.
            string_value:
                The value to be set for the global config.
            can_overwrite:
                Whether user settings can override this global setting.
            is_public:
                Whether users can see the value for this global setting.
            value_type:
                The type of the value to be set for the global config.

        Returns:
            List[GlobalConfigItem]: List of global configurations.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.configuration_api.set_global_configuration(
                    key_name=key_name,
                    set_global_configuration_request=rest.SetGlobalConfigurationRequest(
                        string_value=string_value,
                        can_overwrite=can_overwrite,
                        is_public=is_public,
                        value_type=value_type,
                    ),
                    _headers=header,
                )
            )
        return [GlobalConfigItem(**c.to_dict()) for c in response]

    async def get_global_configurations_by_admin(self) -> List[GlobalConfigItem]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.configuration_api.list_global_configurations(
                    as_admin=True,
                    _headers=header,
                )
            )
        return [GlobalConfigItem(**c.to_dict()) for c in response]

    async def get_global_configurations(self) -> List[GlobalConfigItem]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.configuration_api.list_global_configurations(
                    as_admin=False,
                    _headers=header,
                )
            )
        return [GlobalConfigItem(**c.to_dict()) for c in response]

    async def bulk_delete_global_configurations(
        self, key_names: List[str]
    ) -> List[GlobalConfigItem]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.configuration_api.delete_global_configurations(
                    key_names=key_names,
                    _headers=header,
                )
            )
        return [GlobalConfigItem(**c.to_dict()) for c in response]

    async def set_user_configuration_for_user(
        self, key_name: str, string_value: str, user_id: str, value_type: str = None
    ) -> List[ConfigItem]:
        """Set a user configuration for a specific user (overrides the global configuration and to be used by admins only).

        Note: Both default collection size limit and inactivity interval can be disabled. To do so, pass '-1' as the string_value.

        Args:
            key_name:
                The name of the global config key.
            string_value:
                The value to be set for the config.
            user_id:
                The user id you want to apply the config for.
            value_type:
                The type of the value to be set for the config.

        Returns:
            List[ConfigItem]: List of user configurations.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.configuration_api.set_user_configuration(
                    key_name=key_name,
                    user_id=user_id,
                    set_user_configuration_request=rest.SetUserConfigurationRequest(
                        string_value=string_value,
                        value_type=value_type,
                    ),
                    _headers=header,
                )
            )
        return [ConfigItem(**c.to_dict()) for c in response]

    async def get_user_configurations_for_user(self, user_id: str) -> List[ConfigItem]:
        """Gets the user configurations for a specific user (to be used by admins only).

        Args:
            user_id:
                The unique identifier of the user.

        Returns:
            List[ConfigItem]: List of user configurations.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.configuration_api.list_user_configurations(
                    user_id=user_id,
                    _headers=header,
                )
            )
        return [ConfigItem(**c.to_dict()) for c in response]

    async def get_user_configurations(self) -> List[ConfigItem]:
        """Gets the user configurations for the current user.

        Returns:
            List[ConfigItem]: List of user configurations.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.configuration_api.list_current_user_configurations(
                    _headers=header
                )
            )
        return [ConfigItem(**c.to_dict()) for c in response]

    async def bulk_delete_user_configurations_for_user(
        self, user_id: str, key_names: List[str]
    ) -> List[ConfigItem]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.configuration_api.delete_user_configurations(
                    user_id=user_id,
                    key_names=key_names,
                    _headers=header,
                )
            )
        return [ConfigItem(**c.to_dict()) for c in response]

    async def reset_user_configurations_for_user(
        self, key_name: str, user_id: str
    ) -> List[ConfigItem]:
        """Reset a user configuration for a specific user (to be used by admins only).

        Returns:
            List[ConfigItem]: List of user configurations.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.configuration_api.reset_user_configuration(
                    user_id=user_id,
                    key_name=key_name,
                    _headers=header,
                )
            )
        return [ConfigItem(**c.to_dict()) for c in response]

    async def delete_agent_directories(self, chat_session_id: str) -> bool:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_result(
                _rest_to_client_exceptions(
                    rest_client.chat_api.delete_agent_server_directories(
                        session_ids=[chat_session_id],
                        _headers=header,
                    )
                )
            )
        return result.status == "completed"

    async def set_role_configuration(
        self, key_name: str, role_id: str, string_value: str, value_type: str = None
    ) -> List[ConfigItem]:
        """Set a role configuration, overrides the global configuration.
        Args:
            role_id:
                The role id you want to apply the config for.
            key_name:
                The name of the global config key.
            string_value:
                The value to be set for the config.
            value_type:
                The type of the value to be set for the config.

        Returns:
            List[ConfigItem]: List of role configurations.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.configuration_api.set_role_configuration(
                    key_name=key_name,
                    role_id=role_id,
                    user_configuration_item=rest.UserConfigurationItem(
                        key_name=key_name,
                        string_value=string_value,
                        value_type=value_type,
                    ),
                    _headers=header,
                )
            )
        return [ConfigItem(**c.to_dict()) for c in response]

    async def list_role_configurations(self, role_id: str) -> List[ConfigItem]:
        """Lists role configurations for a given role.
        Args:
            role_id:
                The role id to get configurations for.

        Returns:
            List[ConfigItem]: List of role configurations.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.configuration_api.list_role_configurations(
                    role_id=role_id,
                    _headers=header,
                )
            )
        return [ConfigItem(**c.to_dict()) for c in response]

    async def bulk_delete_role_configurations(
        self, role_id: str, keys: List[str]
    ) -> List[ConfigItem]:
        """Delete role configuration items for a given role.
        Args:
            role_id:
                The role id to delete configurations for.
            keys:
                List of configuration keys to delete.

        Returns:
            List[ConfigItem]: List of remaining role configurations.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.configuration_api.delete_role_configurations(
                    key_names=keys,
                    role_id=role_id,
                    _headers=header,
                )
            )
        return [ConfigItem(**c.to_dict()) for c in response]

    async def delete_multiple_agent_directories(
        self, chat_session_ids: List[str], dir_types: List[str]
    ) -> bool:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_result(
                _rest_to_client_exceptions(
                    rest_client.chat_api.delete_agent_server_directories(
                        session_ids=chat_session_ids,
                        dir_types=dir_types,
                        _headers=header,
                    )
                )
            )
        return result.status == "completed"

    async def get_all_directory_stats(
        self, chat_session_id: str, detail_level: int = 0
    ) -> dict:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.chat_api.list_all_agent_server_directories_stats(
                    session_id=chat_session_id,
                    detail_level=detail_level,
                    _headers=header,
                )
            )
        return {d.id: d.to_dict() for d in response}

    async def get_directory_stats(
        self, directory_name: str, chat_session_id: str, detail_level: int = 0
    ) -> dict:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.chat_api.get_agent_server_directory_stats(
                    session_id=chat_session_id,
                    detail_level=detail_level,
                    directory_name=directory_name,
                    _headers=header,
                )
            )
        return response.to_dict()

    async def get_h2ogpt_system_stats(self) -> dict:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.system_api.get_h2ogpt_system_info(_headers=header)
            )
        return response.to_dict()

    async def create_api_key_for_user(
        self,
        user_id: str,
        name: Optional[str] = None,
        collection_id: Optional[str] = None,
        expires_in: Optional[str] = None,
    ) -> str:
        """Allows admins to create a new api key for a specific user and optionally make it specific to a collection.
        Args:
            user_id:
                String: The id of the user the API key is for.
            name:
                (Optional) String: The name of the API key.
            collection_id:
                (Optional) String: The id of the specific collection.
            expires_in:
                (Optional) String: The expiration for the API key as an interval. Ex. "30 days" or "30 minutes"

        Returns:
            String: The id of the API key.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.api_keys_api.create_api_key_for_user(
                    api_key_create_request=rest.APIKeyCreateRequest(
                        user_id=user_id,
                        name=name,
                        collection_id=collection_id,
                        expires_in=expires_in,
                    ),
                    _headers=header,
                )
            )

        return response.secret_key

    async def deactivate_api_key(self, api_key_id: str) -> Result:
        """Allows admins to deactivate an API key.

        Note: You cannot undo this action.

        Args:
            api_key_id:
                String: The id of the API key.

        Returns:
            Result: Status of the deactivate request.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_result(
                _rest_to_client_exceptions(
                    rest_client.api_keys_api.deactivate_api_key(
                        key_id=api_key_id,
                        _headers=header,
                    )
                )
            )
        return result

    async def list_all_api_keys(
        self, offset: int, limit: int, key_filter: str = ""
    ) -> List[APIKey]:
        """Allows admins to list all the API keys that exist.

        Args:
            offset:
                Int: How many keys to skip before returning.
            limit:
                Int: How many keys to return.
            key_filter:
                String: Only returns keys for usernames matching this filter.

        Returns:
            List[APIKey]: List of APIKeys with metadata about each key.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.api_keys_api.list_all_api_keys(
                    offset=offset,
                    limit=limit,
                    filter=key_filter,
                    _headers=header,
                )
            )
        return [APIKey(**k.to_dict()) for k in response]

    async def set_api_key_expiration(
        self, api_key_id: str, expires_in: Optional[str] = None
    ) -> Result:
        """Allows admins to set an expiration on an API key.

        Args:
            api_key_id:
                String: The id of the API key.
            expires_in:
                (Optional) String: The expiration for the API key as an interval or None (to remove an expiration that was previously set). Ex. "30 days" or "30 minutes"

        Returns:
            Result: Status of the expiration request.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_result(
                _rest_to_client_exceptions(
                    rest_client.api_keys_api.update_api_key_expiry(
                        key_id=api_key_id,
                        api_key_update_expiry_request=rest.APIKeyUpdateExpiryRequest(
                            expires_in=expires_in
                        ),
                        _headers=header,
                    )
                )
            )
        return result

    async def delete_api_keys(self, api_key_ids: List[str]) -> Result:
        """Allows admins to delete API keys.

        Args:
            api_key_ids:
                List[str]: The API keys to delete.

        Returns:
            Result: Status of the delete request.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            for api_key_id in api_key_ids:
                await _rest_to_client_exceptions(
                    rest_client.api_keys_api.delete_api_key(
                        key_id=api_key_id,
                        _headers=header,
                    )
                )
        return Result(status="completed")

    async def get_agent_server_files(self, chat_session_id: str) -> List[dict]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.chat_api.list_agent_server_files(
                    session_id=chat_session_id,
                    _headers=header,
                )
            )
        return [f.to_dict() for f in response]

    async def delete_agent_server_files(self, chat_session_id: str) -> bool:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            result = await _get_result(
                _rest_to_client_exceptions(
                    rest_client.chat_api.delete_agent_server_files(
                        session_id=chat_session_id,
                        _headers=header,
                    )
                )
            )
        return result.status == "completed"

    async def get_user_all_agent_directories(
        self, offset: int, limit: int, filter_text: Optional[str]
    ) -> List[dict]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.agent_api.list_agent_directory_stats(
                    offset=offset,
                    limit=limit,
                    filter_text=filter_text,
                    _headers=header,
                )
            )
        result = []
        for agent_session in response:
            stats = {s.id: s.to_dict() for s in agent_session.stats}
            stats["chat_preview"] = agent_session.chat_preview
            result.append({agent_session.agent_chat_session_id: stats})
        return result

    async def get_agent_tool_preference(self) -> List[str]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.agent_api.list_agent_tool_preference(_headers=header)
            )
        return response

    async def update_agent_tool_preference(self, reference_value: List[str]) -> None:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.agent_api.update_agent_tool_preference(
                    update_agent_tool_preference_request=rest.UpdateAgentToolPreferenceRequest(
                        reference_value=reference_value,
                    ),
                    _headers=header,
                )
            )

    async def delete_agent_tool_preference(self) -> None:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.agent_api.delete_agent_tool_preference(_headers=header)
            )

    async def add_agent_key(self, agent_keys: List[dict]) -> List[dict]:
        result = []
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            for agent_key in agent_keys:
                try:
                    request = rest.CreateAgentKeyRequest(
                        name=agent_key["name"],
                        value=agent_key["value"],
                        type=agent_key["key_type"],
                        description=agent_key.get("description"),
                    )
                    agent_key = await _rest_to_client_exceptions(
                        rest_client.agent_api.create_agent_key(
                            create_agent_key_request=request, _headers=header
                        )
                    )
                    result.append({"agent_key_id": agent_key.id})
                except FailedError as e:
                    print(f"Failed to create the key '{agent_key}': {e}")
        return result

    async def get_agent_keys(self) -> List[dict]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.agent_api.list_agent_keys(_headers=header)
            )
        return [k.to_dict() for k in response]

    async def update_agent_key(
        self,
        key_id: str,
        name: Optional[str] = None,
        value: Optional[str] = None,
        key_type: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[dict]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            try:
                request = rest.UpdateAgentKeyRequest(
                    name=name, value=value, type=key_type, description=description
                )
                agent_key = await _rest_to_client_exceptions(
                    rest_client.agent_api.update_agent_key(
                        key_id=key_id, update_agent_key_request=request, _headers=header
                    )
                )
                return agent_key.to_dict()
            except FailedError as e:
                print(f"Failed to update the key with id '{key_id}': {e}")
                return None

    async def delete_agent_keys(self, key_ids: List[str]) -> None:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            await _rest_to_client_exceptions(
                rest_client.agent_api.delete_agent_keys(
                    key_ids=key_ids,
                    _headers=header,
                )
            )

    async def assign_agent_key_for_tool(
        self, tool_dict_list: List[dict]
    ) -> Optional[List[Tuple]]:
        result = []
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            for association in tool_dict_list:
                request = rest.CreateAgentToolKeyAssociationsRequest.from_dict(
                    association["tool_dict"]
                )
                response = await _rest_to_client_exceptions(
                    rest_client.agent_api.create_agent_key_tool_associations(
                        create_agent_tool_key_associations_request=request,
                        _headers=header,
                    )
                )
                for key in response.keys:
                    result.append(
                        (
                            key.associate_id,
                            response.tool,
                            key.name,
                            key.key_id,
                            key.user_id,
                        )
                    )
        return result

    async def get_agent_key_tool_associations(self) -> List[dict]:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.agent_api.list_agent_key_tool_associations(_headers=header)
            )
        return [r.to_dict() for r in response]

    async def delete_agent_tool_association(self, associate_ids: List[str]) -> int:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.agent_api.delete_agent_tool_association(
                    associate_ids=associate_ids,
                    _headers=header,
                )
            )
        return response.count

    async def add_custom_agent_tool(
        self, tool_type: str, tool_args: dict, custom_tool_path: Optional[str] = None
    ) -> list:
        header = await self._get_auth_header()
        custom_tool_path = str(custom_tool_path) if custom_tool_path else None
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.agent_api.add_custom_agent_tool(
                    file=custom_tool_path,
                    tool_type=tool_type,
                    tool_args=json.dumps(tool_args),
                    custom_tool_path=custom_tool_path,
                    filename=os.path.basename(custom_tool_path)
                    if custom_tool_path
                    else None,
                    _headers=header,
                )
            )
        return [obj.agent_custom_tool_id for obj in response]

    async def delete_custom_agent_tool(self, tool_ids: List[str]) -> int:
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.agent_api.delete_custom_agent_tool(
                    tool_ids=tool_ids,
                    _headers=header,
                )
            )
        return response.count

    async def update_custom_agent_tool(
        self,
        tool_id: str,
        tool_args: dict,
    ) -> str:
        """Updates a custom agent tool's arguments.

        Args:
            tool_id: The ID of the tool to update
            tool_args: New tool arguments

        Returns:
            The updated tool ID
        """
        header = await self._get_auth_header()

        # Build request body with only tool_args
        request_obj = rest.UpdateCustomAgentToolRequest(tool_args=tool_args)

        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.agent_api.update_custom_agent_tool(
                    tool_id=tool_id,
                    update_custom_agent_tool_request=request_obj,
                    _headers=header,
                )
            )
        return response.agent_custom_tool_id

    async def get_custom_agent_tools(self) -> List[dict]:
        """Gets all custom agent tools for the current user.

        Returns:
            List[dict]: A list of custom agent tools with their details.
                Each tool contains: id, tool_name, tool_type, tool_args, owner_email
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.agent_api.list_custom_agent_tools(_headers=header)
            )
        return response

    async def set_role_priority(self, role_id: str, priority: int) -> UserRole:
        """Sets the priority for a role.
        Args:
            role_id:
                String: The id of the role to set the priority for.
            priority:
                Int: The priority value to set for the role. ex: 100, 200, 300...etc.
                The lower the number, the higher the priority.
        Returns:
            UserRole: The updated user role with the new priority.
        """
        header = await self._get_auth_header()
        async with self._RESTClient(self) as rest_client:
            response = await _rest_to_client_exceptions(
                rest_client.permission_api.set_role_priority(
                    role_id=role_id,
                    set_role_priority_request=rest.SetRolePriorityRequest(
                        priority=priority
                    ),
                    _headers=header,
                )
            )
        return UserRole(**response.to_dict())

    # ----------------------------------------------------------------------------------
    # Private
    # ----------------------------------------------------------------------------------

    async def _check_version(self, strict: bool):
        from h2ogpte import __version__ as client_version

        server_version = (await self.get_meta()).version
        server_version = server_version.lstrip("v")

        if server_version != client_version:
            msg = (
                f"Server version {server_version} doesn't match client "
                f"version {client_version}, unexpected errors may occur.\n"
                f"Please install the correct version of H2OGPTE "
                f"with `pip install h2ogpte=={server_version}`."
            )
            if strict:
                raise RuntimeError(msg)
            else:
                print(
                    f"Warning: {msg}\n"
                    "You can enable strict version checking by passing "
                    "strict_version_check=True."
                )

    async def _get(self, endpoint: str, as_json: bool = True) -> Any:
        headers = await self._get_auth_header()
        res = await self._client.get(
            self._address + endpoint,
            timeout=H2OGPTEAsync.TIMEOUT,
            headers=headers,
        )
        self._raise_error_if_any(res)
        if as_json:
            try:
                return res.json()
            except:
                return res
        return res

    async def _put(self, endpoint: str, files) -> Any:
        headers = await self._get_auth_header()
        res = await self._client.put(
            self._address + endpoint,
            files=files,
            headers=headers,
        )
        return res

    async def _post(self, endpoint: str, data: Any) -> Any:
        headers = await self._get_auth_header()
        headers["Content-Type"] = "application/json"
        content = json.dumps(data, allow_nan=False, separators=(",", ":"))
        res = await self._client.post(
            self._address + endpoint,
            content=content,
            timeout=H2OGPTEAsync.TIMEOUT,
            headers=headers,
        )
        self._raise_error_if_any(res)
        return res.json()

    async def _delete(self, endpoint: str) -> Any:
        headers = await self._get_auth_header()
        res = await self._client.delete(
            self._address + endpoint,
            timeout=H2OGPTEAsync.TIMEOUT,
            headers=headers,
        )
        self._raise_error_if_any(res)
        return res.json()

    async def _job(self, method: str, **kwargs: Any) -> Any:
        request_id = str(uuid.uuid4())
        return await self._post("/rpc/job", [method, kwargs, request_id])

    async def _wait_for_completion(
        self, job_id: str, timeout: Optional[float] = None
    ) -> Job:
        if timeout is None:
            timeout = 86400
        dt = H2OGPTEAsync.INITIAL_WAIT_INTERVAL
        last_job: Optional[Job] = None
        while True:
            job = await self.get_job(job_id)
            if job.completed or job.canceled:
                # will reach here if processing times out (self cancels since quit is set to 1)
                break
            if last_job is not None and last_job.progress == job.progress:
                if job.start_time and time.time() > job.start_time + timeout:
                    raise TimeoutError(
                        f"Job {job.kind} ({job_id}) timed out after {timeout} seconds"
                    )
            else:
                last_job = job
            await asyncio.sleep(dt)
            dt = min(
                H2OGPTEAsync.MAX_WAIT_INTERVAL, dt * H2OGPTEAsync.WAIT_BACKOFF_FACTOR
            )
        return job

    def _raise_error_if_any(self, res: httpx.Response) -> None:
        if res.status_code == 200:
            return
        error: ErrorResponse
        try:
            error = res.json()
        except:
            error = {"error": res.content.decode(errors="replace")}

        self._http_code_to_error(res.status_code, error)

    @staticmethod
    def _http_code_to_error(http_code, error) -> None:
        if http_code == 200:
            return
        if http_code == 400:
            raise InvalidArgumentError(error)
        elif http_code == 401:
            raise UnauthorizedError(error)
        elif http_code == 404:
            raise ObjectNotFoundError(error)
        elif http_code == 500:
            raise InternalServerError(error)
        elif http_code == 501:
            raise NotImplementedError(error)
        else:
            raise HTTPError(error, http_code)


def _to_id(data: Any) -> str:
    return Identifier(**data).id


async def _get_share_permission_status(coroutine) -> ShareResponseStatus:
    try:
        await coroutine
        return ShareResponseStatus(status="completed")
    except rest.exceptions.ApiException as e:
        if e.status == 409:
            return ShareResponseStatus(status="failed")
        raise e


async def _get_result(coroutine) -> Result:
    try:
        await coroutine
        return Result(status="completed")
    except rest.exceptions.ApiException as e:
        if e.status == 409:
            return Result(status="failed")
        raise e


async def _rest_to_client_exceptions(coroutine) -> Any:
    try:
        return await coroutine
    except rest.exceptions.BadRequestException as e:
        raise InvalidArgumentError(_convert_error_message(e))
    except rest.exceptions.UnauthorizedException as e:
        raise UnauthorizedError(_convert_error_message(e))
    except rest.exceptions.ForbiddenException as e:
        raise UnauthorizedError(_convert_error_message(e))
    except rest.exceptions.NotFoundException as e:
        raise ObjectNotFoundError(_convert_error_message(e))
    except rest.exceptions.ServiceException as e:
        if e.status == 500:
            raise InternalServerError(_convert_error_message(e))
        else:
            raise HTTPError(_convert_error_message(e), e.status)
    except rest.exceptions.ApiException as e:
        if e.status == 409:
            raise FailedError(_convert_error_message(e))
        raise HTTPError(_convert_error_message(e), e.status)


def _convert_error_message(exception: rest.exceptions.ApiException) -> "ErrorResponse":
    error = json.loads(exception.body)
    return {"error": error["message"]}


def _convert_rest_job(job: rest.JobDetails) -> Job:
    job_dict = job.to_dict()
    job_dict["passed"] = job_dict["passed_percentage"]
    job_dict["failed"] = job_dict["failed_percentage"]
    job_dict["date"] = job_dict["created_at"]
    job_dict["last_update_date"] = job_dict["updated_at"]
    job_dict["completed"] = job_dict["overall_status"] in ["failed", "completed"]
    job_dict["canceled"] = job_dict["overall_status"] == "canceled"

    return Job(**job_dict)


def unmarshal(s: str):
    return json.loads(s)


def unmarshal_dict(d, include_layout=False):
    if d and type(d) == dict:
        if not include_layout:
            if "page_layout_dict" in d:
                del d["page_layout_dict"]
        # keys in DB that are stored as string, but must be dicts in Python
        for k, default in [
            # collection settings is not nullable
            ("chat_settings", "{}"),
            ("collection_settings", "{}"),
            ("guardrails_settings", "null"),
            # meta_data_dict default is empty dict since can append more values when re-importing an existing document
            ("meta_data_dict", "{}"),
            ("user_source_file", "null"),
            ("page_ocr_model_dict", "null"),
            ("page_layout_dict", "null"),
        ]:
            d[k] = unmarshal(d.get(k, default) or default)
