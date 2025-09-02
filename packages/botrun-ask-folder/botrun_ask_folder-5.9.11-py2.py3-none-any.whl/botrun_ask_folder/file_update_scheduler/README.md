# File Update Scheduler 是一個會自動去檢查Google Drive 有沒有檔案更新，有的話會去update qdrant 的程式
## Docker-compose 裡面要注意的事情
- .env 也要上傳
- keys 也要上傳
- 要把　`botrun_back/data` 的目錄也 mount 上來 

## 參考資料
- [設定排程的 spreadsheet](https://docs.google.com/spreadsheets/d/1yxj6rtsYccq5LY9LXC6Ih6PKM_vFjFwJF5LUx3oja9I/edit?gid=0#gid=0)