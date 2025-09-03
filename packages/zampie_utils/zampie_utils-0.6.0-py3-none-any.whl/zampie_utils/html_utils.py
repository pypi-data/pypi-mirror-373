import os
from urllib.parse import urlparse

SERVER_URL = "http://127.0.0.1:8000/"


def is_url(s):
    try:
        result = urlparse(s)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False


def is_file(s):
    return os.path.exists(s)


def gen_td(part, enable_click_zoom=False, text_collapse_length=200):
    """
    生成HTML img标签
    :param part: 图片URL或文本内容
    :param enable_click_zoom: 是否启用点击放大功能
    :param text_collapse_length: 文本折叠长度阈值
    :return: HTML td标签字符串
    """
    part = str(part)
    if is_url(part):
        if enable_click_zoom:
            return f"<td><img src='{part}' style='width: 360px; cursor: pointer;' class='zoomable-img' onclick='showModal(this.src)'></td>\n"
        else:
            return f"<td><img src='{part}' style='width: 360px;'></td>\n"
    elif is_file(part):
        # 如果是本地文件，加上服务器地址
        img_url = f"{SERVER_URL}{part}"
        if enable_click_zoom:
            return f"<td><img src='{img_url}' style='width: 360px; cursor: pointer;' class='zoomable-img' onclick='showModal(this.src)'></td>\n"
        else:
            return f"<td><img src='{img_url}' style='width: 360px;'></td>\n"

    # 处理文本内容，支持折叠
    if len(part) > text_collapse_length:
        preview_text = part[:50]

        return f"""<td style='max-width:360px; word-break:break-all; white-space:pre-wrap;'>
            <details>
                <summary>{preview_text}...</summary>
                <div style='margin-top: 8px;'>{part}</div>
            </details>
        </td>\n"""
    else:
        # 文本不长，正常显示
        return f"<td style='max-width:360px; word-break:break-all; white-space:pre-wrap;'>{part}</td>\n"


def process(lines):
    # 生成html界面，每行一条，可视化img58_url和img60_url
    html_content = "<html><head><meta charset='utf-8'></head><body>\n"
    # html_content += "<h1>Image Generation Results</h1>\n"
    html_content += "<table border='1'>\n"
    # html_content += "<tr><th>query</th><th>caption</th><th>t1</th><th>t2</th><th>58</th><th>60</th><th>60 seed=42</th></tr>\n"
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        print(len(parts))
        html_content += "<tr>\n"
        for part in parts:
            html_content += gen_td(part)
        html_content += "</tr>\n"
    html_content += "</table>\n"
    html_content += "</body></html>\n"

    return html_content


def process_df(df):
    html_content = """<html>
<head>
    <meta charset='utf-8'>
    <style>
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
        }
        .modal-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            max-width: 90%;
            max-height: 90%;
        }
        .close {
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }
        .close:hover,
        .close:focus {
            color: #bbb;
            text-decoration: none;
            cursor: pointer;
        }
        .zoomable-img:hover {
            opacity: 0.8;
        }
        details {
            cursor: pointer;
        }
        summary {
            list-style-type: none;
            position: relative;
            padding-left: 20px;
        }
        summary::-webkit-details-marker {
            display: none;
        }
        summary::before {
            content: '▶';
            position: absolute;
            left: 0;
            color: #666;
            font-size: 12px;
        }
        details[open] summary::before {
            content: '▼';
        }
        details[open] summary {
            margin-bottom: 8px;
        }
    </style>
</head>
<body>
    <div id="imageModal" class="modal">
        <span class="close" onclick="closeModal()">&times;</span>
        <img class="modal-content" id="modalImage">
    </div>
    <script>
        function showModal(src) {
            document.getElementById('imageModal').style.display = 'block';
            document.getElementById('modalImage').src = src;
        }
        
        function closeModal() {
            document.getElementById('imageModal').style.display = 'none';
        }
        
        // 点击模态框背景关闭
        window.onclick = function(event) {
            var modal = document.getElementById('imageModal');
            if (event.target == modal) {
                closeModal();
            }
        }
        
        // ESC键关闭模态框
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                closeModal();
            }
        });
    </script>
"""
    html_content += "<table border='1'>\n"
    html_content += "<tr>\n"
    for col in df.columns:
        html_content += f"<th>{col}</th>\n"
    html_content += "</tr>\n"
    for index, row in df.iterrows():
        html_content += "<tr>\n"
        for part in row:
            html_content += gen_td(part, enable_click_zoom=True)
        html_content += "</tr>\n"
    html_content += "</table>\n"
    html_content += "</body></html>\n"
    return html_content


if __name__ == "__main__":
    # 读取保存的 DataFrame
    # file_name = "df_279_sample_rewrite_gen2.txt"
    file_name = "data_1_result.txt"
    process(file_name)
