def generate_pdf_gallery_html(pdf_list):
    """
    pdf_list 裡的元素是
    {
                 "filename": f"{hit.payload.get(ori_file_name_field, 'N/A')}",
                 "page": page_number,
                 "image_url": f"/api/data/{collection_name}/img/{google_file_id}_{page_number}.png",
                 "pdf_url": f"{api_prefix}/download_file/{google_file_id}"
        }
    """
    html_template = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>相關的參考內容</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        h1 {{
            text-align: center;
            color: #2c3e50;
        }}
        .gallery {{
            max-width: 800px;
            margin: 40px auto;
        }}
        .item {{
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
            overflow: hidden;
        }}
        .item-image {{
            padding: 10px;
            background-color: #fff;
        }}
        .item img {{
            width: 100%;
            height: auto;
            display: block;
            border: 1px solid #ddd;
        }}
        .item-content {{
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .item-title {{
            font-size: 18px;
            font-weight: bold;
            color: #34495e;
            flex-grow: 1;
        }}
        .item-link {{
            display: inline-block;
            background-color: #3498db;
            color: #fff;
            padding: 8px 15px;
            border-radius: 5px;
            text-decoration: none;
            transition: background-color 0.3s ease;
            white-space: nowrap;
        }}
        .item-link:hover {{
            background-color: #2980b9;
        }}
        @media (max-width: 600px) {{
            .gallery {{
                width: 95%;
            }}
            .item-content {{
                flex-direction: column;
                align-items: flex-start;
            }}
            .item-title {{
                margin-bottom: 10px;
            }}
        }}
    </style>
</head>
<body>
    <h1>相關的參考內容</h1>
    <div class="gallery">
        {gallery_items}
    </div>
</body>
</html>
    """

    gallery_item_template = """
        <div class="item">
            <div class="item-image">
                <img src="{image_url}" alt="{title}">
            </div>
            <div class="item-content">
                <div class="item-title">{title}</div>
                <a href="{pdf_url}" class="item-link" target="_blank">查看原始文件</a>
            </div>
        </div>
    """

    gallery_items = []
    for pdf in pdf_list:
        title = f"{pdf['filename']} (第 {pdf['page']} 頁)"
        item_html = gallery_item_template.format(
            image_url=pdf['image_url'],
            title=title,
            pdf_url=pdf['pdf_url']
        )
        gallery_items.append(item_html)

    gallery_content = "\n".join(gallery_items)
    full_html = html_template.format(gallery_items=gallery_content)

    return full_html
