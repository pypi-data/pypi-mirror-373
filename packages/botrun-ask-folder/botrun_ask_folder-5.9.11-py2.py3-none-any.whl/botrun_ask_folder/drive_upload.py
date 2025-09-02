# drive_upload.py
# 上傳檔案到 google drive
import argparse
import glob
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def upload_file(service, file_path, parent_folder_id):
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [parent_folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')


def get_files_from_patterns(file_patterns):
    all_files = []
    for pattern in file_patterns:
        files = glob.glob(pattern, recursive=True)
        all_files.extend(files)
    return all_files


def drive_upload(service_account_file, parent_folder_id, file_patterns):
    credentials = service_account.Credentials.from_service_account_file(service_account_file)
    service = build('drive', 'v3', credentials=credentials)
    upload_files = get_files_from_patterns(file_patterns)
    for file_path in upload_files:
        if os.path.exists(file_path):
            file_id = upload_file(service, file_path, parent_folder_id)
            print(f"Uploaded {file_path} successfully. File ID: {file_id}.")
        else:
            print(f"File does not exist: {file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload files to Google Drive.")
    parser.add_argument('--service_account_file', type=str, help="Path to the service account credentials file.")
    parser.add_argument('--parent_folder_id', type=str,
                        help="ID of the Google Drive folder to which files will be uploaded.")
    parser.add_argument('--upload_files', nargs='+', help="List of file patterns to upload.")
    args = parser.parse_args()
    drive_upload(args.service_account_file, args.parent_folder_id, args.upload_files)
'''
source venv/bin/activate
python lib_botrun/botrun_ask_folder/drive_upload.py \
--service_account_file "./keys/google_service_account_key.json" \
--parent_folder_id "1EsKZlL8fEjrARS_zYK-515YFA0UpWY3M" \
--upload_files "./data/1pxy3LFhTvzkS2PRkdr3ZsuXQb1GJuvLe/加速推動地方創生計畫院核定本.pdf.txts/*.page_3.*" "./data/1pxy3LFhTvzkS2PRkdr3ZsuXQb1GJuvLe/加速推動地方創生計畫院核定本.pdf.txts/*.page_4.*" "./data/1pxy3LFhTvzkS2PRkdr3ZsuXQb1GJuvLe/加速推動地方創生計畫院核定本.pdf.txts/*.page_5.*"

'''
