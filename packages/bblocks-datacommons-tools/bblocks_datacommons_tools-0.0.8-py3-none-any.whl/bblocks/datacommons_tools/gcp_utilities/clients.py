from typing import TypeVar, Type

from google.cloud.run_v2 import JobsClient, ServicesClient
from google.cloud.storage import Client

ClientType = TypeVar("ClientType")


def _build_client(client_cls: Type[ClientType], credentials: dict) -> ClientType:
    if not credentials:
        raise RuntimeError("No credentials available to build Google client")

    if hasattr(client_cls, "from_service_account_info") and isinstance(
        credentials, dict
    ):
        return client_cls.from_service_account_info(credentials)

    return client_cls(credentials=credentials)


def get_gcs_client(credentials: dict) -> Client:
    """Initialize the Google Cloud Storage client."""
    return _build_client(Client, credentials=credentials)


def get_jobs_client(credentials: dict) -> JobsClient:
    """Initialize the Google Cloud Run Jobs client."""
    return _build_client(JobsClient, credentials=credentials)


def get_services_client(credentials: dict) -> ServicesClient:
    """Initialize the Google Cloud Run Services client."""
    return _build_client(ServicesClient, credentials=credentials)
