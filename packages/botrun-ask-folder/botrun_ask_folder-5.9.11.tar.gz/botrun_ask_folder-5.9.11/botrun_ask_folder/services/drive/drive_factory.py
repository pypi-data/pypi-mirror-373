from botrun_ask_folder.services.drive.drive_client import (
    DriveClient,
)
from botrun_ask_folder.services.drive.fast_api_drive_client import (
    FastAPIDriveClient,
)
from botrun_ask_folder.services.drive.drive_store import (
    DriveFolderStore,
    DriveFileStore,
    SplittedFileStore,
)
from botrun_ask_folder.services.drive.drive_fs_store import (
    DriveFolderFsStore,
    DriveFileFsStore,
    SplittedFileFsStore,
)


def drive_client_factory() -> DriveClient:
    return FastAPIDriveClient()


def drive_folder_store_factory() -> DriveFolderStore:
    return DriveFolderFsStore()


def drive_file_store_factory() -> DriveFileStore:
    return DriveFileFsStore()


def splitted_file_store_factory() -> SplittedFileStore:
    return SplittedFileFsStore()
