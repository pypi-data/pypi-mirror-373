import re
import json5


def find_emojis(response):
    """
    匹配 emoji
    """

    emoji_pattern = re.compile(
        r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F"
        r"\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F"
        r"\U0001FA70-\U0001FAFF\U00002640\U00002642]",  # 添加 U+2640 和 U+2642 范围
        flags=re.UNICODE,
    )

    emojis = emoji_pattern.findall(response)
    return emojis


def find_expressings(response):
    """
    匹配 emoji
    """

    expression_pattern = re.compile(r"<.*?>")

    # 查找匹配项
    expressions = expression_pattern.findall(response)
    return expressions


def remove_blank_lines(dialog):
    """
    Args:
        dialog: str, dialog content
    """
    dialog = dialog.strip()
    dialog_list = []
    for line in dialog.split("\n"):
        if not line:
            continue
        dialog_list.append(line)

    dialog = "\n".join(dialog_list)

    return dialog


def find_chinese(text):
    """
    提取文本中的中文字符

    Args:
        text: str, 输入文本

    Returns:
        list: 包含所有中文字符的列表
    """
    chinese_pattern = re.compile(r"[\u4e00-\u9fff]+", flags=re.UNICODE)
    chinese_chars = chinese_pattern.findall(text)
    return "".join(chinese_chars)


def load_json_block(json_text):
    """解析大模型输出的JSON代码块

    Args:
        json_text (str): 大模型返回的文本，可能包含JSON代码块

    Returns:
        dict: 解析后的字典，如果解析失败返回None
    """
    # 先判断是否包含```json代码块
    if "```json" in json_text:
        try:
            json_pattern = r"```json\s*(.*?)\s*```"
            match = re.search(json_pattern, json_text, re.DOTALL)
            if match:
                json_content = match.group(1).strip()
                return json5.loads(json_content)
        except Exception as e:
            print(f"解析```json代码块失败: {e}")
            return ""

    # 再判断是否包含普通```代码块
    elif "```" in json_text:
        try:
            code_pattern = r"```\s*(.*?)\s*```"
            match = re.search(code_pattern, json_text, re.DOTALL)
            if match:
                json_content = match.group(1).strip()
                return json5.loads(json_content)
        except Exception as e:
            print(f"解析```代码块失败: {e}")
            return ""

    # 最后尝试直接解析
    else:
        try:
            return json5.loads(json_text)
        except Exception as e:
            print(f"直接解析JSON失败: {e}")
            return ""

    print(f"无法解析JSON: {json_text}")
    return ""
