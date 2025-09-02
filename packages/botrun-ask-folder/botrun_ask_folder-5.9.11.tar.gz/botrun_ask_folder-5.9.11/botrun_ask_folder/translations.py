from typing import Any

translations = {
    "Start processing folder {folder_id} at {timestamp}": "開始執行資料 {folder_id} 匯入工作 {timestamp}",
    "List all files in {folder_id}, job_id: {job_id} {timestamp}": "條列所有 {folder_id} 的檔案, job_id: {job_id} {timestamp}",
    "Data {folder_id} import job failed: {message} at {timestamp}": "資料 {folder_id} 匯入工作失敗: 得到訊息 {message} {timestamp}",
    "Please click this link to check the import status: {check_url}": "請點選此連結檢查匯入狀態: {check_url}",
    "{folder_id} data import completed, can start using {timestamp}": "{folder_id} 資料匯入完成，可以開始使用 {timestamp}",
    "Data import completed, took {time_str}, processed {total_files} files": "資料匯入完成，花費 {time_str}, 處理了 {total_files} 個檔案",
    "{folder_id} data import failed, please contact our customer service partners!": "{folder_id} 資料匯入有發生錯誤，請連繫我們最貼心的客服夥伴們喔！",
    "Check import job {folder_id} timeout at {timestamp}": "檢查匯入工作 {folder_id} 逾時 {timestamp}",
    "Check import job {folder_id} failed: {message} at {timestamp}": "檢查匯入工作 {folder_id} 失敗: {message} {timestamp}",
    "@begin link({url}) {text} @end": "@begin link({url}) {text} @end",
}
language = "en"


def set_language(lang: str):
    global language
    language = lang


def tr(text: str, **kwargs: Any) -> str:
    global language
    if language == "en":
        translated = text
    else:
        translated = translations.get(text, text)

    # 如果提供了额外的参数，使用它们来格式化翻译后的字符串
    if kwargs:
        try:
            return translated.format(**kwargs)
        except KeyError:
            # 如果格式化失败，返回原始翻译
            return translated

    return translated
