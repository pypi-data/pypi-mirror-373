# 使用方式
- 安裝 FastAPI
```shell
pip install fastapi
```
- 執行測試的 server，在這個 folder下執行
```shell
fastapi dev main.py
```
## 本地測試
 - 如果在 local 測試: http://127.0.0.1:8000/api/botrun/botrun_ask_folder/這裡接自己的 api 名稱
 - 線上測試：/api/botrun/botrun_ask_folder/這裡接自己的 api 名稱

## 測試功能
### 查看 folder 處理進度
```bash
curl -X POST http://0.0.0.0:8080/api/botrun/botrun_ask_folder/folder-status \
-H "Content-Type: application/json" \
-d '{"folder_id": "1qk5maEqbxtTcr1tsAHawVduonPedpHV0"}'
```

### 處理單一文件
```bash
curl -X POST http://0.0.0.0:8080/api/botrun/botrun_ask_folder/process-file \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "1xIXIm6LoEdrpAvJRDnHuIybxTNqi0JDP",
    "force": true,
    "embed": true
  }'
```
### 青創貸款 (呼叫 cloud run job)
```bash
curl -X POST http://0.0.0.0:8080/api/botrun/botrun_ask_folder/process-folder-job \
-H "Content-Type: application/json" \
-d '{"folder_id": "1qk5maEqbxtTcr1tsAHawVduonPedpHV0", "force":true}'
```

### 青創貸款 (呼叫 cloud run job)
```bash
curl -X POST https://dev-ask-folder-api.botrun.ai/api/botrun/botrun_ask_folder/process-folder-job \
-H "Content-Type: application/json" \
-d '{"folder_id": "1qk5maEqbxtTcr1tsAHawVduonPedpHV0", "force":true}'
```

### 查看 folder 處理進度
```bash
curl -X POST https://dev-ask-folder-api.botrun.ai/api/botrun/botrun_ask_folder/folder-status \
-H "Content-Type: application/json" \
-d '{"folder_id": "1qk5maEqbxtTcr1tsAHawVduonPedpHV0"}'
```









# 備份使用 cloud run 做平行處理
## 要使用 firestore 來建立 queue ，需要幫它建 index
### 參考圖片  
![firestore index](https://i.ibb.co/PmqgtV7/2024-08-22-7-46-32.png)

## 測試 功能
### 青創貸款 
```bash
curl -X POST http://0.0.0.0:8080/api/botrun/botrun_ask_folder/pub-process-folder \
-H "Content-Type: application/json" \
-d '{"folder_id": "1qk5maEqbxtTcr1tsAHawVduonPedpHV0", "force":true}'
```

### 青創貸款 (不要 embed)
```bash
curl -X POST http://0.0.0.0:8080/api/botrun/botrun_ask_folder/pub-process-folder \
-H "Content-Type: application/json" \
-d '{"folder_id": "1qk5maEqbxtTcr1tsAHawVduonPedpHV0", "force":false, "embed":false}'
```
### 清除所有 job
```bash
curl -X POST http://0.0.0.0:8080/api/botrun/botrun_ask_folder/complete-all-jobs \
-H "Authorization: Bearer ${BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN}" \
```

## Cloud run 測試
### 青創貸款 (備份)
```bash
curl -X POST https://dev-ask-folder-api.botrun.ai/api/botrun/botrun_ask_folder/pub-process-folder \
-H "Content-Type: application/json" \
-d '{"folder_id": "1qk5maEqbxtTcr1tsAHawVduonPedpHV0", "force":true}'
```

### 青創貸款 (不要 embed)  (備份)
```bash
curl -X POST https://dev-ask-folder-api.botrun.ai/api/botrun/botrun_ask_folder/pub-process-folder \
-H "Content-Type: application/json" \
-d '{"folder_id": "1qk5maEqbxtTcr1tsAHawVduonPedpHV0", "force":true, "embed":false}'
```
### 清除所有 job  (備份)
```bash
curl -X POST https://dev-ask-folder-api.botrun.ai/api/botrun/botrun_ask_folder/complete-all-jobs  \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJib3RydW5fYXNrX2ZvbGRlciJ9.Q5xTx5aoCeyZOqrA2Nz0oKl9KtgW8FvYQJ9lOd-Mj5c" \
```


### 做壓力測試的網頁
- https://dev-ask-folder-api.botrun.ai/api/botrun/botrun_ask_folder/stress