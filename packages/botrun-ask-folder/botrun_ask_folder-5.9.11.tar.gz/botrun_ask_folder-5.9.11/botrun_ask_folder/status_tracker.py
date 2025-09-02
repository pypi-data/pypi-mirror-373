import os
import shutil
from datetime import datetime, timedelta
import sys
import io
from functools import wraps
import pytz

class LogStatus:
    def __init__(self, log_status_path="./data/botrun_ask_folder/status_tracker/", backup_folder="./data/botrun_ask_folder/status_tracker/backup/"):
        self.log_status_path = log_status_path
        self.backup_folder = backup_folder
        self.google_drive_folder_id=None
        self.is_capture_stdout = True
        os.makedirs(self.log_status_path, exist_ok=True)
        os.makedirs(self.backup_folder, exist_ok=True)

    def log(self, parent_folder_id, message):
        try:
            # 去除消息首尾的空白字符
            trimmed_message = message.strip()        
            # 檢查去除空白後的消息是否有效、檢查 parent_folder_id 是否有效
            if parent_folder_id and trimmed_message:
                log_file = os.path.join(self.log_status_path, f"{parent_folder_id}.log")
                with open(log_file, 'a') as f:
                    # 使用 pytz 來設定 +8 時區
                    tz = pytz.timezone('Asia/Taipei')  # 台北時間，即 UTC+8
                    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"{timestamp}: {message}\n")
                #print(f".....[LogStatus]Logged message: {message}")
            #else:
                #print(f"no log warning!! parent_folder_id={parent_folder_id}: message={message}")
        except Exception as e:
            #print(f"An error occurred while logging the message: {message}")
            #print(f"Error: {e}")
            return f"Error: {e}"

    def check_log_status(self, parent_folder_id):
        log_file = os.path.join(self.log_status_path, f"{parent_folder_id}.log")
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                return f.read()
        return "No log found for this parent_folder_id."

    def start_new_process(self, parent_folder_id):
        self.google_drive_folder_id=parent_folder_id
        log_file = os.path.join(self.log_status_path, f"{parent_folder_id}.log")
        if os.path.exists(log_file):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_folder, f"{parent_folder_id}_{timestamp}.log")
            shutil.move(log_file, backup_file)
        self.log(parent_folder_id, "New process started.")

    def set_google_drive_folder_id(self, parent_folder_id):
        self.google_drive_folder_id=parent_folder_id
        return self.google_drive_folder_id

    def get_google_drive_folder_id(self):
        return self.google_drive_folder_id

    def cleanup_old_logs(self):
        three_days_ago = datetime.now() - timedelta(days=3)
        for filename in os.listdir(self.backup_folder):
            file_path = os.path.join(self.backup_folder, filename)
            if os.path.isfile(file_path):
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_mtime < three_days_ago:
                    os.remove(file_path)


'''
    # 初始化 LogStatus
    log_status = LogStatus()
    # 開始新的處理過程
    log_status.start_new_process(parent_folder_id)

    # 記錄一些日誌
    log_status.log(parent_folder_id, "Starting download process")

    # 清理舊的日誌
    log_status.cleanup_old_logs()

    # 檢查日誌狀態
    status = log_status.check_log_status(parent_folder_id)
'''

class StdoutCapture(io.StringIO):
    def __init__(self, original_stdout, log_status, parent_folder_id):
        super().__init__()
        self.original_stdout = original_stdout
        self.log_status = log_status
        self.parent_folder_id = parent_folder_id

    def write(self, text):
        self.original_stdout.write(text)  # 保持原有的 stdout 輸出
        super().write(text)  # 捕獲輸出
        if text.strip():  # 只記錄非空白的文本
            self.log_status.log(self.parent_folder_id, text.rstrip())

    def flush(self):
        self.original_stdout.flush()
        super().flush()

def capture_stdout(log_status):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 有設定開啟才啟用 stdout 捕獲
            if log_status.is_capture_stdout:
                original_stdout = sys.stdout
                capture_stream = StdoutCapture(original_stdout, log_status, log_status.get_google_drive_folder_id())
                sys.stdout = capture_stream
                try:
                    result = func(*args, **kwargs)
                    captured_output = capture_stream.getvalue()
                    return result, captured_output
                finally:
                    sys.stdout = original_stdout
            else:
                return func(*args, **kwargs), ""
        return wrapper
    return decorator


import os



def generate_log_viewer_html(output_path, url_base, force_update=False):
    """
    生成日誌查看器 HTML 文件。

    :param output_path: 輸出 HTML 文件的路徑
    :param url_base: 基礎 URL，用於構建日誌文件的 URL
    :param force_update: 是否強制更新現有文件，默認為 False
    :return: 如果文件被創建或更新則返回 True，否則返回 False
    """
    # 檢查文件是否已存在
    if os.path.exists(output_path) and not force_update:
        print(f"文件 {output_path} 已存在，未進行更新。")
        return False

    # HTML 內容，使用 f-string 插入 url_base
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📜 Log Viewer</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
        
        body {{
            font-family: 'Roboto', Arial, sans-serif;
            margin: 0;
            padding: 10px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            display: flex;
            flex-direction: column;
            height: 95vh;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            margin-top: 0;
            text-align: center;
            font-size: 1.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }}
        #logContainer {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 10px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            word-wrap: break-word;
            flex-grow: 1;
            transition: all 0.3s ease;
            font-size: 12px;
            line-height: 1.2;
        }}
        #logContainer:hover {{
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
            padding: 10px;
        }}
        #status {{
            margin-top: 15px;
            font-style: italic;
            text-align: center;
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 20px;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        .log-entry {{
            margin-bottom: 2px;
            padding: 1px 0;
            animation: fadeIn 0.5s ease-out;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-5px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .timestamp {{
            color: #3498db;
            font-weight: bold;
        }}
        .message {{
            color: #2c3e50;
        }}
        .error {{
            color: #e74c3c;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <h1>📜 Log Viewer: <span id="logName"></span></h1>
    <div id="status">🔍 Waiting for logs...</div>
    <div id="logContainer"></div>

    <script>
        function getParameterByName(name, url = window.location.href) {{
            name = name.replace(/[\[\]]/g, '\\$&');
            var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
                results = regex.exec(url);
            if (!results) return null;
            if (!results[2]) return '';
            return decodeURIComponent(results[2].replace(/\+/g, ' '));
        }}

        const logName = getParameterByName('log') || 'test';
        document.getElementById('logName').textContent = `📁 ${{logName}}`;

        const baseUrl = '{url_base}';
        const logUrl = `${{baseUrl}}${{logName}}.log`;
        const logContainer = document.getElementById('logContainer');
        const statusElement = document.getElementById('status');
        let previousContent = '';

        function setLogContainerHeight() {{
            const windowHeight = window.innerHeight;
            const headerHeight = document.querySelector('h1').offsetHeight;
            const statusHeight = statusElement.offsetHeight;
            const padding = 40;
            const availableHeight = windowHeight - headerHeight - statusHeight - padding;
            logContainer.style.height = `${{availableHeight}}px`;
        }}

        function updateLogs() {{
            fetch(logUrl + '?nocache=' + new Date().getTime())
                .then(response => response.text())
                .then(text => {{
                    if (text !== previousContent) {{
                        const newLines = compareAndGetNewContent(previousContent, text);
                        if (newLines.length > 0) {{
                            newLines.forEach(line => {{
                                const logEntry = document.createElement('div');
                                logEntry.className = 'log-entry';
                                const match = line.match(/^(\\d{{4}}-\\d{{2}}-\\d{{2}} \\d{{2}}:\\d{{2}}:\\d{{2}}):\\s(.+)$/);
                                if (match) {{
                                    const [, timestamp, message] = match;
                                    logEntry.innerHTML = `<span class="timestamp">${{timestamp}}:</span> <span class="message">${{formatMessage(message)}}</span>`;
                                }} else {{
                                    logEntry.innerHTML = `<span class="message">${{formatMessage(line)}}</span>`;
                                }}
                                logContainer.appendChild(logEntry);
                            }});
                            logContainer.scrollTop = logContainer.scrollHeight;
                            statusElement.innerHTML = '🔄 Logs updated at ' + new Date().toLocaleString();
                        }} else {{
                            statusElement.innerHTML = '⏸️ No new logs. Last check: ' + new Date().toLocaleString();
                        }}
                        previousContent = text;
                    }} else {{
                        statusElement.innerHTML = '⏸️ No changes. Last check: ' + new Date().toLocaleString();
                    }}
                }})
                .catch(error => {{
                    console.error('Error fetching logs:', error);
                    statusElement.innerHTML = '❌ Error fetching logs. Check console for details.';
                }});
        }}

        function compareAndGetNewContent(oldContent, newContent) {{
            const oldLines = oldContent.split('\\n');
            const newLines = newContent.split('\\n');
            let newContentStartIndex = oldLines.length;

            for (let i = 0; i < oldLines.length; i++) {{
                if (oldLines[i] !== newLines[i]) {{
                    newContentStartIndex = i;
                    break;
                }}
            }}

            return newLines.slice(newContentStartIndex);
        }}

        function formatMessage(message) {{
            message = message.replace(/error/gi, '<span class="error">❌ ERROR</span>');
            message = message.replace(/warning/gi, '<span style="color: #f39c12;">⚠️ WARNING</span>');
            message = message.replace(/success/gi, '<span style="color: #2ecc71;">✅ SUCCESS</span>');
            message = message.replace(/info/gi, '<span style="color: #3498db;">ℹ️ INFO</span>');
            return message;
        }}

        setLogContainerHeight();
        window.addEventListener('resize', setLogContainerHeight);
        updateLogs();
        setInterval(updateLogs, 10000);
    </script>
</body>
</html>
"""

    # 寫入文件
    try:
        print(f"正在創建/更新 HTML 文件：{output_path}")
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
        print(f"HTML 文件已成功創建/更新：{output_path}")
        return True
    except IOError as e:
        print(f"創建/更新文件時發生錯誤：{e}")
        return False

# 使用示例
# generate_log_viewer_html('./data/{collection_name}/html/status.html', '/api/data/botrun_ask_folder/status_tracker/', force_update=True)


# 使用示例
if __name__ == "__main__":
    log_status = LogStatus()
    parent_folder_id = "example_folder_id"
    
    # 開始新的處理過程
    log_status.start_new_process(parent_folder_id)
    
    # 記錄一些日誌
    log_status.log(parent_folder_id, "Starting download process")
    log_status.log(parent_folder_id, "Downloading file 1")
    log_status.log(parent_folder_id, "Downloading file 2")
    log_status.log(parent_folder_id, "Download complete")
    
    # 檢查日誌狀態
    status = log_status.check_log_status(parent_folder_id)
    print(status)
    
    # 清理舊的日誌
    log_status.cleanup_old_logs()