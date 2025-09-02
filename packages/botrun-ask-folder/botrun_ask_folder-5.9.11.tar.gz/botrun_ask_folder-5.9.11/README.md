# BotRun Ask Folder

這個專案提供了一個從 Google Drive 資料夾下載文件並處理成嵌入式向量，最後將其上傳到 Qdrant 的工具。以下是如何使用這個工具的說明。

---

## 安裝

請先確保您已經安裝 Python 以及 pip。然後，您可以使用以下指令來安裝這個專案的依賴套件：

```sh
pip install botrun-ask-folder
```

---

## 使用方法

### 調用 `botrun_ask_folder`

`botrun_ask_folder` 函數可以幫助您下載指定 Google Drive 資料夾中的文件，進行處理並上傳到 Qdrant。

```python
from botrun_ask_folder import botrun_ask_folder

# Google Drive 資料夾ID
google_drive_folder_id = "your_google_drive_folder_id"

botrun_ask_folder(google_drive_folder_id)
```

### 所需環境變數
在運行此工具前，請設置以下環境變數：

| 環境變數                  | 說明                            |
| -------------------------- |-------------------------------|
| GOOGLE_APPLICATION_CREDENTIALS | 用於Google服務帳戶的憑證路徑             |
| QDRANT_HOST                | Qdrant 伺服器的主機名 (default為 "qdrant")   |
| QDRANT_PORT                | Qdrant 伺服器的埠號 (default為 6333) |

### 各個函數的詳細用法

#### `drive_download`

從 Google Drive 下載文件。

```python
from botrun_ask_folder.drive_download import drive_download

google_service_account_key_path = "/path/to/google_service_account_key.json"
google_drive_folder_id = "your_google_drive_folder_id"
max_results = 9999999
output_folder = "./data/your_google_drive_folder_id"

drive_download(google_service_account_key_path, google_drive_folder_id, max_results, output_folder)
```

#### `run_split_txts`

將下載的文件切分成指定大小的文本片段。

```python
from botrun_ask_folder.run_split_txts import run_split_txts

input_folder = "./data/your_google_drive_folder_id"
split_size = 2000  # 每個文本片段的最大字符數
force = False

run_split_txts(input_folder, split_size, force)
```

#### `embeddings_to_qdrant`

將文本片段轉換為嵌入式向量並上傳到 Qdrant。

```python
import asyncio
from botrun_ask_folder.embeddings_to_qdrant import embeddings_to_qdrant

input_folder = "./data/your_google_drive_folder_id"
embedding_model_name = "openai/text-embedding-3-large"
dimension = 3072
max_tasks = 30
collection_name = "your_google_drive_folder_id"
qdrant_host = "qdrant"
qdrant_port = 6333

asyncio.run(embeddings_to_qdrant(input_folder, embedding_model_name, dimension, max_tasks, collection_name, qdrant_host, qdrant_port))
```

#### `botrun_drive_manager`

管理和更新 .botrun 提示工程的模板與副本。

```python
from botrun_ask_folder.botrun_drive_manager import botrun_drive_manager

botrun_file_name = "your_botrun_file_name"
collection_name = "your_collection_name"

botrun_drive_manager(botrun_file_name, collection_name)
```

### 開啟 Fast API 的方式

到目錄 `botrun_ask_folder/fast_api` 下，執行以下指令：

```shell
fastapi dev main.py
```

然後可以透過 http://localhost:8000 存取 api

### 佈署 Google Cloud Function
前有使用 Google Cloud Function，檔案在主目錄下的 main.py
佈署方式如下：
要先讓 gcloud cli 有 botrun-ask-folder-2@scoop-386004.iam.gserviceaccount.com service account 的權限
去 console 下載，或是跟阿杰要
```shell
gcloud auth activate-service-account \
    --key-file=/path/to/your/keyfile.json
```

---

## 開發環境設置

### 創建虛擬環境

為專案創建一個虛擬環境，以便管理依賴包和避免與其他專案的衝突。

```sh
python -m venv venv
source venv/bin/activate  # 在 Windows 上使用 `venv\Scripts\activate`
```

### 安裝依賴

在虛擬環境中安裝必要的依賴包。

```sh
pip install -r requirements.txt
```

### 運行單元測試

運行項目的單元測試，以確保所有功能都正確實現。

```sh
python -m unittest discover tests
```

---

## 常見問題

### 無法下載文件，出現許可權錯誤？

請確保您的 Google 服務帳戶憑證具有訪問所需 Google Drive 資料夾的正確許可權。

### Qdrant 連接失敗？

請檢查您的 Qdrant 伺服器主機和埠號是否正確，以及是否已啟動並可連接。

### 如何自訂分頁處理的字符數量？

您可以在呼叫 `run_split_txts` 時傳遞 `split_size` 參數來設置每頁的最大字符數。

# 將 botrun_ask_folder 使用 fastapi 服務
需要有一個 .env.cloudrun 跟阿杰拿
## 打包 cloud run, dev 的版本
```bash
gcloud builds submit --config cloudbuild_fastapi_dev.yaml --project=scoop-386004
```

## deploy cloud run, dev 的版本
```bash
gcloud run deploy botrun-ask-folder-fastapi-dev \
  --image asia-east1-docker.pkg.dev/scoop-386004/botrun-ask-folder/botrun-ask-folder-fastapi-dev \
  --port 8080 \
  --platform managed \
  --allow-unauthenticated \
  --project=scoop-386004 \
  --region=asia-east1 \
  --cpu 2 \
  --memory 4Gi \
  --min-instances 0 \
  --max-instances 5 \
  --timeout 3600s \
  --concurrency 300 \
  --cpu-boost \
```

## 打包 Cloud Run, staging 的版本
```bash
gcloud builds submit --config cloudbuild_fastapi.yaml --project=scoop-386004
```

## 佈署 cloud run, staging 的版本
```bash
gcloud run deploy botrun-ask-folder-fastapi \
  --image asia-east1-docker.pkg.dev/scoop-386004/botrun-ask-folder/botrun-ask-folder-fastapi \
  --port 8080 \
  --platform managed \
  --allow-unauthenticated \
  --project=scoop-386004 \
  --region=asia-east1 \
  --cpu 2 \
  --memory 8Gi \
  --min-instances 0 \
  --max-instances 5 \
  --timeout 3600s \
  --concurrency 300 \
  --cpu-boost \
```

## 打包 cloud run job
```bash
gcloud builds submit --config cloudbuild_job.yaml --project=scoop-386004
```

## deploy cloud run job
```bash
gcloud run jobs create process-folder-job \
--image asia-east1-docker.pkg.dev/scoop-386004/botrun-ask-folder/botrun-ask-folder-job \
--region asia-east1 \
--project scoop-386004 \
--cpu 2 \
--memory 8Gi \
--max-retries 3 \
--task-timeout 7200s 
```

## update cloud run job
```bash
gcloud run jobs update process-folder-job \
--image asia-east1-docker.pkg.dev/scoop-386004/botrun-ask-folder/botrun-ask-folder-job \
--region asia-east1 \
--project scoop-386004 \
--cpu 2 \
--memory 8Gi \
--max-retries 3 \
--task-timeout 7200s
```
## cancel 正在執行的 job
```bash
gcloud run jobs executions list --job process-folder-job --format="value(name)" --region=asia-east1 --project=scoop-386004 | xargs -I {} gcloud run jobs executions cancel {} --region=asia-east1 --project=scoop-386004 --quiet
```

# Qdrant 要加 api_key
## 本地端
```bash
docker run -d \  
     -p 6333:6333 \
     -p 6334:6334 \
     -e QDRANT__SERVICE__GRPC_PORT=6334 \
     -e QDRANT__SERVICE__HTTP_PORT=6333 \
     -e QDRANT__SERVICE__API_KEY=your-own-api-key \
     -v ./qdrant_storage:/qdrant/storage \
     --name qdrant \
     qdrant/qdrant
``` 

## server 端 docker-compose



# Dapr
## 執行
```bash
dapr run -f dapr.yaml
```

## 停止
```bash
dapr stop -f dapr.yaml
```

## 測試 dapr
### 青創貸款 
```bash
curl -X POST http://localhost:8000/api/botrun/botrun_ask_folder/process-folder \
-H "Content-Type: application/json" \
-d '{"folder_id": "1qk5maEqbxtTcr1tsAHawVduonPedpHV0", "force":true}'
```

## Dapr 佈署到 Cloud Run (以下還在實驗階段，目前還沒有成功)
在專案目錄下執行
- 不要使用專案的 venv 環境，要在本機自己安裝 gcloud
- service account 要用 另一個，跟阿杰拿
### 打包 docker
```bash
gcloud builds submit --tag gcr.io/scoop-386004/botrun-ask-folder ./botrun_ask_folder/fast_api --project=scoop-386004
gcloud builds submit --config ./botrun_ask_folder/fast_api/cloudbuild.yaml --project=scoop-386004
gcloud builds submit --tag gcr.io/scoop-386004/subscriber ./botrun_ask_folder/subscribers --project=scoop-386004
gcloud builds submit --config cloudbuild_dapr.yaml --project=scoop-386004
```

### 佈署
```bash
gcloud run services replace botrun-ask-folder-service.yaml --platform managed --region asia-east1 --project=scoop-386004
gcloud run services replace subscriber-service.yaml --platform managed --region asia-east1 --project=scoop-386004
```
### 如果要設環境變數 (留存參考)
```bash
gcloud run services update botrun-ask-folder --set-env-vars KEY1=VALUE1,KEY2=VALUE2
gcloud run services update subscriber --set-env-vars KEY1=VALUE1,KEY2=VALUE2
```