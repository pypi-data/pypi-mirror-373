import argparse
import os
import re
import sys
import json
import time
from datetime import datetime
from litellm import completion
from qdrant_client import QdrantClient
from qdrant_client.http import models

from botrun_ask_folder.generate_pages_html import generate_pdf_gallery_html
from botrun_ask_folder.util import extract_date_from_filename, get_formatted_date_for_qdrant


# custom_log 需要 debug 時才開啟寫檔案
def custom_log(level, message, is_write_to_file=False):
    log_file_path = "./users/botrun_ask_folder/query_keyword.log"
    log_format = "{} - {} - {}\n".format(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), level, message
    )
    print(log_format)
    if is_write_to_file:
        with open(log_file_path, "a") as log_file:
            log_file.write(log_format)


DEFAULT_NOTICE_PROMPT = """
妳是臺灣人，回答要用臺灣繁體中文正式用語不能輕浮、不能隨便 
請妳不可以使用簡體中文回答，不可以使用大陸慣用語回答 
請妳基於「知識庫」及使用者的提問，step by step 分析之後，列點（要有標題與內容）回答 
若「知識庫」有談到相關的時間、數字、數據，務必一定要講出來，才精確，不能省略！ 
若「知識庫」有談到舉例、案例、故事、示範，務必一定要用例子回答，才能懂，不能省略！ 
若「知識庫」有時間或日期，而文字內容相似矛盾的話，要用最新時間日期的為準，別用舊的
如果妳不會回答的部分，不可以亂猜
"""

SPECIAL_STRING = "<<Botrun.ai波特人的沉穩參考來源>>"


def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        minutes, seconds = divmod(elapsed_time, 60)
        print(f"{func.__name__} executed in {int(minutes)}m{seconds:.3f}s")
        return result

    return wrapper


# 從使用者問提產生關鍵字清單
@timing_decorator
def generate_keywords(
    user_input: str, model="gpt-4o-2024-08-06", prompt_keyword="auto"
) -> list:
    # 達成生成關鍵字的邏輯
    # keyword_list=['T-ROAD', 't-road', 'T-Road', 'Data Fabric', 'data fabric', 'DATA FABRIC', 'Data Fabric', 'data fabric', 'DATA FABRIC', 'Data Fabric', 'data fabric', 'DATA FABRIC'] #roy debug
    # print(keyword_list) #roy debug
    # return keyword_list #roy debug

    if not prompt_keyword or prompt_keyword == "auto":
        # prompt_keyword = '''找出句子中1個用來搜尋的專有名詞，以 "keyword1,keyword2" 的格式回傳，優先選中文專有名詞，英文的專有名詞務必回傳第一個字母與連接號後第一個字母大寫,全大寫,全小寫三種格式，只給專有名詞關鍵字清單就好，如果沒有關鍵字請回傳無關鍵字'''
        prompt_keyword = """請從句子中找出一個用來搜尋的專有名詞，以 "keyword1,keyword2" 的格式回傳。請優先選擇中文專有名詞。對於英文專有名詞，請以三種格式回傳 1.首字母大寫, 2.全大寫(uppercase), 3.全小寫(lowercase)。只需回傳專有名詞關鍵字的清單。如果沒有關鍵字，請回傳 "無關鍵字"。"""

    # 假設這裡會有一些生成關鍵字的邏輯，並且將結果添加到keywords列表中
    response = completion(
        model=model,
        messages=[{"role": "user", "content": f"{prompt_keyword}:{user_input}"}],
    )
    keywords = response.choices[0].message.content.strip()
    # 將回應切割成清單
    keyword_list = [keyword.strip() for keyword in keywords.split(",")]
    print(keyword_list)
    return keyword_list


@timing_decorator
def query_qdrant_knowledge_base_keyword(
    qdrant_host,
    qdrant_port,
    collection_name,
    user_input,
    embedding_model,
    hnsw_ef,
    chat_model="gpt-4o-mini",
    top_k=10,
    is_show_ref_info=True,
    file_path_field="file_path",
    text_content_field="text_content",
    google_file_id_field="google_file_id",
    page_number_field="page_number",
    gen_page_imgs_field="gen_page_imgs",
    ori_file_name_field="ori_file_name",
    sheet_name_field="sheet_name",
    file_upload_date_field="file-upload-date",
    prompt_keyword="auto",
    qdrant_api_key="",
    prefix=None,
    https=False,
) -> str:
    try:
        custom_log("INFO", f"Querying Qdrant Keyword for user input: {user_input}")
        qdrant_client_instance = QdrantClient(
            qdrant_host,
            port=qdrant_port,
            api_key=qdrant_api_key,
            prefix=prefix,
            https=https,
        )

        # 擷取使用者問題中查詢用的關鍵字
        # Query by keywords roy added
        user_input_keywords = generate_keywords(
            user_input, model=chat_model, prompt_keyword=prompt_keyword
        )
        # user_input_keywords = ["利息補貼", "額度計算", "承貸銀行"] #,"青年創業", "驗光師", "信用保證"]
        print(f" user_input_keywords for query: {user_input_keywords}")

        # 多個關鍵字進行 OR 檢索
        # 執行全文檢索
        search_result = qdrant_client_instance.scroll(
            collection_name=collection_name,
            scroll_filter=models.Filter(
                # 篩選邏輯 OR 要用 "should", AND 要用 "must"
                should=[
                    field_condition
                    for keyword in user_input_keywords
                    for field_condition in [
                        models.FieldCondition(
                            key="text_content", match=models.MatchText(text=keyword)
                        ),
                        models.FieldCondition(
                            key="file_path", match=models.MatchText(text=keyword)
                        ),
                    ]
                ]
            ),
            limit=top_k*10,  # 取10倍資料量，以便取得較新資料後排序
        )

        # debug: 使用者查詢內容寫道 log 擋
        # custom_log('INFO', f"Received {len(search_result)} results from Qdrant")

        str_knowledge_base = ""
        # fastapi_url = os.environ.get('BOTRUN_ASK_FOLDER_FAST_API_URL', 'http://localhost:8000')
        pdf_list = []

        # 列印 response 顯示其內容，用於確定結構
        print(f"search_result type: {type(search_result)}")
        print(f"search_result length: {len(search_result[0])}")
        # print(f"search_result content: {search_result[0]}")

        # 假設返回的一個元組，第二個元素是包含 Record 物件的列表
        if isinstance(search_result, tuple) and len(search_result) > 1:
            print("檢查所有關鍵字搜索到的檔案以確認排序:")
            for doc in search_result[0]:
                ori_file_name = doc.payload.get(ori_file_name_field, "")
            
            # 取出所有搜尋結果並附上日期資訊用於排序
            results_with_dates = []
            for doc in search_result[0]:
                ori_file_name = doc.payload.get(ori_file_name_field, "")
                date_obj = extract_date_from_filename(ori_file_name)
                # 使用絕對字符串格式化，避免隱藏字符問題
                print(f"關鍵字搜索提取日期: {repr(ori_file_name)} -> {date_obj}")
                results_with_dates.append((doc, date_obj))
            
            # 將所有結果以日期排序
            # print(f"results_with_dates: {results_with_dates}")
            results_with_dates.sort(key=lambda x: (x[1] is not None, x[1]), reverse=True)
            
            # 打印排序後的結果以便確認
            print("排序後的關鍵字搜索結果（從新到舊）:")
            for i, (doc, date) in enumerate(results_with_dates, 1):
                ori_file_name = doc.payload.get(ori_file_name_field, "")
                print(f"{i}. {repr(ori_file_name)} -> {date}")
            
            # 獲取排序後的檔案列表，只取前 top_k 筆
            sorted_results = [doc for doc, _ in results_with_dates][:top_k]
            print(f"只保留前 {top_k} 筆排序後的結果")
            
            for matched_doc in sorted_results:
                # print(f"===matched_doc======================")
                # print(matched_doc.payload["file_path"])
                # print(matched_doc.payload["text_content"])
                # print(f"=========================")

                # 取得參考來源欄位要用的資訊
                google_file_id = matched_doc.payload.get(google_file_id_field, "")
                page_number = matched_doc.payload.get(page_number_field, "")
                ori_file_name = matched_doc.payload.get(ori_file_name_field, "")
                gen_page_imgs = matched_doc.payload.get(gen_page_imgs_field, False)
                file_upload_date = matched_doc.payload.get(file_upload_date_field, "")
                
                # 生成標準格式的日期字符串
                file_info_date = get_formatted_date_for_qdrant(ori_file_name)

                str_knowledge_base += f"\n" f"<關鍵字回傳>\n"

                str_knowledge_base += (
                    f"\n"
                    f"<a-rag-file>\n"
                    f"<file-path>\n"
                    f"""{matched_doc.payload["file_path"], 'N/A'}\n"""
                    f"</file-path>\n"
                )
                str_knowledge_base += (
                    f"<text-content>\n"
                    f"""{matched_doc.payload["text_content"], 'N/A'}"""
                    f"</text-content>\n"
                    # f"</a-rag-file>\n"
                )
                # 要加，前端才可以依照資料庫動是否有資料，來動態顯示參考原檔圖片
                if is_show_ref_info:
                    str_knowledge_base += (
                        f"<{google_file_id_field}>"
                        f"{google_file_id}"
                        f"</{google_file_id_field}>\n"
                    )
                    str_knowledge_base += (
                        f"<{page_number_field}>"
                        f"{page_number}"
                        f"</{page_number_field}>\n"
                    )
                    str_knowledge_base += (
                        f"<{ori_file_name_field}>"
                        f"{ori_file_name}"
                        f"</{ori_file_name_field}>\n"
                    )
                    str_knowledge_base += (
                        f"<{gen_page_imgs_field}>"
                        f"{gen_page_imgs}"
                        f"</{gen_page_imgs_field}>\n"
                    )
                    str_knowledge_base += (
                        f"<collection_name>"
                        f"{collection_name}"
                        f"</collection_name>\n"
                    )
                    str_knowledge_base += (
                        f"<{file_upload_date_field}>"
                        f"{file_upload_date}"
                        f"</{file_upload_date_field}>\n"
                    )
                    str_knowledge_base += (
                        f"<file-info-date>"
                        f"{file_info_date}"
                        f"</file-info-date>\n"
                    )
                str_knowledge_base += f"</a-rag-file>\n"
                str_knowledge_base += f"\n" f"</關鍵字回傳>\n"

        else:
            print(
                "[query_qdrant_knowledge_base (query_qdrant_keyword.py)] info:知識庫內找不到資料..."
            )

        os.makedirs("./dev", exist_ok=True)
        str_knowledge_base_to_file = f" user_input_keywords for query: {user_input_keywords}\n {str_knowledge_base} "
        open("./dev/keyword.txt", "w").write(str_knowledge_base_to_file)

    except Exception as e:
        print(f"query_qdrant.py, query_qdrant_knowledge_base_keyword, exception: {e}")
        import traceback

        traceback
        return ""  # error return empty string

    return str_knowledge_base


def query_qdrant_and_llm_keyword(
    qdrant_host,
    qdrant_port,
    collection_name,
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
):
    # 呼叫 query_qdrant_knowledge_base 函式
    str_knowledge_base = query_qdrant_knowledge_base_keyword(
        qdrant_host=qdrant_host,
        qdrant_port=qdrant_port,
        collection_name=collection_name,
        user_input=user_input,
        embedding_model=embedding_model,
        hnsw_ef=hnsw_ef,
        chat_model=chat_model,  # 2024-07-25 新增，因為要生成查詢關鍵字
        top_k=top_k,
        file_path_field=file_path_field,
        text_content_field=text_content_field,
        google_file_id_field=google_file_id_field,
        page_number_field=page_number_field,
        gen_page_imgs_field=gen_page_imgs_field,
        ori_file_name_field=ori_file_name_field,
    )

    # print("=============str_knowledge_base===============")
    # print(str_knowledge_base)
    # print("=============str_knowledge_base===============")

    if not notice_prompt:
        notice_prompt = DEFAULT_NOTICE_PROMPT
    str_message = f"""
    <知識庫RAG搜索到的內容>
    {str_knowledge_base}
    </知識庫RAG搜索到的內容>

    <回答時請妳注意>
    {notice_prompt}
    </回答時請妳注意>

    <使用者提問請妳回答>
    {user_input}
    </使用者提問請妳回答>
    """
    return completion_call(chat_model, str_message)


def completion_call(model, message):
    custom_log(
        "INFO", f"Entering completion_call with model: {model}, message: {message}"
    )
    try:
        messages = [{"content": message, "role": "user"}]
        custom_log("INFO", f"Messages prepared: {messages}")
        generator = filtered_stream_with_hidden_content(model, messages)
        reference_content = ""
        custom_log("INFO", "Starting iteration over generator")
        # 迭代生成器直到倒數第二個值
        for chunk in generator:
            if isinstance(chunk, str):  # 確保chunk是字符串
                custom_log("INFO", f"Chunk received: {chunk}")
                if chunk.startswith(SPECIAL_STRING):
                    reference_content = chunk.split(SPECIAL_STRING, 1)[1]
                    custom_log(
                        "INFO",
                        f"Found special string. Reference content: {reference_content}",
                    )
                    break
                yield chunk
            else:
                custom_log("DEBUG", "Chunk is not a string, breaking loop")
                break  # 如果chunk不是字符串，跳出循環

        """
        try:
            custom_log('INFO', f"Reference content: {reference_content}")
            lst_refs = json.loads(reference_content)['references']
            custom_log('INFO', f"References parsed: {lst_refs}")
            generated_ref_page = generate_pdf_page_to_image(lst_refs)
            custom_log('INFO', f"Generated reference page: {generated_ref_page}")
            yield generate_ref_section(lst_refs, generated_ref_page)
        except json.JSONDecodeError as e:
            custom_log('ERROR', f"Invalid JSON: {e}")
        """
    except Exception as e:
        custom_log("ERROR", f"Exception in completion_call: {e}")
        # print stacktrace
        import traceback

        traceback.print_exc()
        print(f"query_qdrant.py, completion_call, exception: {e}")


def generate_ref_section(lst_refs, generated_ref_page: bool):
    api_prefix = "/api/botrun/botrun_ask_folder"
    ref_files_id = {}
    ref_files_and_page = {}
    for ref in lst_refs:
        if ref["ori_file_name"] in ref_files_and_page.keys():
            current_pages = ref_files_and_page[ref["ori_file_name"]]
            if ref["page_number"] not in current_pages:
                ref_files_and_page[ref["ori_file_name"]].append(str(ref["page_number"]))
        else:
            ref_files_and_page[ref["ori_file_name"]] = [str(ref["page_number"])]
        if ref["google_file_id"] not in ref_files_id.keys():
            ref_files_id[ref["ori_file_name"]] = ref["google_file_id"]
    ref_text = "參考來源："
    for file_name, pages in ref_files_and_page.items():
        google_file_id = ref_files_id[file_name]
        ref_text += (
            f"\n- [{file_name} 第{', '.join(pages)}頁]("
            + f"{api_prefix}/download_file/{google_file_id}"
            + ")"
        )
    if generated_ref_page:
        ref_text += f"\n- [參考頁面截圖](/api/data/{lst_refs[0]['collection_name']}/html/index{datetime.now().strftime('%Y%m%d%H%M%S')}.html)"
    return ref_text


def generate_pdf_page_to_image(lst_refs):
    api_prefix = "/api/botrun/botrun_ask_folder"
    pdf_list = []
    for ref in lst_refs:
        google_file_id = ref.get("google_file_id", "")
        page_number = ref.get("page_number", "")
        # if page_number is not a int
        try:
            page_number = int(page_number)
        except ValueError:
            page_number = 0
        if page_number < 1:
            continue
        ori_file_name = ref.get("ori_file_name", "")
        gen_page_imgs = ref.get("gen_page_imgs", False)
        # if gen_page_imgs is string, convert to boolean
        if isinstance(gen_page_imgs, str):
            gen_page_imgs = gen_page_imgs.lower() == "true"
        if not gen_page_imgs:
            continue
        collection_name = ref.get("collection_name", "")
        if google_file_id and page_number and gen_page_imgs:
            pdf_list.append(
                {
                    "filename": f"{ori_file_name}",
                    "page": page_number,
                    "image_url": f"/api/data/{collection_name}/img/{google_file_id}_{page_number}.png",
                    "pdf_url": f"{api_prefix}/download_file/{google_file_id}",
                }
            )
    if len(pdf_list) > 0:
        os.makedirs(f"./data/{collection_name}/html", exist_ok=True)
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        open(f"./data/{collection_name}/html/index{now}.html", "w").write(
            generate_pdf_gallery_html(pdf_list)
        )
        return True
    return False


def filtered_stream_with_hidden_content(model, messages):
    custom_log(
        "INFO",
        f"Entering filtered_stream_with_hidden_content with model: {model}, messages: {messages}",
    )
    response = completion(model=model, messages=messages, stream=True)
    buffer = ""
    hidden_content = ""
    found_special_string = False

    for chunk in response:
        content = chunk.choices[0].delta.content or ""
        buffer += content
        custom_log("INFO", f"Buffer after adding content: {buffer}")

        if not found_special_string:
            # 檢查是否包含特殊字符串
            split = buffer.split(SPECIAL_STRING, 1)
            custom_log("INFO", f"Split result: {split}")

            if len(split) > 1:
                # 如果找到特殊字符串
                yield split[0]  # 只輸出特殊字符串之前的內容
                hidden_content += split[1]  # 開始收集隱藏內容
                found_special_string = True
                buffer = ""
                custom_log(
                    "INFO", f"Found special string. Hidden content: {hidden_content}"
                )
            else:
                # 如果沒有找到特殊字符串，檢查是否可以安全地yield一部分buffer
                safe_to_yield = re.search(r"(.*\S+\s+)", buffer)
                if safe_to_yield:
                    to_yield = safe_to_yield.group(1)
                    yield to_yield
                    buffer = buffer[len(to_yield) :]
                    custom_log("INFO", f"Yielded safe content: {to_yield}")
        else:
            # 特殊字符串之後的所有內容都添加到hidden_content
            hidden_content += content
            custom_log("INFO", f"Hidden content after adding content: {hidden_content}")

    # 如果整個響應結束都沒有找到特殊字符串，yield剩餘的buffer
    if buffer and not found_special_string:
        yield buffer
        custom_log("INFO", f"Yielded remaining buffer: {buffer}")

    # 最後yield隱藏內容
    yield SPECIAL_STRING + hidden_content.strip()
    custom_log(
        "INFO",
        f"Yielded final hidden content: {SPECIAL_STRING + hidden_content.strip()}",
    )

    # 添加日志记录
    custom_log("INFO", f"Filtered stream with hidden content: {hidden_content}")


def query_qdrant_and_llm_print_keyword(
    qdrant_host,
    qdrant_port,
    collection_name,
    user_input,
    embedding_model,
    top_k,
    notice_prompt,
    chat_model,
    hnsw_ef,
    file_path_field,
    text_content_field,
    google_file_id_field="google_file_id",
    page_number_field="page_number",
    gen_page_imgs_field="gen_page_imgs",
    ori_file_name_field="ori_file_name",
):
    custom_log("INFO", f"Starting query_qdrant_and_llm for user input: {user_input}")
    for fragment in query_qdrant_and_llm_keyword(
        qdrant_host,
        qdrant_port,
        collection_name,
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
    ):
        print(fragment, end="")
        sys.stdout.flush()
    custom_log("INFO", "Finished query_qdrant_and_llm")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search documents in Qdrant using natural language query."
    )
    parser.add_argument("--query")
    parser.add_argument("--collection", default="collection_1")
    parser.add_argument("--embedding_model", default="openai/text-embedding-3-large")
    parser.add_argument("--top_k", default=12)
    parser.add_argument("--notice_prompt", default=DEFAULT_NOTICE_PROMPT)
    parser.add_argument("--chat_model", default="gpt-4-turbo-preview")
    parser.add_argument("--hnsw_ef", default=256)
    parser.add_argument("--file_path_field", default="file_path")
    parser.add_argument("--text_content_field", default="text_content")
    args = parser.parse_args()

    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    query_qdrant_and_llm_print_keyword(
        qdrant_host,
        qdrant_port,
        args.collection,
        args.query,
        args.embedding_model,
        args.top_k,
        args.notice_prompt,
        args.chat_model,
        args.hnsw_ef,
        args.file_path_field,
        args.text_content_field,
    )
