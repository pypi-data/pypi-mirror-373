import re
from datetime import date

def extract_date_from_filename(filename):
    """從檔名中提取日期用於排序，支援多種日期格式
    
    Args:
        filename: 檔案名稱字串
        
    Returns:
        date對象，若日期不完整則以該年/月的第一天補齊，無日期則返回None
    """
    result = _extract_date_components(filename)
    if result == (0, 0, 0):
        return None
    
    year, month, day = result
    # 對於不完整日期，用1來補齊
    if month == 0:
        month = 1
    if day == 0:
        day = 1
        
    return date(year, month, day)

def get_formatted_date_for_qdrant(filename):
    """從檔名中提取日期並轉換為標準格式字串，用於qdrant的<file-info-date>欄位
    
    Args:
        filename: 檔案名稱字串
        
    Returns:
        YYYY-MM-DD 格式的字串，若無法提取日期則返回空字串
    """
    date_obj = extract_date_from_filename(filename)
    if date_obj:
        return date_obj.strftime("%Y-%m-%d")
    return ""

def _extract_date_components(filename):
    """從檔名中提取日期元件
    
    Args:
        filename: 檔案名稱字串
        
    Returns:
        一個排序用的元組 (year, month, day) 或 (0, 0, 0) 如果沒有找到日期
    """
    if not filename:
        return (0, 0, 0)
    
    # 優先順序1：檔名開頭是 YYYY-MM-DD 格式 (最精確的日期格式)
    match = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})', filename)
    if match:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        # 驗證日期是否合理
        if 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
            return (year, month, day)
    
    # 優先順序2：檔名開頭是 YYYY-MM 格式
    match = re.match(r'^(\d{4})-(\d{1,2})(?!-\d)', filename)
    if match:
        year, month = int(match.group(1)), int(match.group(2))
        # 驗證日期是否合理
        if 1900 <= year <= 2100 and 1 <= month <= 12:
            return (year, month, 0)
    
    # 優先順序3：檔名開頭是 YYYY_ 格式
    match = re.match(r'^(\d{4})_', filename)
    if match:
        year = int(match.group(1))
        if 1900 <= year <= 2100:
            return (year, 0, 0)
    
    # 優先順序4：檔名中包含 YYYY年 格式 (通常是民國年轉西元)
    match = re.search(r'(\d{4})年', filename)
    if match:
        year = int(match.group(1))
        if 1900 <= year <= 2100:
            return (year, 0, 0)
    
    # 優先順序5：處理民國年份格式 (例如 113年)
    match = re.search(r'(\d{2,3})年', filename)
    if match:
        roc_year = int(match.group(1))
        # 檢查是否是合理的民國年份 (1年到150年)
        if 1 <= roc_year <= 150:
            ad_year = roc_year + 1911
            return (ad_year, 0, 0)
    
    # 優先順序6：處理檔名中包含民國年月日格式如 1130903 (民國113年9月3日)
    match = re.search(r'(\d{2,3})(\d{2})(\d{2})(?!\d)', filename)
    if match:
        # 提取年月日
        roc_year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        
        # 檢查是否是合理的民國年份和月日
        if 1 <= roc_year <= 150 and 1 <= month <= 12 and 1 <= day <= 31:
            ad_year = roc_year + 1911
            print(f"民國年月日格式 {match.group(0)} -> ({ad_year}, {month}, {day})")
            return (ad_year, month, day)
    
    # 優先順序7：檔名中包含 _YYYY_ 格式 (不在開頭)
    match = re.search(r'_(\d{4})_', filename)
    if match:
        year = int(match.group(1))
        if 1900 <= year <= 2100:
            return (year, 0, 0)
    
    # 優先順序8：檔名中包含獨立的4位數年份 (不是作為其他數字的一部分)
    match = re.search(r'(?<!\d)(\d{4})(?!\d)', filename)
    if match:
        year = int(match.group(1))
        if 1900 <= year <= 2100:
            return (year, 0, 0)
    
    # 若沒有找到日期格式，回傳最小值
    return (0, 0, 0) 