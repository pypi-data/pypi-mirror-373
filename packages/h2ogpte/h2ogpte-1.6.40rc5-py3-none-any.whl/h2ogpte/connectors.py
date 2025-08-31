import base64
import os
from typing import Union, List, Dict, Any


def create_ingest_job_from_cloud_storage(
    h2ogpte_client,
    collection_id: str,
    storage_type: str,
    url: Union[str, List[str]],
    credentials: Dict[str, Union[str, None]],
    gen_doc_summaries: bool,
    gen_doc_questions: bool,
    audio_input_language: str,
    ocr_model: Union[str, None],
    tesseract_lang: Union[str, None],
    keep_tables_as_one_chunk: Union[bool, None],
    chunk_by_page: Union[bool, None],
    handwriting_check: Union[bool, None],
    ingest_mode: Union[str, None],
    metadata: Union[Dict[str, Any], None] = None,
):
    if url is None:
        raise ValueError("The 'url' argument can't be None.")
    elif isinstance(url, str):
        url = [
            url,
        ]

    return h2ogpte_client._job(
        "crawl.IngestFromCloudStorageJob",
        collection_id=collection_id,
        storage_type=storage_type,
        urls=url,
        credentials=credentials,
        gen_doc_summaries=gen_doc_summaries,
        gen_doc_questions=gen_doc_questions,
        audio_input_language=audio_input_language,
        ocr_model=ocr_model,
        tesseract_lang=tesseract_lang,
        keep_tables_as_one_chunk=keep_tables_as_one_chunk,
        chunk_by_page=chunk_by_page,
        handwriting_check=handwriting_check,
        ingest_mode=ingest_mode,
        metadata=metadata,
    )


class S3Credential:
    def __init__(
        self,
        access_key_id: str,
        secret_access_key: str,
        session_token: str = None,
        role_arn: str = None,
    ):
        """
        Creates an object with S3 credentials.
        :param access_key_id: Access Key ID
        :param secret_access_key: Secret Access Key
        :param session_token: Session Token (optional)
        :param role_arn: Role providing access to the S3 storage
        """
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.session_token = session_token
        self.role_arn = role_arn


def create_ingest_job_from_s3(
    h2ogpte_client,
    collection_id: str,
    url: Union[str, List[str]],
    region: str,
    credentials: Union[S3Credential, None],
    gen_doc_summaries: bool,
    gen_doc_questions: bool,
    audio_input_language: str,
    ocr_model: Union[str, None],
    tesseract_lang: Union[str, None],
    keep_tables_as_one_chunk: Union[bool, None],
    chunk_by_page: Union[bool, None],
    handwriting_check: Union[bool, None],
    ingest_mode: Union[str, None],
    metadata: Union[Dict[str, Any], None] = None,
):
    if credentials is None:
        credentials_dict = {}
    else:
        credentials_dict = credentials.__dict__

    credentials_dict["region"] = region

    job = create_ingest_job_from_cloud_storage(
        h2ogpte_client=h2ogpte_client,
        collection_id=collection_id,
        storage_type="s3",
        url=url,
        credentials=credentials_dict,
        gen_doc_summaries=gen_doc_summaries,
        gen_doc_questions=gen_doc_questions,
        audio_input_language=audio_input_language,
        ocr_model=ocr_model,
        tesseract_lang=tesseract_lang,
        keep_tables_as_one_chunk=keep_tables_as_one_chunk,
        chunk_by_page=chunk_by_page,
        handwriting_check=handwriting_check,
        ingest_mode=ingest_mode,
        metadata=metadata,
    )
    return job


class GCSServiceAccountCredential:
    def __init__(self, path_to_json_key_file: str):
        """
        Creates an object with Google Cloud credentials for a service account.
        :param path_to_json_key_file: A local path to a file containing a service account JSON key.
        """
        self.path_to_json_key_file = path_to_json_key_file

    def _file_check(self):
        if not self.path_to_json_key_file or not os.path.isfile(
            self.path_to_json_key_file
        ):
            raise ValueError(
                f"The path '{self.path_to_json_key_file}' that should point to a JSON key doesn't exist."
            )

    def load_key_as_string(self):
        self._file_check()
        with open(self.path_to_json_key_file, "r") as file:
            return file.read()

    def load_key(self):
        self._file_check()
        with open(self.path_to_json_key_file, "rb") as file:
            key = file.read()
            encoded = base64.b64encode(key).decode("ascii")
            return {
                "service_account_key": encoded,
            }


def create_ingest_job_from_gcs(
    h2ogpte_client,
    collection_id: str,
    url: Union[str, List[str]],
    credentials: Union[GCSServiceAccountCredential, None],
    gen_doc_summaries: bool,
    gen_doc_questions: bool,
    audio_input_language: str,
    ocr_model: Union[str, None],
    tesseract_lang: Union[str, None],
    keep_tables_as_one_chunk: Union[bool, None],
    chunk_by_page: Union[bool, None],
    handwriting_check: Union[bool, None],
    ingest_mode: Union[str, None],
    metadata: Union[Dict[str, Any], None] = None,
):
    if credentials is None:
        credentials_dict = {}
    else:
        credentials_dict = credentials.load_key()

    job = create_ingest_job_from_cloud_storage(
        h2ogpte_client=h2ogpte_client,
        collection_id=collection_id,
        storage_type="gcs",
        url=url,
        credentials=credentials_dict,
        gen_doc_summaries=gen_doc_summaries,
        gen_doc_questions=gen_doc_questions,
        audio_input_language=audio_input_language,
        ocr_model=ocr_model,
        tesseract_lang=tesseract_lang,
        keep_tables_as_one_chunk=keep_tables_as_one_chunk,
        chunk_by_page=chunk_by_page,
        handwriting_check=handwriting_check,
        ingest_mode=ingest_mode,
        metadata=metadata,
    )
    return job


class AzureKeyCredential:
    def __init__(self, account_key: str):
        """
        Creates an object with Azure credentials.
        :param account_key: Access key of a storage account
        """
        self.account_key = account_key


class AzureSASCredential:
    def __init__(self, sas_token: str):
        """
        Creates an object with Azure credentials.
        :param sas_token: Shared Access Signature token
        """
        self.sas_token = sas_token


def create_ingest_job_from_azure_blob_storage(
    h2ogpte_client,
    collection_id: str,
    container: str,
    path: Union[str, List[str]],
    account_name: str,
    credentials: Union[AzureKeyCredential, AzureSASCredential, None],
    gen_doc_summaries: bool,
    gen_doc_questions: bool,
    audio_input_language: str,
    ocr_model: Union[str, None],
    tesseract_lang: Union[str, None],
    keep_tables_as_one_chunk: Union[bool, None],
    chunk_by_page: Union[bool, None],
    handwriting_check: Union[bool, None],
    ingest_mode: Union[str, None],
    metadata: Union[Dict[str, Any], None] = None,
):
    if credentials is None:
        credentials_dict = {}
    else:
        credentials_dict = credentials.__dict__

    credentials_dict["container"] = container
    credentials_dict["account_name"] = account_name

    job = create_ingest_job_from_cloud_storage(
        h2ogpte_client=h2ogpte_client,
        collection_id=collection_id,
        storage_type="azure_blob",
        url=path,
        credentials=credentials_dict,
        gen_doc_summaries=gen_doc_summaries,
        gen_doc_questions=gen_doc_questions,
        audio_input_language=audio_input_language,
        ocr_model=ocr_model,
        tesseract_lang=tesseract_lang,
        keep_tables_as_one_chunk=keep_tables_as_one_chunk,
        chunk_by_page=chunk_by_page,
        handwriting_check=handwriting_check,
        ingest_mode=ingest_mode,
        metadata=metadata,
    )
    return job
