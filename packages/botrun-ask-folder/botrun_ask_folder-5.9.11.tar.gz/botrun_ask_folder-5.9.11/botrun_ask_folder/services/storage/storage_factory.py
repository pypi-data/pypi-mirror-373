from botrun_ask_folder.services.storage.storage_store import StorageStore
from botrun_ask_folder.services.storage.storage_cs_store import StorageCsStore
from botrun_ask_folder.services.storage.storage_client import StorageClient
from botrun_ask_folder.services.storage.fast_api_storage_client import (
    FastAPIStorageClient,
)


def storage_store_factory() -> StorageStore:
    return StorageCsStore()


def storage_client_factory() -> StorageClient:
    return FastAPIStorageClient()
