from typing import Union


PAGE_NUMBER_NA = "n/a"


class RagMetadata:
    """
    這個是 RAG 用來存放在 qdrant裡的 metadata
    """

    def __init__(
        self,
        name: str,
        ori_file_name: str,
        gen_page_imgs: bool,
        page_number: Union[int, str],
        sheet_name: str = None,
        save_path: str = "",
    ):
        """
        @param name: 這個處理檔案的名字，因為有的時候會分頁分段，所以這裡是分頁分段後的檔案名字，根原始檔案名字不一樣
        @param ori_file_name: 原始檔案名字
        @param gen_page_imgs: 是否有要生成頁面圖片
        @param page_number: 如果有頁面的話，這個會是數字，如果沒有的話，會是 n/a
        """
        self.name = name
        self.ori_file_name = ori_file_name
        self.gen_page_imgs = gen_page_imgs
        self.page_number = page_number
        self.sheet_name = sheet_name
        self.save_path = save_path
