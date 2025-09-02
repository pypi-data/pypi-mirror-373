from botrun_ask_folder.services.queue.queue_store import QueueStore
from botrun_ask_folder.services.queue.queue_fs_store import QueueFsStore
from botrun_ask_folder.services.queue.queue_client import QueueClient
from botrun_ask_folder.services.queue.fast_api_queue_client import FastAPIQueueClient


def queue_store_factory() -> QueueStore:
    return QueueFsStore()


def queue_client_factory() -> QueueClient:
    return FastAPIQueueClient()
