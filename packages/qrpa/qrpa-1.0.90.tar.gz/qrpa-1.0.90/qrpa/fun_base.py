import inspect
import os
import traceback
import socket
import hashlib
import shutil

from datetime import datetime

from .wxwork import WxWorkBot

from .RateLimitedSender import RateLimitedSender

from typing import TypedDict

# 自定义错误类型，继承自 Exception
class NetWorkIdleTimeout(Exception):
    """这是一个自定义错误类型"""
    pass

# 定义一个 TypedDict 来提供配置结构的类型提示

class ZiNiao(TypedDict):
    company: str
    username: str
    password: str

class Config(TypedDict):
    wxwork_bot_exception: str
    ziniao: ZiNiao
    auto_dir: str

def log(*args, **kwargs):
    """封装 print 函数，使其行为与原 print 一致，并写入日志文件"""
    stack = inspect.stack()
    fi = stack[1] if len(stack) > 1 else None
    log_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][{os.path.basename(fi.filename) if fi else 'unknown'}:{fi.lineno if fi else 0}:{fi.function if fi else 'unknown'}] " + " ".join(map(str, args))

    print(log_message, **kwargs)

def hostname():
    return socket.gethostname()

# ================= WxWorkBot 限频异常发送 =================
def send_exception(msg=None):
    """
    发送异常到 WxWorkBot，限制发送频率，支持异步批量
    """
    # 首次调用时初始化限频发送器
    if not hasattr(send_exception, "_wx_sender"):
        def wxwork_bot_send(message):
            bot_id = os.getenv('wxwork_bot_exception', 'ee5a048a-1b9e-41e4-9382-aa0ee447898e')
            WxWorkBot(bot_id).send_text(message)

        send_exception._wx_sender = RateLimitedSender(
            sender_func=wxwork_bot_send,
            interval=30,  # 10 秒发一次
        )

    # 构造异常消息
    error_msg = f'【{hostname()}】{datetime.now():%Y-%m-%d %H:%M:%S}\n{msg}\n'
    error_msg += f'{traceback.format_exc()}'
    print(error_msg)

    # 异步发送
    send_exception._wx_sender.send(error_msg)
    return error_msg

def get_safe_value(data, key, default=0):
    value = data.get(key)
    return default if value is None else value

def md5_string(s):
    # 需要先将字符串编码为 bytes
    return hashlib.md5(s.encode('utf-8')).hexdigest()

# 将windows文件名不支持的字符替换成下划线
def sanitize_filename(filename):
    # Windows 文件名非法字符
    illegal_chars = r'\/:*?"<>|'
    for char in illegal_chars:
        filename = filename.replace(char, '_')

    # 去除首尾空格和点
    filename = filename.strip(' .')

    # 替换连续多个下划线为单个
    filename = '_'.join(filter(None, filename.split('_')))

    return filename

def add_https(url):
    if url and url.startswith('//'):
        return 'https:' + url
    return url

def create_file_path(file_path):
    dir_name = os.path.dirname(file_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)  # 递归创建目录
    return file_path

def copy_file(source, destination):
    try:
        shutil.copy2(source, destination)
        print(f"文件已复制到 {destination}")
    except FileNotFoundError:
        print(f"错误：源文件 '{source}' 不存在")
    except PermissionError:
        print(f"错误：没有权限复制到 '{destination}'")
    except Exception as e:
        print(f"错误：发生未知错误 - {e}")

def get_file_size(file_path, human_readable=False):
    """
    获取文件大小

    :param file_path: 文件路径
    :param human_readable: 是否返回可读格式（KB, MB, GB）
    :return: 文件大小（字节数或可读格式）
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    size_bytes = os.path.getsize(file_path)

    if not human_readable:
        return size_bytes

    # 转换为可读单位
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

def calculate_star_symbols(rating):
    """
    计算星级对应的符号组合（独立评分逻辑函数）
    参数:
    rating (int): 标准化评分（0-5）
    返回:
    str: 星级符号字符串（如★★★⭐☆）
    """
    full_stars = int(rating)
    empty_stars = 5 - full_stars
    star_string = '★' * full_stars
    star_string += '☆' * empty_stars
    return star_string

def remove_columns(matrix, indices):
    """
    过滤二维列表，移除指定索引的列

    参数:
        matrix: 二维列表
        indices: 需要移除的列索引列表

    返回:
        过滤后的二维列表
    """
    # 创建要保留的索引集合（排除需要移除的索引）
    indices_to_keep = set(range(len(matrix[0]))) - set(indices)

    # 遍历每行，只保留不在indices中的列
    return [[row[i] for i in indices_to_keep] for row in matrix]

def filter_columns(matrix, indices):
    """
    过滤二维列表，只保留指定索引的列

    参数:
        matrix: 二维列表
        indices: 需要保留的列索引列表

    返回:
        过滤后的二维列表
    """
    # 转置矩阵，获取每一列
    columns = list(zip(*matrix))

    # 只保留指定索引的列
    filtered_columns = [columns[i] for i in indices]

    # 将过滤后的列转回二维列表
    return [list(row) for row in zip(*filtered_columns)]

# # 示例使用
# matrix = [
#     [1, 2, 3, 4],
#     [5, 6, 7, 8],
#     [9, 10, 11, 12]
# ]
#
# # 只保留索引为 0 和 2 的列
# filtered = filter_columns(matrix, [0, 2])
# print(filtered)  # 输出: [[1, 3], [5, 7], [9, 11]]

def add_column_to_2d_list(data, new_col, index=None):
    """
    给二维列表增加一列数据

    :param data: 原始二维列表，例如 [[1, 2], [3, 4]]
    :param new_col: 要添加的新列数据，例如 [10, 20]
    :param index: 插入位置，默认为最后一列之后；支持负数索引
    :return: 增加新列后的二维列表
    """
    if not data:
        raise ValueError("原始数据为空")
    if len(data) != len(new_col):
        raise ValueError("新列长度必须与原始数据的行数相等")

    new_data = []
    for i, row in enumerate(data):
        row = list(row)  # 防止修改原始数据
        insert_at = index if index is not None else len(row)
        row.insert(insert_at, new_col[i])
        new_data.append(row)
    return new_data

def add_prefixed_column(data, header, value):
    """
    给二维列表增加第一列，第一行为 header，后面为 value。

    :param data: 原始二维列表
    :param header: 新列的标题
    :param value: 新列内容（相同值）
    :return: 增加新列后的二维列表
    """
    if not data:
        raise ValueError("原始数据不能为空")

    new_col = [header] + [value] * (len(data) - 1)
    return [[new_col[i]] + row for i, row in enumerate(data)]

def add_suffixed_column(data, header, value):
    """
    给二维列表增加第一列，第一行为 header，后面为 value。

    :param data: 原始二维列表
    :param header: 新列的标题
    :param value: 新列内容（相同值）
    :return: 增加新列后的二维列表
    """
    if not data:
        raise ValueError("原始数据不能为空")

    new_col = [header] + [value] * (len(data) - 1)
    return [row + [new_col[i]] for i, row in enumerate(data)]

def merge_2d_lists_keep_first_header(data1, data2):
    """
    合并两个二维列表，只保留第一个列表的标题（即第一行）。

    :param data1: 第一个二维列表（包含标题）
    :param data2: 第二个二维列表（包含标题）
    :return: 合并后的二维列表
    """
    if not data1 or not isinstance(data1, list):
        raise ValueError("data1 不能为空并且必须是二维列表")
    if not data2 or not isinstance(data2, list):
        raise ValueError("data2 不能为空并且必须是二维列表")

    header = data1[0]
    rows1 = data1[1:]
    rows2 = data2[1:]

    return [header] + rows1 + rows2

def insert_total_row(data, row_index=1, label="合计"):
    """
    在指定行插入一行，第一列为 label，其余为空字符串。

    :param data: 原始二维列表
    :param row_index: 插入位置，默认插在第二行（索引1）
    :param label: 第一列的标签内容，默认为 "合计"
    :return: 新的二维列表
    """
    if not data or not isinstance(data, list):
        raise ValueError("data 不能为空并且必须是二维列表")

    num_cols = len(data[0])
    new_row = [label] + [""] * (num_cols - 1)

    return data[:row_index] + [new_row] + data[row_index:]

def insert_empty_column_after(data, col_index, new_header="单价成本"):
    """
    在二维列表中指定列的后面插入一个新列，标题为 new_header，其余内容为空字符串。

    :param data: 原始二维列表
    :param col_index: 要插入的位置（在该列后面插入）
    :param new_header: 新列的标题
    :return: 新的二维列表
    """
    if not data or not isinstance(data, list):
        raise ValueError("data 不能为空且必须是二维列表")

    new_data = []
    for i, row in enumerate(data):
        row = list(row)  # 复制避免修改原数据
        insert_value = new_header if i == 0 else ""
        row.insert(col_index + 1, insert_value)
        new_data.append(row)

    return new_data

def insert_empty_column_after_column_name(data, target_col_name, new_header="单价成本"):
    """
    在指定列名对应的列后面插入一个新列，标题为 new_header，其余行为空字符串。

    :param data: 原始二维列表
    :param target_col_name: 要在哪一列之后插入（通过列标题匹配）
    :param new_header: 插入的新列标题
    :return: 新的二维列表
    """
    if not data or not isinstance(data, list):
        raise ValueError("data 不能为空且必须是二维列表")

    header = data[0]
    if target_col_name not in header:
        raise ValueError(f"找不到列名：{target_col_name}")

    col_index = header.index(target_col_name)

    new_data = []
    for i, row in enumerate(data):
        row = list(row)  # 防止修改原始数据
        insert_value = new_header if i == 0 else ""
        row.insert(col_index + 1, insert_value)
        new_data.append(row)

    return new_data
