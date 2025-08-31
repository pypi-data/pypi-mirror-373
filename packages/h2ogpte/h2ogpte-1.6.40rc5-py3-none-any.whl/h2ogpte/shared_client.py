"""
Standalone per-session websocket client for h2oGPTe.

This module provides a thread-safe websocket client that creates one dedicated
websocket connection per chat session, ensuring proper message isolation and
avoiding routing issues between different sessions.

Usage:
    from h2ogpte.shared_client import SharedH2OGPTEClient

    client = SharedH2OGPTEClient(
        address="https://your-h2ogpte-server.com",
        api_key="your-api-key"
    )

    # Each unique session_id gets its own websocket connection
    response = client.query(
        session_id="session-1",
        message="Your question here",
        system_prompt="Your system prompt",
        llm="your-llm-model",
        timeout=600
    )

    # Different session uses a separate websocket connection
    response2 = client.query(
        session_id="session-2",
        message="Another question",
        timeout=600
    )

    # Close specific session when done
    client.close_session("session-1")
"""

import json
import ssl
import sys
import threading
import uuid
import warnings
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, Optional, Union, List
from urllib.parse import urlparse

from websockets.exceptions import (
    ConnectionClosed,
    ConnectionClosedOK,
    ConnectionClosedError,
)
from websockets.sync.client import connect as ws_connect, ClientConnection
from websockets.uri import parse_uri

from h2ogpte.session import ChatRequest, ChatMessage, ChatResponse, ChatAcknowledgement

warnings.filterwarnings("ignore")


class SessionError(Exception):
    pass


class SessionWebsocket:
    def __init__(self, session_id: str, address: str, auth_headers: Dict, ssl_context):
        self.session_id = session_id
        self._connection: Optional[ClientConnection] = None
        self._pending_requests: Dict[str, threading.Event] = {}
        self._responses: Dict[str, Union[ChatMessage, Exception]] = {}
        self._request_ids: Dict[str, str] = {}  # correlation_id -> request_id
        self._connection_lock = threading.Lock()
        self._response_lock = threading.Lock()
        self._receiver_thread: Optional[threading.Thread] = None
        self._running = False
        self._address = address
        self._auth_headers = auth_headers
        self._ssl_context = ssl_context
        self._connect()

    def _connect(self):
        try:
            if self._connection:
                try:
                    self._connection.close()
                except:
                    pass

            session_ws_address = f"{self._address}?currentSessionID={self.session_id}"

            self._connection = ws_connect(
                session_ws_address,
                additional_headers=self._auth_headers,
                ssl_context=self._ssl_context,
                open_timeout=60,
                close_timeout=60,
            )

            self._running = True
            if self._receiver_thread is None or not self._receiver_thread.is_alive():
                self._receiver_thread = threading.Thread(
                    target=self._message_receiver, daemon=True
                )
                self._receiver_thread.start()

        except Exception as e:
            self._running = False
            raise e

    def _message_receiver(self):
        while self._running and self._connection:
            try:
                res = self._connection.recv(timeout=1.0)
                if isinstance(res, str):
                    payloads = res.splitlines()
                    for payload in payloads:
                        self._handle_message(payload)
            except TimeoutError:
                continue
            except (ConnectionClosed, ConnectionClosedError, ConnectionClosedOK):
                self._running = False
                break
            except Exception as e:
                print(
                    f"Error in message receiver for session {self.session_id}: {e}",
                    file=sys.stderr,
                )
                continue

    def _handle_message(self, payload: str):
        try:
            res = deserialize(payload)

            with self._response_lock:
                if res.t == "cx":  # ack
                    correlation_id = res.correlation_id
                    if correlation_id in self._request_ids:
                        self._request_ids[correlation_id] = res.message_id

                elif res.t == "ca":  # response
                    reply_to_id = res.reply_to_id
                    correlation_id = None

                    # Find correlation_id by request_id
                    for cid, rid in self._request_ids.items():
                        if rid == reply_to_id:
                            correlation_id = cid
                            break

                    if correlation_id and correlation_id in self._pending_requests:
                        chat_message = ChatMessage(
                            id=res.message_id,
                            content=res.body,
                            reply_to=res.reply_to_id,
                            votes=0,
                            created_at=datetime.now(),
                            type_list=[],
                        )
                        self._responses[correlation_id] = chat_message
                        self._pending_requests[correlation_id].set()

                elif res.t == "ce":  # error
                    reply_to_id = res.reply_to_id
                    correlation_id = None

                    # Find correlation_id by request_id
                    for cid, rid in self._request_ids.items():
                        if rid == reply_to_id:
                            correlation_id = cid
                            break

                    if correlation_id and correlation_id in self._pending_requests:
                        error = SessionError(f"Remote error: {res.error}")
                        self._responses[correlation_id] = error
                        self._pending_requests[correlation_id].set()

        except Exception as e:
            print(
                f"Error handling message for session {self.session_id}: {e}",
                file=sys.stderr,
            )

    def send_request(self, request: ChatRequest, timeout: float = 1000) -> ChatMessage:
        correlation_id = request.correlation_id

        with self._response_lock:
            if correlation_id in self._pending_requests:
                raise RuntimeError(f"Request {correlation_id} already pending")

            self._pending_requests[correlation_id] = threading.Event()
            self._request_ids[correlation_id] = None

        try:
            with self._connection_lock:
                if not self._connection or not self._running:
                    raise RuntimeError("Connection not established")

                self._connection.send(serialize(request))

            # wait for response
            if not self._pending_requests[correlation_id].wait(timeout=timeout):
                raise TimeoutError(f"Request timed out: {serialize(request)}")

            with self._response_lock:
                response = self._responses.pop(correlation_id, None)
                self._pending_requests.pop(correlation_id, None)
                self._request_ids.pop(correlation_id, None)

            if isinstance(response, Exception):
                raise response
            elif response is None:
                raise RuntimeError("No response received")

            return response

        except Exception as e:
            with self._response_lock:
                self._pending_requests.pop(correlation_id, None)
                self._responses.pop(correlation_id, None)
                self._request_ids.pop(correlation_id, None)
            raise e

    def close(self):
        self._running = False
        if self._connection:
            try:
                self._connection.close()
            except:
                pass
        if self._receiver_thread and self._receiver_thread.is_alive():
            self._receiver_thread.join(timeout=5.0)


class SharedWebsocketManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self._session_sockets: Dict[str, SessionWebsocket] = {}
            self._sessions_lock = threading.Lock()
            self._address = None
            self._auth_headers = None
            self._ssl_context = None
            self.initialized = True

    def setup_connection(self, address: str, auth_headers: Dict, ssl_context):
        self._address = address
        self._auth_headers = auth_headers
        self._ssl_context = ssl_context

    def get_session_socket(self, session_id: str) -> SessionWebsocket:
        with self._sessions_lock:
            if session_id not in self._session_sockets:
                if not self._address or not self._auth_headers:
                    raise RuntimeError(
                        "Connection parameters not set. Call setup_connection first."
                    )
                self._session_sockets[session_id] = SessionWebsocket(
                    session_id, self._address, self._auth_headers, self._ssl_context
                )
            return self._session_sockets[session_id]

    def send_request(self, request: ChatRequest, timeout: float = 1000) -> ChatMessage:
        session_socket = self.get_session_socket(request.session_id)
        return session_socket.send_request(request, timeout)

    def close(self):
        with self._sessions_lock:
            for session_socket in self._session_sockets.values():
                session_socket.close()
            self._session_sockets.clear()

    def close_session(self, session_id: str):
        with self._sessions_lock:
            if session_id in self._session_sockets:
                self._session_sockets[session_id].close()
                del self._session_sockets[session_id]


class SharedH2OGPTEClient:
    def __init__(self, address: str, api_key: str, verify: bool = False):
        self.address = address
        self.api_key = api_key
        self.verify = verify
        self._websocket_manager = None
        self._setup_connection()

    def _setup_connection(self):
        url = urlparse(self.address)
        scheme = "wss" if url.scheme == "https" else "ws"
        ws_address = f"{scheme}://{url.netloc}/ws"

        # Setup SSL context
        wsuri = parse_uri(ws_address)
        if wsuri.secure:
            context = ssl.SSLContext()
            if not self.verify:
                context.verify_mode = ssl.CERT_NONE
        else:
            context = None

        # Setup auth headers
        auth_headers = {"Authorization": f"Bearer {self.api_key}"}

        # Initialize shared websocket manager
        self._websocket_manager = SharedWebsocketManager()
        self._websocket_manager.setup_connection(ws_address, auth_headers, context)

    def query(
        self,
        session_id: str,
        message: str,
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
    ) -> ChatMessage:
        correlation_id = str(uuid.uuid4())
        request = ChatRequest(
            t="cq",
            mode="s",
            session_id=session_id,
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

        for attempt in range(retries + 1):
            try:
                return self._websocket_manager.send_request(request, timeout)
            except Exception as e:
                if attempt == retries:
                    raise e
                print(
                    f"Request failed (attempt {attempt + 1}/{retries + 1}): {e}",
                    file=sys.stderr,
                )
                # Reconnect and retry
                self._setup_connection()

    def close(self):
        """Close the client and cleanup all connections."""
        if self._websocket_manager:
            self._websocket_manager.close()

    def close_session(self, session_id: str):
        """Close the websocket connection for a specific session."""
        if self._websocket_manager:
            self._websocket_manager.close_session(session_id)


def serialize(request: ChatRequest) -> str:
    """Serialize chat request to JSON."""
    return json.dumps(asdict(request), allow_nan=False, separators=(",", ":"))


def deserialize(response: str) -> Union[ChatResponse, ChatAcknowledgement]:
    """Deserialize JSON response to chat object."""
    data = json.loads(response)
    t = data["t"]
    if t == "cx":
        return ChatAcknowledgement(**data)
    elif t in ["ca", "cp", "ce", "cr", "cm"]:
        return ChatResponse(**data)
    else:
        raise SessionError(f"Invalid chat response type: {t}.")


def cleanup_shared_websocket():
    """Cleanup the shared websocket connection."""
    try:
        manager = SharedWebsocketManager()
        manager.close()
    except Exception as e:
        print(f"Warning: Failed to cleanup shared websocket: {e}", file=sys.stderr)
