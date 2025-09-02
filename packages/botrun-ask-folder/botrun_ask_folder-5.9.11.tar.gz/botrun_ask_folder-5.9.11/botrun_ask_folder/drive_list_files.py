import argparse
import json
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build

from .emoji_progress_bar import EmojiProgressBar


def extract_folder_id(google_drive_url):
    """
    三種格式都可以正確抽出 Google Drive document id
    001 https://drive.google.com/drive/folders/101lIrf6O-3iGOMF19Y-5exJooDp8wht8?usp=drive_link
    002 https://drive.google.com/drive/u/0/folders/101lIrf6O-3iGOMF19Y-5exJooDp8wht8
    003 101lIrf6O-3iGOMF19Y-5exJooDp8wht8
    """
    pattern = r'https?://drive.google.com/drive/(folders/|u/[0-9]+/folders/)?([a-zA-Z0-9_-]+)|(^[a-zA-Z0-9_-]+$)'
    match = re.search(pattern, google_drive_url)
    if match:
        return match.group(2) if match.group(2) else match.group(3)
    else:
        raise ValueError("Invalid Google Drive URL format.")


def list_files_recursive(service, folder_id, base_path="", max_files=10, current_count=0, is_top_level=True,
                         filter_sub_folder=""):
    all_files = []
    total_size = 0
    folder_count = 0  # 資料夾計數器
    file_count = 0  # 檔案計數器

    query = f"'{folder_id}' in parents and trashed=false"
    page_token = None
    while True:
        try:
            response = service.files().list(q=query, spaces='drive',includeItemsFromAllDrives=True,
                                            supportsAllDrives=True,
                                            fields='nextPageToken, files(id, name, mimeType, modifiedTime, size, parents)',
                                            pageToken=page_token, pageSize=1000).execute()
        except Exception as e:
            print(f"Error listing files: {e}")
            break

        items = response.get('files', [])
        if is_top_level:
            progress_bar = EmojiProgressBar(len(items))  # 在頂層資料夾時初始化進度條

        for item in items:
            if max_files is not None and current_count >= max_files:
                break
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                if is_top_level and filter_sub_folder != "" and item["name"] != filter_sub_folder:
                    continue
                folder_count += 1  # 資料夾計數
                try:
                    child_files, child_size, current_count = list_files_recursive(service, item['id'],
                                                                                  base_path=base_path + item[
                                                                                      'name'] + "/",
                                                                                  max_files=max_files,
                                                                                  current_count=current_count,
                                                                                  is_top_level=False)
                except Exception as e:
                    print(f"Error listing files in folder {item['name']}: {e}")
                    continue
                all_files.extend(child_files)
                total_size += child_size
            else:
                file_count += 1  # 檔案計數
                item_size = int(item.get('size', 0))
                total_size += item_size
                all_files.append({'id': item['id'], 'name': item['name'], 'mimeType': item['mimeType'],
                                  'modifiedTime': item.get('modifiedTime'),
                                  'size': str(item_size), 'parent': item['parents'][0] if 'parents' in item else 'None',
                                  'path': base_path + item['name']})
                current_count += 1
            if is_top_level:
                progress_bar.update(folder_count + file_count)  # 更新進度條

        page_token = response.get('nextPageToken', None)
        if page_token is None or (max_files is not None and current_count >= max_files):
            break

    return all_files, total_size, current_count


def list_files_common(service, parent_folder_id_or_url, max_files):
    parent_folder_id = extract_folder_id(parent_folder_id_or_url)
    try:
        files_info, total_size, final_count = list_files_recursive(service, parent_folder_id, max_files=max_files)
    except Exception as e:
        print(f"Error listing files: {e}")
        return {}

    dic_result = {
        'parent_id': parent_folder_id,
        'items': files_info[:max_files] if max_files is not None else files_info,
        'total_files_returned': final_count,
        'total_size': total_size
    }

    return dic_result


def drive_list_files(service_account_file, parent_folder_id_or_url, max_files):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    try:
        credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
        service = build('drive', 'v3', credentials=credentials)
    except Exception as e:
        print(f"Error setting up Google Drive service: {e}")
        return {}

    return list_files_common(service, parent_folder_id_or_url, max_files)


def drive_list_files_with_service(service, parent_folder_id_or_url, max_files):
    return list_files_common(service, parent_folder_id_or_url, max_files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch all files under a specific folder recursively with their paths, limited by a maximum number of files.")
    parser.add_argument('--service_account_file', required=True, type=str,
                        help="Path to the service account credentials file.")
    parser.add_argument('--parent_folder_id_or_url', required=True, type=str,
                        help="ID of the Google Drive folder to fetch contents from.")
    parser.add_argument('--max_files', type=int, default=None,
                        help="Maximum number of files to return. None is no limit.")
    args = parser.parse_args()

    dic_result = drive_list_files(args.service_account_file, args.parent_folder_id_or_url, args.max_files)
    # 很美的印出 dic_result
    json_dumps = json.dumps(dic_result, indent=4, ensure_ascii=False)
    print(json_dumps)

'''
source venv/bin/activate
python lib_botrun/botrun_ask_folder/drive_list_files.py \
--service_account_file "keys/google_service_account_key.json" \
--parent_folder_id_or_url "1IpnZVKecvjcPOsH0q6YyhpS2ek2-Eig9" \
--max_files 100
'''
