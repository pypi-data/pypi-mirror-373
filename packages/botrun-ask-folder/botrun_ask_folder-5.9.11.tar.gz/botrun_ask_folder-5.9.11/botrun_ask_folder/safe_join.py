import os


def safe_join(base_path, *paths):
    # 確保基礎路徑是絕對路徑
    base_path = os.path.abspath(base_path)
    # 組合所有的路徑
    full_path = os.path.join(base_path, *paths)
    # 正規化路徑，解析掉 '..' 和 './'
    normalized_path = os.path.normpath(full_path)

    # 確保正規化後的路徑是在指定的基本目錄下
    if not normalized_path.startswith(base_path + os.sep):
        raise ValueError("Attempt to access outside the base directory")

    return normalized_path
