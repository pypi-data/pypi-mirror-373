# text_file_detector.py
import os

import chardet


def is_text_file(file_path, initial_bytes=1024):
    text_extensions = {
        '.json', '.jsonl', '.yaml', '.yml', '.txt', '.botrun', '.txt.botrun', '.csv',
        '.py', '.html', '.css', '.js', '.jsx', '.xml', '.md', '.markdown',
        '.ts', '.rs', '.toml',
        '.scss', '.less', '.vue', '.svelte',
        '.sh', '.bash', '.zsh', '.fish',
        '.sql', '.pl', '.php', '.java', '.c', '.cpp', '.h', '.hpp',
        '.rb', '.r', '.go', '.dart', '.swift', '.kt', '.kts',
        '.ini', '.cfg', '.conf', '.env',
        '.log', '.gitignore', '.dockerignore', '.editorconfig',
        '.htaccess'
    }

    non_text_extensions = {
        '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls',
        '.zip', '.rar', '.7z', '.tar', '.gz', '.pdf', '.exe', '.dll',
        '.mp4', '.mp3', '.m4a', '.jpg', '.jpeg', '.png', '.gif',
        'mov', '.avi', '.mkv', '.webm', '.lnk'
    }

    extension = os.path.splitext(file_path)[1].lower()

    if extension in text_extensions:
        return True
    if extension in non_text_extensions:
        return False

    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(initial_bytes)

        detected = chardet.detect(raw_data)
        encoding = detected.get('encoding', '')

        return try_decode(raw_data, encoding) or (
                'utf-16' in encoding.lower() and
                (try_decode(raw_data[:-1], encoding) or try_decode(raw_data[:-2], encoding))
        )
    except Exception:
        return False


def try_decode(data, encoding):
    try:
        data.decode(encoding)
        return True
    except (UnicodeDecodeError, LookupError):
        return False
