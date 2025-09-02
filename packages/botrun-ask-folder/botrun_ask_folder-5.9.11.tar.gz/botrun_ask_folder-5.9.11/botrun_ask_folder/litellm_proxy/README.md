# Proxy Server

## 開發注意事項
- 確定一些package 是否最新版
  - `litellm`, 可以執行 `pip install -U litellm`
  - `botrun_flow_lang`, 可以執行 `pip install -U botrun_flow_lang`
- 本地端要先能夠跑起來
執行方式可以參考 `launch.json`
```json
    {
      "name": "litellm proxy",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/.venv/bin/litellm",  // 修改這裡
      "args": [
        "--config",
        "botrun_ask_folder/litellm_proxy/config/config.yaml"
      ],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      },
      "console": "integratedTerminal",
      "justMyCode": false
    },

```
- 本地端開發的時候，不要去檢查 key，所以要把 db disable，去 `config.yaml`修改 `general_settings`
  把 `allow_requests_on_db_unavailable: true` 打開

## 要看 litellm proxy 有哪些 api 
- http://dev.botrun.ai:4000

## 測試方式，測試讀取 .botrun的檔案
```shell
# 新版的 litellm 不支援在 header 裡面放中文，所以要使用之前，需要將中文字 urlencode
# 以下為波殼
curl -X POST 'http://0.0.0.0:4000/chat/completions' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer sk-key' \
-d '{
    "model": "botrun/botrun-%E6%B3%A2%E6%AE%BC",
    "messages": [{"role": "user", "content": "講一個小紅帽的故事"}]
}'
curl -X POST 'http://0.0.0.0:4000/chat/completions' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer sk-key' \
-H "Accept: text/event-stream" \
-d '{
    "model": "botrun/botrun-%E6%B3%A2%E6%AE%BC",
    "messages": [{"role": "user", "content": "講一個小紅帽的故事"}],
    "stream":true
}'
# 以下為波創價學會
curl -X POST 'http://0.0.0.0:4000/chat/completions' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer sk-key' \
-d '{
    "model": "botrun/botrun-%E6%B3%A2%E5%89%B5%E5%83%B9%E5%AD%B8%E6%9C%83",
    "messages": [{"role": "user", "content": "創價學會的宗指為何？"}]
}'
curl -X POST 'http://0.0.0.0:4000/chat/completions' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer sk-key' \
-H "Accept: text/event-stream" \
-d '{
    "model": "botrun/botrun-%E6%B3%A2%E5%89%B5%E5%83%B9%E5%AD%B8%E6%9C%83",
    "messages": [{"role": "user", "content": "創價學會的宗指為何？"}],
    "stream":true
}'
```
這個是沒有 import_rag_plus 的
```shell
curl -X POST 'https://dev.botrun.ai/llmapi/chat/completions' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer api-key' \
-d '{
    "model": "botrun/botrun-波分段",
    "messages": [{"role": "user", "content": "你好，請介紹一下你自己"}]
}'
curl -X POST 'https://dev.botrun.ai/llmapi/chat/completions' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer api-key' \
-H "Accept: text/event-stream" \
-d '{
    "model": "botrun/botrun-波分段",
    "messages": [{"role": "user", "content": "你好，請介紹一下你自己"}],
    "stream":true
}'

```

## 測試方式，測試讀取 波孵人
```shell
curl -X POST 'http://0.0.0.0:4000/chat/completions' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer sk-key' \
-d '{
    "model": "botrun/botrun-h-sebastian.hsu%40gmail.com",
    "messages": [{"role": "user", "content": "你好，請介紹一下你自己"}]
}'
curl -X POST 'http://0.0.0.0:4000/chat/completions' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer sk-key' \
-H "Accept: text/event-stream" \
-d '{
    "model": "botrun/botrun-h-sebastian.hsu%40gmail.com",
    "messages": [{"role": "user", "content": "你好，請介紹一下你自己"}],
    "stream":true
}'



## 生 key
給所有的 model
```shell
curl --location 'http://dev.botrun.ai:4000/key/generate' \
--header 'Authorization: Bearer bo-1cda98a6-4f5f-46c5-ab5f-6ff62b9aec00' \
--header 'Content-Type: application/json' \
--data '{
    "metadata": {"user": "seba"}
}'
```
給特殊的 model
```shell
curl --location 'http://dev.botrun.ai:4000/key/generate' \
--header 'Authorization: Bearer bo-1cda98a6-4f5f-46c5-ab5f-6ff62b9aec00' \
--header 'Content-Type: application/json' \
--data '{
      "models": ["botrun/botrun-波創價學會"],
      "key_alias":"sebastian.hsu@gmail.com",
      "metadata": {"user": "seba波"}
}'
curl --location 'http://dev.botrun.ai:4000/key/generate' \
--header 'Authorization: Bearer bo-1cda98a6-4f5f-46c5-ab5f-6ff62b9aec00' \
--header 'Content-Type: application/json' \
--data '{
      "models": ["botrun/botrun-%E6%B3%A2%E6%AE%BC"],
      "key_alias":"sebastian.hsu@gmail.com",
      "metadata": {"user": "sebastian.hsu@gmail.com"}
}'
```

- config.yaml 裡要有的 model，才能使用
## 安裝
- 需要安裝 litellm[proxy]

## 執行 server
目前改成 docker 方式，所以這一行可能無法執行了，但是還是留著參考
```shell
litellm --config botrun_ask_folder/litellm_proxy/config/config.yaml
```

## 執行 server docker
```shell
docker-compose up -d
```
