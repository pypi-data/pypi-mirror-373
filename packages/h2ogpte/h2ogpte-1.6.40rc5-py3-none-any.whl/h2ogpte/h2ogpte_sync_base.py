import json
import requests
import uuid
import time
from typing import Any, Union, Dict, Optional, Callable
from h2o_authn import TokenProvider

from h2ogpte.errors import (
    ErrorResponse,
    HTTPError,
    InternalServerError,
    InvalidArgumentError,
    ObjectNotFoundError,
    UnauthorizedError,
    NotImplementedError,
)
from h2ogpte.types import SessionError, Identifier, Result, ShareResponseStatus, Job
from h2ogpte.session import Session
from h2ogpte import rest_sync as rest
from h2ogpte.h2ogpte_async import H2OGPTEAsync


class H2OGPTESyncBase:
    # Timeout for HTTP requests
    TIMEOUT = 3600.0

    def __init__(
        self,
        address: str,
        api_key: Optional[str] = None,
        token_provider: Optional[TokenProvider] = None,
        verify: Union[bool, str] = True,
        strict_version_check: bool = False,
    ):
        """Create a new H2OGPTE client.

        Args:
            address:
                Full URL of the h2oGPTe server to connect to, e.g. "https://h2ogpte.h2o.ai".
            api_key:
                API key for authentication to the h2oGPTe server. Users can generate
                a key by accessing the UI and navigating to the Settings.
            token_provider:
                User's token provider.
            verify:
                Whether to verify the server's TLS/SSL certificate.
                Can be a boolean or a path to a CA bundle.
                Defaults to True.
            strict_version_check:
                Indicate whether a version check should be enforced.

        Returns:
            A new H2OGPTE client.
        """
        # Remove trailing slash from address, if any
        address = address.rstrip("/ ")

        self._address = address
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

        self._check_version(strict_version_check)
        verify = self._verify if isinstance(self._verify, str) else None
        configuration = rest.Configuration(
            host=self._address + "/api/v1", ssl_ca_cert=verify
        )
        if self._verify in [False]:
            configuration.verify_ssl = False
        self._rest_client = rest.ApiClient(configuration)
        self._collection_api = rest.CollectionsApi(self._rest_client)
        self._document_api = rest.DocumentsApi(self._rest_client)
        self._model_api = rest.ModelsApi(self._rest_client)
        self._chat_api = rest.ChatApi(self._rest_client)
        self._tag_api = rest.TagsApi(self._rest_client)
        self._prompt_template_api = rest.PromptTemplatesApi(self._rest_client)
        self._ingestion_api = rest.DocumentIngestionApi(self._rest_client)
        self._job_api = rest.JobsApi(self._rest_client)
        self._model_api = rest.ModelsApi(self._rest_client)
        self._system_api = rest.SystemApi(self._rest_client)
        self._permission_api = rest.PermissionsApi(self._rest_client)
        self._api_keys_api = rest.APIKeysApi(self._rest_client)
        self._configuration_api = rest.ConfigurationsApi(self._rest_client)
        self._agent_api = rest.AgentsApi(self._rest_client)
        self._secrets_api = rest.SecretsApi(self._rest_client)

    class _RESTClient:
        def __init__(self, h2ogpte):
            self.collection_api = h2ogpte._collection_api
            self.document_api = h2ogpte._document_api
            self.model_api = h2ogpte._model_api
            self.chat_api = h2ogpte._chat_api
            self.tag_api = h2ogpte._tag_api
            self.prompt_template_api = h2ogpte._prompt_template_api
            self.ingestion_api = h2ogpte._ingestion_api
            self.job_api = h2ogpte._job_api
            self.model_api = h2ogpte._model_api
            self.system_api = h2ogpte._system_api
            self.permission_api = h2ogpte._permission_api
            self.api_keys_api = h2ogpte._api_keys_api
            self.configuration_api = h2ogpte._configuration_api
            self.agent_api = h2ogpte._agent_api
            self.secrets_api = h2ogpte._secrets_api

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    def _get_auth_header(self) -> Dict:
        if self._api_key is not None:
            return {
                "Authorization": f"Bearer {self._api_key}",
            }
        elif self._token_provider is not None:
            token = self._token_provider.token()
            return {
                "Authorization": f"Bearer-Token {token}",
                "Session-Id": self._session_id,
            }
        else:
            raise Exception(
                "Please provide either an api_key or a token_provider to authenticate."
            )

    def _check_version(self, strict_version_check: bool):
        from h2ogpte import __version__ as client_version

        server_version = self.get_meta().version
        if client_version.count(".") == 3:
            client_version = client_version[: client_version.rfind(".")]
        if server_version.count(".") == 3:
            server_version = server_version[: server_version.rfind(".")]

        if server_version[0] == "v":
            server_version = server_version[1:]

        if server_version != client_version:
            msg = (
                f"Warning: Server version {server_version} doesn't match client "
                f"version {client_version}: unexpected errors may occur.\n"
                f"Please install the correct version of H2OGPTE "
                f"with `pip install h2ogpte=={server_version}`."
            )
            if strict_version_check:
                raise RuntimeError(msg)
            else:
                print(msg)
                print(
                    "You can enable strict version checking by passing strict_version_check=True."
                )

    def _post(self, slug: str, data: Any):
        res = requests.post(
            f"{self._address}{slug}",
            data=data,
            headers={**self._get_auth_header(), **{"Content-Type": "application/json"}},
            verify=self._verify,
            timeout=H2OGPTESyncBase.TIMEOUT,
        )
        self._raise_error_if_any(res)
        return res.json()

    def _get(self, slug: str, as_json=True):
        res = requests.get(
            f"{self._address}{slug}",
            headers={**self._get_auth_header()},
            verify=self._verify,
            timeout=H2OGPTESyncBase.TIMEOUT,
        )
        self._raise_error_if_any(res)
        if as_json:
            try:
                return res.json()
            except:
                return res
        return res

    def _put(self, endpoint: str, files) -> Any:
        res = requests.put(
            self._address + endpoint,
            headers={**self._get_auth_header()},
            files=files,
            verify=self._verify,
            timeout=H2OGPTESyncBase.TIMEOUT * 2,
        )
        return res

    def _delete(self, slug: str):
        res = requests.delete(
            f"{self._address}{slug}",
            headers={**self._get_auth_header()},
            verify=self._verify,
            timeout=H2OGPTESyncBase.TIMEOUT,
        )
        self._raise_error_if_any(res)
        return res.json()

    def _post_stream(self, slug: str, data: Any, custom_headers: dict = None):
        headers = {
            **self._get_auth_header(),
            "Content-Type": "application/json",
            **(custom_headers or {}),
        }
        res = requests.post(
            f"{self._address}{slug}",
            data=data,
            headers=headers,
            verify=self._verify,
            timeout=H2OGPTESyncBase.TIMEOUT,
            stream=True,
        )
        res.raise_for_status()
        return res

    def _raise_error_if_any(self, res: requests.Response) -> None:
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

    def _db(self, method: str, *args: Any) -> Any:
        return self._post("/rpc/db", marshal([method, *args]))

    def _job(self, method: str, **kwargs: Any) -> Any:
        request_id = str(uuid.uuid4())
        return self._post("/rpc/job", marshal([method, kwargs, request_id]))

    def _lang(self, method: str, **kwargs: Any) -> Any:
        res = self._post("/rpc/lang", marshal(dict(method=method, params=kwargs)))
        ret = res["result"]
        if isinstance(ret, dict) and ret.get("error"):
            raise SessionError(ret["error"])
        return ret

    def _vex(self, method: str, collection_id: str, **kwargs: Any) -> Any:
        return self._post(
            "/rpc/vex",
            marshal(dict(method=method, collection_id=collection_id, params=kwargs)),
        )

    def _crawl_func(self, name: str, **kwargs: Any) -> Any:
        response = self._post("/rpc/crawl/func", marshal([name, kwargs]))
        return response

    def _wait_for_completion(self, job_id: str, timeout: Optional[float] = None) -> Job:
        if timeout is None:
            timeout = 86400
        dt = H2OGPTEAsync.INITIAL_WAIT_INTERVAL
        last_job: Optional[Job] = None
        while True:
            job = self.get_job(job_id)
            if job.completed or job.canceled:
                break
            if last_job is not None and last_job.progress == job.progress:
                if job.start_time and time.time() > job.start_time + timeout:
                    raise TimeoutError(
                        f"Job {job.kind} ({job_id}) timed out after {timeout} seconds"
                    )
            else:
                last_job = job
            time.sleep(dt)
            dt = min(
                H2OGPTEAsync.MAX_WAIT_INTERVAL, dt * H2OGPTEAsync.WAIT_BACKOFF_FACTOR
            )
        return job

    def connect(
        self,
        chat_session_id: str,
        prompt_template_id: Optional[str] = None,
        open_timeout: int = 10,
        close_timeout: int = 10,
        max_connect_retries: int = 10,
        connect_retry_delay: int = 0.5,
        connect_retry_max_delay: int = 60,
    ) -> Session:
        """Create and participate in a chat session.

        This is a live connection to the H2OGPTE server contained to a specific
        chat session on top of a single collection of documents. Users will find all
        questions and responses in this session in a single chat history in the
        UI.

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
        return Session(
            self._address,
            client=self,
            chat_session_id=chat_session_id,
            prompt_template_id=prompt_template_id,
            open_timeout=open_timeout,
            close_timeout=close_timeout,
            max_connect_retries=max_connect_retries,
            connect_retry_delay=connect_retry_delay,
            connect_retry_max_delay=connect_retry_max_delay,
        )


def _to_id(data: Dict[str, Any]) -> str:
    if data is not None and isinstance(data, dict) and data.get("error", ""):
        raise ValueError(data.get("error", ""))
    return Identifier(**data).id


def _get_result(func: Callable) -> Result:
    try:
        func()
        return Result(status="completed")
    except rest.exceptions.ApiException as e:
        if e.status == 409:
            return Result(status="failed")
        raise e


def _rest_to_client_exceptions(func: Callable) -> Any:
    try:
        return func()
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
        raise HTTPError(_convert_error_message(e), e.status)


def _convert_error_message(exception: rest.exceptions.ApiException) -> "ErrorResponse":
    error = json.loads(exception.body)
    return {"error": error["message"]}


def _get_share_permission_status(func: Callable) -> ShareResponseStatus:
    try:
        func()
        return ShareResponseStatus(status="completed")
    except rest.exceptions.ApiException as e:
        if e.status == 409:
            return ShareResponseStatus(status="failed")
        raise e


def marshal(d):
    return json.dumps(d, allow_nan=False, separators=(",", ":"))
