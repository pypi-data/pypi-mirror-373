from copy import deepcopy
from datetime import datetime
import litellm
from litellm.types.utils import GenericStreamingChunk, ModelResponse
from typing import Iterator, AsyncIterator, List, Union
from litellm import CustomLLM, Choices, CustomStreamWrapper
import uuid
import os
import asyncio
from botrun_log import Logger, TextLogEntry
import pytz
import json
import urllib.parse

from botrun_keys_mgr.key_manager import KeyManager
from botrun_ask_folder.query_qdrant import query_qdrant_and_llm
from dotenv import load_dotenv

from botrun_litellm.utils.llm_utils import get_api_key, get_base_url, get_model_name
from botrun_ask_folder.botrun_reader import (
    read_notice_prompt_and_collection_from_botrun,
)
from botrun_ask_folder.litellm_proxy.config.hatch_reader import (
    read_notice_prompt_and_model_from_hatch,
)
import re

load_dotenv()
BOTRUN_LOG_PROJECT_ID = os.getenv("BOTRUN_LOG_PROJECT_ID")
BOTRUN_LOG_CREDENTIALS_PATH = os.getenv("BOTRUN_LOG_CREDENTIALS_PATH")
BOTRUN_LOG_DATASET_NAME = os.getenv("BOTRUN_LOG_DATASET_NAME")
BOTRUN_LOG_DEPARTMENT = os.getenv("BOTRUN_LOG_DEPARTMENT")
big_query_logger = Logger(
    db_type="bigquery",
    project_id=BOTRUN_LOG_PROJECT_ID,
    credentials_path=BOTRUN_LOG_CREDENTIALS_PATH,
    dataset_name=BOTRUN_LOG_DATASET_NAME,
    department=BOTRUN_LOG_DEPARTMENT,
)


class BotrunLLMError(Exception):  # use this for all your exceptions
    def __init__(
        self,
        status_code,
        message,
    ):
        self.status_code = status_code
        self.message = message
        super().__init__(
            self.message
        )  # Call the base class constructor with the parameters it needs


class BotrunLLMParams:
    def __init__(
        self,
        qdrant_host,
        qdrant_port,
        qdrant_api_key,
        collection_name,
        chat_history,
        user_input,
        embedding_model,
        top_k,
        notice_prompt,
        chat_model,
        hnsw_ef,
        file_path_field,
        text_content_field,
        google_file_id_field,
        page_number_field,
        gen_page_imgs_field,
        ori_file_name_field,
        sheet_name_field,
        file_upload_date_field,
        prefix=None,
        https=False,
        litellm_api_key="",
        user_email="",
    ):
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.qdrant_api_key = qdrant_api_key
        self.collection_name = collection_name
        self.chat_history = chat_history
        self.user_input = user_input
        self.embedding_model = embedding_model
        self.top_k = top_k
        self.notice_prompt = notice_prompt
        self.chat_model = chat_model
        self.hnsw_ef = hnsw_ef
        self.file_path_field = file_path_field
        self.text_content_field = text_content_field
        self.google_file_id_field = google_file_id_field
        self.page_number_field = page_number_field
        self.gen_page_imgs_field = gen_page_imgs_field
        self.ori_file_name_field = ori_file_name_field
        self.sheet_name_field = sheet_name_field
        self.file_upload_date_field = file_upload_date_field
        self.prefix = prefix
        self.https = https
        self.litellm_api_key = litellm_api_key
        self.user_email = user_email

    def _get_messages(self):
        system_msg_found = False
        for message in self.chat_history:
            if message["role"] == "system":
                message["content"] = self.notice_prompt
                system_msg_found = True
                break
        messages = self.chat_history + [
            {"role": "user", "content": self.user_input},
        ]
        if not system_msg_found:
            messages.insert(0, {"role": "system", "content": self.notice_prompt})
        return messages


class BotrunLLM(CustomLLM):
    def _should_get_params_from_botrun(self, model_name: str) -> bool:
        return model_name.startswith("botrun-") or model_name.startswith("taide-")

    async def _get_botrun_llm_params(self, *args, **kwargs) -> BotrunLLMParams:
        load_dotenv()
        model = kwargs.get("model", "")
        messages = kwargs.get("messages", [])
        user_email = self._extract_user_email(kwargs)
        print(f"===>Extracted user_email: {user_email}")
        # 提取 API key
        litellm_api_key = self._extract_api_key(kwargs)
        print(f"===>Extracted LiteLLM API key: {litellm_api_key}")  # 用於調試

        model_name = model
        is_hatch = False
        if model.startswith("botrun/"):
            model_name = model.split("/", 1)[1]
        if model_name.startswith("botrun-h-"):
            botrun_name = model_name.split("-", 2)[2]
            is_hatch = True
        elif model_name.startswith("botrun-"):
            botrun_name = model_name.split("-", 1)[1]
        elif model_name.startswith("taide-"):
            botrun_name = model_name
        else:
            raise BotrunLLMError(
                status_code=404,
                message=f"model must start with botrun- or taide-, but get {model_name}",
            )

        # todo 如果  model name有 % 符號，則做 url decode
        if "%" in botrun_name:
            botrun_name = urllib.parse.unquote(botrun_name)
        folder_id = os.environ.get("GOOGLE_DRIVE_BOTS_FOLDER_ID")
        if not folder_id:
            raise BotrunLLMError(
                status_code=500,
                message="GOOGLE_DRIVE_BOTS_FOLDER_ID environment variable is not set",
            )

        # 從 botrun 檔案讀取 notice_prompt
        # chat_model = "openai/gpt-4o-2024-08-06"
        # if self._should_get_params_from_botrun(model_name):
        if is_hatch:
            try:
                notice_prompt, collection_name, chat_model = (
                    await read_notice_prompt_and_model_from_hatch(botrun_name)
                )
            except Exception as e:
                import traceback

                traceback.print_exc()
                raise BotrunLLMError(status_code=404, message=str(e))
        else:
            try:
                notice_prompt, collection_name, chat_model = (
                    read_notice_prompt_and_collection_from_botrun(
                        botrun_name, folder_id
                    )
                )
                print(f"[_get_botrun_llm_params]notice_prompt: {notice_prompt}")
                print(f"[_get_botrun_llm_params]collection_name: {collection_name}")
                print(
                    f"[_get_botrun_llm_params]_get_botrun_llm_params chat_model: {chat_model}"
                )
            except Exception as e:
                # print(f"_get_botrun_llm_params exception: {e}")
                raise BotrunLLMError(status_code=404, message=str(e))

        # 固定字段名稱
        file_path_field = "file_path"
        text_content_field = "text_content"
        google_file_id_field = "google_file_id"
        page_number_field = "page_number"
        gen_page_imgs_field = "gen_page_imgs"
        ori_file_name_field = "ori_file_name"
        sheet_name_field = "sheet_name"
        file_upload_date_field = "file-upload-date"
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = os.getenv("QDRANT_PORT", 6333)
        qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
        prefix = os.getenv("QDRANT_PREFIX", None)
        https = os.getenv("QDRANT_HTTPS", "False").lower() == "true"
        embedding_model = "openai/text-embedding-3-large"
        top_k = 6
        hnsw_ef = 256

        chat_history = messages[:-1] if len(messages) > 1 else []
        user_input = messages[-1]["content"] if messages else ""
        return BotrunLLMParams(
            qdrant_host,
            qdrant_port,
            qdrant_api_key,
            collection_name,
            chat_history,
            user_input,
            embedding_model,
            top_k,
            notice_prompt,
            chat_model,
            hnsw_ef,
            file_path_field,
            text_content_field,
            google_file_id_field,
            page_number_field,
            gen_page_imgs_field,
            ori_file_name_field,
            sheet_name_field,
            file_upload_date_field,
            prefix,
            https,
            litellm_api_key,
        )

    def completion(self, *args, **kwargs) -> litellm.ModelResponse:
        print("BotrunLLM.completion")
        # 使用事件循環運行異步的 acompletion 方法
        return asyncio.run(self.acompletion(*args, **kwargs))

    async def acompletion(self, *args, **kwargs) -> litellm.ModelResponse:
        print("BotrunLLM.acompletion")
        print("Args:", json.dumps(args, indent=2, default=str))
        print("Kwargs:", json.dumps(kwargs, indent=2, default=str))
        stream = kwargs.get("stream", False)
        model = kwargs.get("model", "")

        result = await self._generate_complete(
            await self._get_botrun_llm_params(*args, **kwargs)
        )
        return ModelResponse(
            id=f"botrun-{uuid.uuid4()}",
            choices=[
                {
                    "message": {"role": "assistant", "content": result},
                    "finish_reason": "stop",
                }
            ],
            model="botrun",
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        )

    async def _sync_to_async_generator(self, sync_gen):
        for item in sync_gen:
            yield item
            await asyncio.sleep(0)  # 讓出控制權，允許其他協程運行

    async def _generate_stream(
        self, botrun_llm_params: BotrunLLMParams, model: str
    ) -> AsyncIterator[ModelResponse]:
        # print("BotrunLLM._generate_stream model:", model)
        async for fragment in self._sync_to_async_generator(
            query_qdrant_and_llm(
                botrun_llm_params.qdrant_host,
                botrun_llm_params.qdrant_port,
                botrun_llm_params.collection_name,
                botrun_llm_params.user_input,
                botrun_llm_params.embedding_model,
                botrun_llm_params.top_k,
                botrun_llm_params.notice_prompt,
                botrun_llm_params.chat_model,
                botrun_llm_params.hnsw_ef,
                botrun_llm_params.file_path_field,
                botrun_llm_params.text_content_field,
                botrun_llm_params.google_file_id_field,
                botrun_llm_params.page_number_field,
                botrun_llm_params.gen_page_imgs_field,
                botrun_llm_params.ori_file_name_field,
                botrun_llm_params.sheet_name_field,
                botrun_llm_params.file_upload_date_field,
                include_ref_page=False,
                chat_history=botrun_llm_params.chat_history,
                qdrant_api_key=botrun_llm_params.qdrant_api_key,
                prefix=botrun_llm_params.prefix,
                https=botrun_llm_params.https,
            )
        ):
            # print("BotrunLLM._generate_stream fragment:", fragment)
            yield ModelResponse(
                id=f"botrun-chunk-{uuid.uuid4()}",
                choices=[{"delta": {"content": fragment}, "finish_reason": None}],
                model=f"botrun/{model}",
                stream=True,
            )
        # print("BotrunLLM._generate_stream finish")
        yield ModelResponse(
            id=f"botrun-chunk-{uuid.uuid4()}",
            choices=[{"delta": {"content": ""}, "finish_reason": "stop"}],
            model=f"botrun/{model}",
            stream=True,
        )

    async def _generate_generic_stream_chunk(
        self, botrun_llm_params: BotrunLLMParams, model: str
    ) -> AsyncIterator[GenericStreamingChunk]:
        # print("BotrunLLM._generate_generic_stream_chunk model:", model)
        index = 0
        if botrun_llm_params.collection_name is None:
            # agent 串串串先拿掉
            # agents = get_agents(botrun_llm_params.notice_prompt)
            agents = []
            if len(agents) > 0:
                # agent 串串串先拿掉
                # async for chunk in self.respond_with_agents(botrun_llm_params, agents):
                #     yield chunk
                return
            # 使用一般的 litellm streaming
            else:
                print("litellm.acompletion<===2 start")
                print(f"model: {get_model_name(botrun_llm_params.chat_model)}")
                print(f"api_key: {get_api_key(botrun_llm_params.chat_model)}")
                print(f"base_url: {get_base_url(botrun_llm_params.chat_model)}")
                print("litellm.acompletion<===2 end")
                messages = botrun_llm_params._get_messages()
                insert_usage_log(
                    action_type="api_input",
                    model=botrun_llm_params.chat_model,
                    action_details=json.dumps(messages),
                    litellm_api_key=botrun_llm_params.litellm_api_key,
                    user_email=botrun_llm_params.user_email,
                )
                response = await litellm.acompletion(
                    model=get_model_name(botrun_llm_params.chat_model),
                    api_key=get_api_key(botrun_llm_params.chat_model),
                    base_url=get_base_url(botrun_llm_params.chat_model),
                    messages=messages,
                    stream=True,
                )
            note = ""
            async for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    note += content
                    yield GenericStreamingChunk(
                        finish_reason=None,
                        index=index,
                        is_finished=False,
                        text=content,
                        tool_use=None,
                        usage={
                            "completion_tokens": 0,
                            "prompt_tokens": 0,
                            "total_tokens": 0,
                        },
                    )
                    index += 1

            # 最後一個 chunk
            yield GenericStreamingChunk(
                finish_reason="stop",
                index=index,
                is_finished=True,
                text="",
                tool_use=None,
                usage={
                    "completion_tokens": 0,
                    "prompt_tokens": 0,
                    "total_tokens": 0,
                },  # 您可能需要累積實際的使用量
            )
            insert_usage_log(
                action_type="api_output",
                model=botrun_llm_params.chat_model,
                action_details=note,
                litellm_api_key=botrun_llm_params.litellm_api_key,
                user_email=botrun_llm_params.user_email,
            )
        else:
            messages = botrun_llm_params._get_messages()
            insert_usage_log(
                action_type="api_input",
                model=botrun_llm_params.chat_model,
                action_details=json.dumps(messages),
                litellm_api_key=botrun_llm_params.litellm_api_key,
                user_email=botrun_llm_params.user_email,
            )
            note = ""
            async for fragment in self._sync_to_async_generator(
                query_qdrant_and_llm(
                    botrun_llm_params.qdrant_host,
                    botrun_llm_params.qdrant_port,
                    botrun_llm_params.collection_name,
                    botrun_llm_params.user_input,
                    botrun_llm_params.embedding_model,
                    botrun_llm_params.top_k,
                    botrun_llm_params.notice_prompt,
                    botrun_llm_params.chat_model,
                    botrun_llm_params.hnsw_ef,
                    botrun_llm_params.file_path_field,
                    botrun_llm_params.text_content_field,
                    botrun_llm_params.google_file_id_field,
                    botrun_llm_params.page_number_field,
                    botrun_llm_params.gen_page_imgs_field,
                    botrun_llm_params.ori_file_name_field,
                    botrun_llm_params.sheet_name_field,
                    botrun_llm_params.file_upload_date_field,
                    include_ref_page=False,
                    chat_history=botrun_llm_params.chat_history,
                    qdrant_api_key=botrun_llm_params.qdrant_api_key,
                    prefix=botrun_llm_params.prefix,
                    https=botrun_llm_params.https,
                )
            ):
                # print("BotrunLLM._generate_stream fragment:", fragment)
                note += fragment
                yield GenericStreamingChunk(
                    finish_reason=None,
                    index=index,
                    is_finished=False,
                    text=fragment,
                    tool_use=None,
                    usage={
                        "completion_tokens": 10,
                        "prompt_tokens": 20,
                        "total_tokens": 30,
                    },
                )
                index += 1
            # print("BotrunLLM._generate_stream finish")
            yield GenericStreamingChunk(
                finish_reason="stop",
                index=index,
                is_finished=True,
                text="",
                tool_use=None,
                usage={
                    "completion_tokens": 10,
                    "prompt_tokens": 20,
                    "total_tokens": 30,
                },
            )
            insert_usage_log(
                action_type="api_output",
                model=botrun_llm_params.chat_model,
                action_details=note,
                litellm_api_key=botrun_llm_params.litellm_api_key,
                user_email=botrun_llm_params.user_email,
            )

    async def _generate_complete(self, *args) -> str:
        result = ""
        botrun_llm_params = args[0]
        if botrun_llm_params.collection_name is None:
            # agent 串串串先拿掉
            # agents = get_agents(botrun_llm_params.notice_prompt)
            agents = []
            if len(agents) > 0:
                result = ""
                # agent 串串串先拿掉
                # async for chunk in self.respond_with_agents(botrun_llm_params, agents):
                #     if isinstance(chunk, dict):
                #         result += chunk["text"]
                #     else:
                #         result += chunk.text
                return result
            else:
                # 使用一般的 litellm completion
                print("litellm.acompletion<===1 start")
                print(f"model: {get_model_name(botrun_llm_params.chat_model)}")
                print(f"api_key: {get_api_key(botrun_llm_params.chat_model)}")
                print(f"base_url: {get_base_url(botrun_llm_params.chat_model)}")
                print("litellm.acompletion<===1 end")
                messages = botrun_llm_params._get_messages()
                insert_usage_log(
                    action_type="api_input",
                    model=botrun_llm_params.chat_model,
                    action_details=json.dumps(messages),
                    litellm_api_key=botrun_llm_params.litellm_api_key,
                    user_email=botrun_llm_params.user_email,
                )
                # print(botrun_llm_params._get_messages())
                response = await litellm.acompletion(
                    model=get_model_name(botrun_llm_params.chat_model),
                    api_key=get_api_key(botrun_llm_params.chat_model),
                    base_url=get_base_url(botrun_llm_params.chat_model),
                    messages=botrun_llm_params._get_messages(),
                )
                insert_usage_log(
                    action_type="api_output",
                    model=botrun_llm_params.chat_model,
                    action_details=response.choices[0].message.content,
                    litellm_api_key=botrun_llm_params.litellm_api_key,
                    user_email=botrun_llm_params.user_email,
                )
                return response.choices[0].message.content
        else:
            insert_usage_log(
                action_type="api_input",
                model=botrun_llm_params.chat_model,
                action_details=json.dumps(botrun_llm_params._get_messages()),
                litellm_api_key=botrun_llm_params.litellm_api_key,
                user_email=botrun_llm_params.user_email,
            )
            async for fragment in self._sync_to_async_generator(
                query_qdrant_and_llm(
                    botrun_llm_params.qdrant_host,
                    botrun_llm_params.qdrant_port,
                    botrun_llm_params.collection_name,
                    botrun_llm_params.user_input,
                    botrun_llm_params.embedding_model,
                    botrun_llm_params.top_k,
                    botrun_llm_params.notice_prompt,
                    botrun_llm_params.chat_model,
                    botrun_llm_params.hnsw_ef,
                    botrun_llm_params.file_path_field,
                    botrun_llm_params.text_content_field,
                    botrun_llm_params.google_file_id_field,
                    botrun_llm_params.page_number_field,
                    botrun_llm_params.gen_page_imgs_field,
                    botrun_llm_params.ori_file_name_field,
                    botrun_llm_params.sheet_name_field,
                    botrun_llm_params.file_upload_date_field,
                    include_ref_page=False,
                    chat_history=botrun_llm_params.chat_history,
                    qdrant_api_key=botrun_llm_params.qdrant_api_key,
                    prefix=botrun_llm_params.prefix,
                    https=botrun_llm_params.https,
                )
            ):
                result += fragment
        insert_usage_log(
            action_type="api_output",
            model=botrun_llm_params.chat_model,
            action_details=result,
            litellm_api_key=botrun_llm_params.litellm_api_key,
            user_email=botrun_llm_params.user_email,
        )
        return result

    # agent 串串串先拿掉
    # async def respond_with_agents(
    #     self, botrun_llm_params: BotrunLLMParams, agents: List[LlmAgent]
    # ) -> AsyncIterator[GenericStreamingChunk]:
    #     messages_for_llm = deepcopy(botrun_llm_params.chat_history)
    #     last_output = ""
    #     index = 0
    #     include_last_in_history = True
    #     for agent_idx, agent_prompt in enumerate(agents):
    #         model_name = get_model_name(agent_prompt.model)

    #         api_key = get_api_key(model_name)

    #         if not api_key:
    #             raise BotrunLLMError(
    #                 "No API key found for model: {model_name}. Please set up your API key.",
    #                 model_name=model_name,
    #             )

    #         system_prompt = ""
    #         pattern = r"<system-prompt>\r?\n(.*?)\r?\n</system-prompt>"

    #         match = re.search(pattern, agent_prompt.system_prompt, re.DOTALL)
    #         if match:
    #             system_prompt = match.group(1).strip()
    #         else:
    #             system_prompt = agent_prompt.system_prompt

    #         if agent_idx > 0:
    #             input_message = AGENT_TEMPLATE.replace(
    #                 "{context}", last_output
    #             ).replace("{rules}", system_prompt)
    #             if not include_last_in_history:
    #                 messages_for_llm.pop()
    #             messages_for_llm.append({"role": "user", "content": input_message})
    #             include_last_in_history = agent_prompt.include_in_history
    #         else:
    #             input_message = AGENT_TEMPLATE.replace(
    #                 "{context}", botrun_llm_params.user_input
    #             ).replace("{rules}", system_prompt)
    #             messages_for_llm.append({"role": "user", "content": input_message})

    #         final_messages = deepcopy(messages_for_llm)
    #         if agent_prompt.max_system_prompt_length is not None:
    #             for message in final_messages:
    #                 if (
    #                     message["role"] == "system"
    #                     and len(message["content"])
    #                     > agent_prompt.max_system_prompt_length
    #                 ):
    #                     message["content"] = ""
    #         insert_usage_log(
    #             action_type="api_input",
    #             model=model_name,
    #             action_details=json.dumps(final_messages),
    #             litellm_api_key=botrun_llm_params.litellm_api_key,
    #         )
    #         response = await litellm.acompletion(
    #             model=model_name,
    #             messages=final_messages,
    #             api_key=api_key,
    #             base_url=get_base_url(model_name),
    #             stream=True,
    #         )

    #         # 處理每個代理的串流響應
    #         current_content = ""
    #         async for chunk in response:
    #             content = chunk.choices[0].delta.content
    #             if content:
    #                 current_content += content
    #                 if agent_prompt.print_output:
    #                     yield GenericStreamingChunk(
    #                         finish_reason=None,
    #                         index=index,
    #                         is_finished=False,
    #                         text=content,
    #                         tool_use=None,
    #                         usage={
    #                             "completion_tokens": 0,
    #                             "prompt_tokens": 0,
    #                             "total_tokens": 0,
    #                         },
    #                     )
    #                 index += 1

    #         # 更新最後的非圖片輸出，用於下一個代理
    #         last_output = current_content
    #         insert_usage_log(
    #             action_type="api_output",
    #             model=model_name,
    #             action_details=current_content,
    #             litellm_api_key=botrun_llm_params.litellm_api_key,
    #         )

    #     # 最後一個 chunk，表示所有代理都完成了
    #     yield GenericStreamingChunk(
    #         finish_reason="stop",
    #         index=index,
    #         is_finished=True,
    #         text="",
    #         tool_use=None,
    #         usage={
    #             "completion_tokens": 0,
    #             "prompt_tokens": 0,
    #             "total_tokens": 0,
    #         },
    #     )

    def streaming(self, *args, **kwargs) -> Iterator[GenericStreamingChunk]:
        print("BotrunLLM.streaming")
        return self._sync_generator(self.astreaming(*args, **kwargs))

    async def astreaming(self, *args, **kwargs) -> AsyncIterator[GenericStreamingChunk]:
        model = kwargs.get("model", "")
        print("BotrunLLM.astreaming model:", model)
        async for chunk in self._generate_generic_stream_chunk(
            await self._get_botrun_llm_params(*args, **kwargs), model
        ):
            yield chunk

    def _sync_generator(self, async_gen):
        while True:
            try:
                yield asyncio.run(async_gen.__anext__())
            except StopAsyncIteration:
                break

    def _extract_user_email(self, kwargs: dict) -> str:
        # 這裡可以取的到，是因為在 generate key 的時候，有放在 key_alias 中
        user_email = (
            kwargs.get("litellm_params", {})
            .get("metadata", {})
            .get("user_api_key_alias", "")
        )
        return user_email

    def _extract_api_key(self, kwargs: dict) -> str:
        """
        從 kwargs 中安全地提取 API key
        如果找不到或發生錯誤，返回空字串
        """
        try:
            # 從 litellm_params.proxy_server_request.headers.authorization 中提取
            proxy_request = kwargs.get("litellm_params", {}).get(
                "proxy_server_request", {}
            )
            headers = proxy_request.get("headers", {})
            auth_header = headers.get("authorization", "")

            # 檢查是否是 Bearer token 格式
            if auth_header.startswith("Bearer "):
                return auth_header.split(" ")[1]

            return ""
        except Exception as e:
            print(f"Error extracting API key: {e}")
            return ""


def insert_usage_log(
    action_type: str,
    model: str,
    action_details: str,
    litellm_api_key: str,
    user_email: str,
):
    asyncio.create_task(
        insert_usage_log_async(
            action_type, model, action_details, litellm_api_key, user_email
        )
    )


async def insert_usage_log_async(
    action_type: str,
    model: str,
    action_details: str,
    litellm_api_key: str,
    user_email: str,
):
    # return
    try:
        if user_email != "":
            email = user_email
        else:
            key_manager = KeyManager()
            key_data = key_manager.get_key_info(litellm_api_key)
            email = key_data.applicant_email if key_data else ""
        # user = cl.user_session.get("user")
        # email = user.metadata.get("email", user.display_name)
        # if not email:
        #     email = user.identifier
        tz = pytz.timezone("Asia/Taipei")  # 台北時間，即 UTC+8
        text_log = TextLogEntry(
            timestamp=datetime.now(tz).strftime("%Y-%m-%dT%H:%M:%SZ"),
            domain_name=os.getenv("BOTRUN_LOG_DOMAIN_NAME", ""),
            user_department="",  # todo 看要怎麼抓到 department
            user_name=email,
            source_ip="",  # todo
            session_id="",  # todo message start 的時候給一
            action_type=action_type,
            developer=litellm_api_key,
            action_details=action_details,
            model=model,
            botrun=os.getenv("BOTRUN_LOG_BOTRUN_NAME", "botrun"),
            user_agent="",  # todo
            resource_id=os.getenv("BOTRUN_LOG_DOMAIN_NAME", ""),
        )

        big_query_logger.insert_text_log(text_log)
        print(f"===>Inserted usage log: {text_log}")
    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"Error inserting usage log: {e}")


botrun_llm = BotrunLLM()
