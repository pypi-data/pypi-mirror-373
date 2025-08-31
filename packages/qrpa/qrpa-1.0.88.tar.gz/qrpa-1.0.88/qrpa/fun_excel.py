from pathlib import Path
import xlwings as xw
import requests
from PIL import Image  # 需要安装 Pillow 库：pip install pillow
import os
import json
from urllib.parse import urlparse
import time
import random
import traceback
import concurrent.futures
from collections import defaultdict
import threading
from playwright.sync_api import sync_playwright
import psutil

from .fun_base import log, sanitize_filename, create_file_path, copy_file, add_https, send_exception

excel_color_index = {
    "无色(自动)"   : 0,  # 透明/默认
    "黑色"         : 1,  # #000000
    "白色"         : 2,  # #FFFFFF
    "红色"         : 3,  # #FF0000
    "绿色"         : 4,  # #00FF00
    "蓝色"         : 5,  # #0000FF
    "黄色"         : 6,  # #FFFF00
    "粉红色"       : 7,  # #FF00FF
    "青绿色"       : 8,  # #00FFFF
    "深红色"       : 9,  # #800000
    "深绿色"       : 10,  # #008000
    "深蓝色"       : 11,  # #000080
    "橄榄色(深黄)" : 12,  # #808000
    "紫色"         : 13,  # #800080
    "蓝绿色(水色)" : 14,  # #008080
    "灰色（25%）"    : 15,  # #808080
    "浅灰色(12.5%)": 16,  # #C0C0C0
    # 17-19：系统保留（通常不可用）
    "深玫瑰红"     : 20,  # #FF99CC
    "深金色"       : 21,  # #FFCC99
    "深橙红色"     : 22,  # #FF6600
    "深灰色(50%)"  : 23,  # #666666
    "深紫色"       : 24,  # #660066
    "蓝灰色"       : 25,  # #3366FF
    "浅蓝色"       : 26,  # #99CCFF
    "浅紫色"       : 27,  # #CC99FF
    "浅青绿色"     : 28,  # #99FFFF
    "浅绿色"       : 29,  # #CCFFCC
    "浅黄色"       : 30,  # #FFFFCC
    "浅橙红色"     : 31,  # #FFCC99
    "玫瑰红"       : 32,  # #FF9999
    "浅天蓝色"     : 33,  # #99CCFF
    "浅海绿色"     : 34,  # #99FFCC
    "浅草绿色"     : 35,  # #CCFF99
    "浅柠檬黄"     : 36,  # #FFFF99
    "浅珊瑚色"     : 37,  # #FFCC99
    "浅玫瑰红"     : 38,  # #FF9999
    "棕褐色"       : 39,  # #CC9966
    "浅棕褐色"     : 40,  # #FFCC99
    "浅橄榄色"     : 41,  # #CCCC99
    "浅蓝灰色"     : 42,  # #9999FF
    "浅灰绿色"     : 43,  # #99CC99
    "金色"         : 44,  # #FFCC00
    "浅橙黄色"     : 45,  # #FFCC66
    "橙红色"       : 46,  # #FF6600
    "深天蓝色"     : 47,  # #0066CC
    "深海绿色"     : 48,  # #009966
    "深草绿色"     : 49,  # #669900
    "深柠檬黄"     : 50,  # #CCCC00
    "深珊瑚色"     : 51,  # #FF9933
    "深玫瑰红(暗)" : 52,  # #CC6699
    "深棕褐色"     : 53,  # #996633
    "深橄榄色"     : 54,  # #666600
    "深蓝灰色"     : 55,  # #333399
}

def aggregate_by_column(data, group_by_col_name):
    """
    根据指定列名对二维表数据聚合：
    - 数字列求和
    - 字符串列用换行符拼接

    :param data: 二维列表，第一行为表头
    :param group_by_col_name: 要聚合的列名，如 "店长"
    :return: 聚合后的二维列表
    """
    headers = data[0]
    group_index = headers.index(group_by_col_name)
    grouped = defaultdict(list)

    # 按 group_by 列聚合行
    for row in data[1:]:
        key = row[group_index]
        grouped[key].append(row)

    result = [headers]

    for key, rows in grouped.items():
        agg_row = []
        for col_idx in range(len(headers)):
            col_values = [r[col_idx] for r in rows]
            # 聚合字段
            if col_idx == group_index:
                agg_value = key
            else:
                # 尝试将值转为 float，如果成功就求和，否则拼接
                try:
                    nums = [float(v) for v in col_values if
                            isinstance(v, (int, float)) or (isinstance(v, str) and v.strip() != '')]
                    agg_value = sum(nums)
                except ValueError:
                    # 拼接字符串（去重可加 set）
                    strings = [str(v).strip() for v in col_values if str(v).strip()]
                    agg_value = '\n'.join(strings)
            agg_row.append(agg_value)
        result.append(agg_row)

    return result

def set_cell_prefix_red(cell, n, color_name):
    """
    将指定 Excel 单元格内容的前 n 个字符设置为红色。
    """
    text = str(cell.value)

    if not text or n <= 0:
        return

    n = min(n, len(text))  # 避免超出范围

    try:
        # 设置前n个字符为红色
        cell.api.Characters(1, n).Font.ColorIndex = excel_color_index[color_name]
    except Exception as e:
        print(f"设置字体颜色失败: {e}")

def wrap_column(sheet, columns=None, WrapText=True):
    if columns is None:
        return
    used_range_col = sheet.range('A1').expand('right')
    for j, cell in enumerate(used_range_col):
        col = j + 1
        col_name = index_to_column_name(col)
        col_val = sheet.range(f'{col_name}1').value
        if col_val is None:
            continue
        for c in columns:
            if c in col_val:
                log(f'设置[{c}] 换行 {WrapText}')
                sheet.range(f'{col_name}:{col_name}').api.WrapText = WrapText

def sort_by_column(data, col_index, header_rows=2, reverse=True):
    if not data or header_rows >= len(data):
        return data

    try:
        header = data[:header_rows]
        new_data_sorted = data[header_rows:]

        def get_key(row):
            value = row[col_index]
            if isinstance(value, (int, float)):  # 已经是数字
                return (0, value)  # 用元组排序，数字优先
            try:
                return (0, float(value))  # 尝试转数字
            except (ValueError, TypeError):
                return (1, str(value))  # 转不了就按字符串排

        new_data_sorted.sort(key=get_key, reverse=reverse)
        return header + new_data_sorted
    except IndexError:
        print(f"Error: Column index {col_index} out of range")
        return data

def column_exists(sheet, column_name, header_row=1):
    """
    检查工作表中是否存在指定列名
    :param sheet: xlwings Sheet 对象
    :param column_name: 要查找的列名
    :param header_row: 表头所在行号，默认为1
    :return: 如果存在返回True，否则返回False
    """
    # 获取表头行所有值
    header_values = sheet.range((header_row, 1), (header_row, sheet.used_range.last_cell.column)).value

    return column_name in header_values

def merge_by_column_v2(sheet, column_name, other_columns):
    log('正在处理合并单元格')
    # 最好放到 open_excel 后面,不然容易出错
    col_letter = find_column_by_data(sheet, 1, column_name)
    if col_letter is None:
        log(f'未找到合并的列名: {column_name}')
        return

    # 更安全的数据获取方式，确保获取完整的数据范围
    last_row = get_last_row(sheet, col_letter)
    data = sheet.range(f'{col_letter}1:{col_letter}{last_row}').value
    
    # 确保data是列表格式
    if not isinstance(data, list):
        data = [data]
    
    log(f'数据范围: {col_letter}1:{col_letter}{last_row}, 数据长度: {len(data)}')
    
    start_row = 2  # 从第2行开始，跳过表头
    merge_row_ranges = []  # 用来存储需要合并的行范围 (start_row, end_row)

    # 获取所有需要合并的列
    all_columns = [col_letter]  # 主列
    for col in other_columns:
        col_name = find_column_by_data(sheet, 1, col)
        if col_name:
            all_columns.append(col_name)
    
    log(f'需要合并的列: {all_columns}')

    # 遍历数据行，从第3行开始比较（因为第1行是表头，第2行是第一个数据行）
    for row in range(3, len(data) + 1):
        log(f'查找 {row}/{len(data)}, 当前值: {data[row-1] if row-1 < len(data) else "超出范围"}, 前一个值: {data[row-2] if row-2 < len(data) else "超出范围"}')
        
        # 检查值是否发生变化
        if row <= len(data) and data[row - 1] != data[row - 2]:
            # 值发生变化，处理前一组
            end_row = row - 1
            log(f'添加合并范围: {start_row} 到 {end_row}')
            merge_row_ranges.append((start_row, end_row))
            start_row = row

    # 处理最后一组数据（循环结束后，start_row 到数据末尾）
    if start_row <= len(data):
        end_row = len(data)
        log(f'处理最后一组: {start_row} 到 {end_row}')
        merge_row_ranges.append((start_row, end_row))

    log(f'行合并范围: {merge_row_ranges}')
    
    # 对每个行范围，在所有指定列中执行合并
    for start_row, end_row in merge_row_ranges:
        if start_row < end_row:  # 只有当开始行小于结束行时才合并（多行）
            for col_name in all_columns:
                log(f'处理 {col_name}{start_row}:{col_name}{end_row} merge')
                sheet.range(f'{col_name}{start_row}:{col_name}{end_row}').merge()
        elif start_row == end_row:
            log(f'单行数据无需合并: {start_row} 到 {end_row}')
        else:
            log(f'跳过无效合并范围: {start_row} 到 {end_row}')

def merge_by_column(sheet, column_name, other_columns):
    log('正在处理合并单元格')
    # 最好放到 open_excel 后面,不然容易出错
    data = sheet.range('A1').expand('table').value
    col_letter = find_column_by_data(sheet, 1, column_name)
    if col_letter is None:
        log(f'未找到合并的列名: {column_name}')
        return
    col_index = column_name_to_index(col_letter)
    start_row = 1
    for row in range(2, len(data) + 1):
        log(f'{row}/{len(data)}')
        if data[row - 1][col_index] != data[row - 2][col_index]:
            if row - start_row > 1:
                sheet.range(f'{col_letter}{start_row}:{col_letter}{row - 1}').merge()
                for col in other_columns:
                    col_name = find_column_by_data(sheet, 1, col)
                    if col_name is not None:
                        sheet.range(f'{col_name}{start_row}:{col_name}{row - 1}').merge()
            start_row = row

    if len(data) - start_row > 1:
        sheet.range(f'{col_letter}{start_row}:{col_letter}{len(data)}').merge()
        for col in other_columns:
            col_name = find_column_by_data(sheet, 1, col)
            if col_name is not None:
                sheet.range(f'{col_name}{start_row}:{col_name}{len(data)}').merge()

def merge_column_v2(sheet, columns):
    if columns is None:
        return

    # 缓存所有列的字母
    col_letters = {col: find_column_by_data(sheet, 1, col) for col in columns}
    merge_ranges = []  # 用来存储所有待合并的单元格范围

    for c, col_letter in col_letters.items():
        if col_letter is None:
            continue

        data = sheet.range(f'{col_letter}1').expand('table').value
        start_row = 1

        for row in range(2, len(data) + 1):
            log(f'查找 {row}/{len(data)}')  # 如果数据量非常大，这里的日志会影响性能，可以考虑优化
            if data[row - 1][0] != data[row - 2][0]:
                if row - start_row > 1:
                    merge_ranges.append((col_letter, start_row, row - 1))
                start_row = row

        if len(data) - start_row > 1:
            merge_ranges.append((col_letter, start_row, len(data)))

    # 批量合并单元格
    for col_letter, start, end in merge_ranges:
        log(f'处理 {col_letter}{start}:{col_letter}{end} merge')
        sheet.range(f'{col_letter}{start}:{col_letter}{end}').merge()

# 按列相同值合并
def merge_column(sheet, columns):
    # 最后放到 open_excel 后面,不然容易出错
    if columns is None:
        return
    for c in columns:
        col_letter = find_column_by_data(sheet, 1, c)
        if col_letter is None:
            continue
        data = sheet.range(f'{col_letter}1').expand('table').value
        # col_index = column_name_to_index(col_letter)
        col_index = 0
        start_row = 1
        for row in range(2, len(data) + 1):
            if data[row - 1][col_index] != data[row - 2][col_index]:
                if row - start_row > 1:
                    sheet.range(f'{col_letter}{start_row}:{col_letter}{row - 1}').merge()
                start_row = row

        if len(data) - start_row > 1:
            sheet.range(f'{col_letter}{start_row}:{col_letter}{len(data)}').merge()

def remove_excel_columns(sheet, columns):
    # 获取第一行(标题行)的所有值
    header_row = sheet.range('1:1').value

    # 获取要删除的列的索引(从1开始)
    columns_to_remove = []
    for i, header in enumerate(header_row, start=1):
        if header in columns:
            columns_to_remove.append(i)

    # 如果没有找到要删除的列
    if not columns_to_remove:
        log("警告: 未找到任何匹配的列")
        return False

    # 按从右到左的顺序删除列(避免索引变化问题)
    for col_idx in sorted(columns_to_remove, reverse=True):
        col_letter = xw.utils.col_name(col_idx)
        sheet.range(f'{col_letter}:{col_letter}').delete()

    print(f"成功移除列: {columns_to_remove}")
    return True

def delete_sheet_if_exists(wb, sheet_name):
    """
    如果工作簿中存在指定名称的工作表，则将其删除。

    参数:
    wb : xw.Book
        xlwings 的工作簿对象。
    sheet_name : str
        要检查并删除的工作表名称。
    """
    sheet_names = [s.name for s in wb.sheets]
    if sheet_name in sheet_names:
        wb.sheets[sheet_name].delete()
        wb.save()
        print(f"已删除 Sheet: {sheet_name}")
    else:
        print(f"Sheet 不存在: {sheet_name}")

# 水平对齐：
# -4108：居中
# -4131：左对齐
# -4152：右对齐
# 垂直对齐：
# -4108：居中
# -4160：顶部对齐
# -4107：底部对齐
def index_to_column_name(index):
    """
    将列索引转换为Excel列名。
    例如：1 -> 'A', 2 -> 'B', 26 -> 'Z', 27 -> 'AA'
    """
    column_name = ''
    while index > 0:
        index -= 1
        remainder = index % 26
        column_name = chr(65 + remainder) + column_name
        index = index // 26
    return column_name

# # 示例：将列索引转换为列名
# log(index_to_column_name(1))   # 输出: 'A'
# log(index_to_column_name(26))  # 输出: 'Z'
# log(index_to_column_name(27))  # 输出: 'AA'
# log(index_to_column_name(52))  # 输出: 'AZ'

def column_name_to_index(column_name):
    """
    将Excel列名转换为列索引。
    例如：'A' -> 1, 'B' -> 2, 'Z' -> 26, 'AA' -> 27
    例如：'A' -> 0, 'B' -> 1, 'Z' -> 25, 'AA' -> 26
    """
    index = 0
    for char in column_name:
        index = index * 26 + (ord(char.upper()) - 64)
    return index - 1

# # 示例：将列名转换为列索引
# log(column_name_to_index('A'))   # 输出: 1
# log(column_name_to_index('Z'))   # 输出: 26
# log(column_name_to_index('AA'))  # 输出: 27
# log(column_name_to_index('AZ'))  # 输出: 52

def find_row_by_data(sheet, column, target_value):
    """
    查找指定数据在某一列中第一次出现的行号。

    :param sheet: xlwings 的 Sheet 对象。
    :param column: 列名（如 'A', 'B', 'C'）。
    :param target_value: 要查找的数据。
    :return: 数据所在的行号（从1开始），如果未找到返回 None。
    """
    # 获取指定列的所有数据
    column_data = sheet.range(f'{column}1').expand('down').value

    # 遍历数据，查找目标值
    for i, value in enumerate(column_data, start=1):
        if value == target_value:
            return i

    # 如果未找到，返回 None
    return None

def find_column_by_data(sheet, row, target_value):
    """
    查找指定数据在某一行中第一次出现的列名，包括隐藏的列。

    :param sheet: xlwings 的 Sheet 对象。
    :param row: 行号（如 1, 2, 3）。
    :param target_value: 要查找的数据。
    :return: 数据所在的列名（如 'A', 'B', 'C'），如果未找到返回 None。
    """
    last_col = sheet.used_range.last_cell.column  # 获取最后一列索引

    for col in range(1, last_col + 1):  # 遍历所有列
        cell = sheet.cells(row, col)

        # 检查目标值是否匹配
        if cell.value == target_value:
            return xw.utils.col_name(col)  # 返回列名

    return None  # 未找到返回 None

def find_column_by_data_old(sheet, row, target_value):
    """
    查找指定数据在某一行中第一次出现的列名。

    :param sheet: xlwings 的 Sheet 对象。
    :param row: 行号（如 1, 2, 3）。
    :param target_value: 要查找的数据。
    :return: 数据所在的列名（如 'A', 'B', 'C'），如果未找到返回 None。
    """
    # 获取指定行的所有数据
    row_data = sheet.range(f'A{row}').expand('right').value

    # 遍历数据，查找目标值
    for i, value in enumerate(row_data):
        if value == target_value:
            # 将列索引转换为列名
            return xw.utils.col_name(i + 1)

    # 如果未找到，返回 None
    return None

def set_print_area(sheet, print_range, pdf_path=None, fit_to_width=True, landscape=False):
    """
    设置指定sheet的打印区域和打印布局为适合A4宽度打印。

    :param sheet: xlwings 的 Sheet 对象
    :param print_range: 要设置为打印区域的字符串范围，比如 "A1:G50"
    :param fit_to_width: 是否缩放以适应A4纸宽度
    :param landscape: 是否横向打印（默认纵向）
    """
    # 设置打印区域
    sheet.api.PageSetup.PrintArea = print_range

    # 取消打印标题行/列
    sheet.api.PageSetup.PrintHeadings = False

    # 取消打印网格线
    sheet.api.PageSetup.PrintGridlines = False

    # 打印方向（横向或纵向）
    sheet.api.PageSetup.Orientation = 2 if landscape else 1  # 2: Landscape, 1: Portrait

    # 设置纸张大小为 A4
    sheet.api.PageSetup.PaperSize = 9  # 9: xlPaperA4

    # 设置页边距
    sheet.api.PageSetup.LeftMargin = 20  # 上边距
    sheet.api.PageSetup.RightMargin = 20  # 上边距
    sheet.api.PageSetup.TopMargin = 20  # 上边距
    sheet.api.PageSetup.BottomMargin = 20  # 上边距

    if fit_to_width:
        # 适应一页宽度，多页高度
        sheet.api.PageSetup.Zoom = False
        sheet.api.PageSetup.FitToPagesWide = 1
        sheet.api.PageSetup.FitToPagesTall = False  # 高度不限制，可以分页
    else:
        # 使用默认缩放（不建议用于A4布局控制）
        sheet.api.PageSetup.Zoom = 100

    # 可选：居中打印
    sheet.api.PageSetup.CenterHorizontally = True
    sheet.api.PageSetup.CenterVertically = False

    # 导出打印区域为PDF
    if pdf_path is not None:
        sheet.to_pdf(path=pdf_path)
        log(f"PDF已成功生成：{pdf_path}")

def minimize(app):
    # 让 Excel 窗口最小化
    app.api.WindowState = -4140  # -4140 对应 Excel 中的 xlMinimized 常量

def insert_fixed_scale_image_v2(sheet, cell, image_path):
    """
    将图片插入到指定单元格中，自动缩放以适应单元格尺寸，但保持宽高比例不变。
    - sheet: xlwings 工作表对象
    - cell: 单元格地址，如 'C3'
    - image_path: 图片路径
    """
    if not image_path:
        return None

    target_range = sheet.range(cell)
    if target_range.merge_cells:
        target_range = target_range.merge_area

    cell_value = target_range.value

    try:
        # 获取单元格的宽高（单位是 points）
        cell_width = target_range.width
        cell_height = target_range.height

        # 获取图片实际尺寸（像素），并计算比例
        with Image.open(image_path) as img:
            img_width_px, img_height_px = img.size

        # 计算图片的实际宽高比（防止变形）
        img_ratio = img_width_px / img_height_px
        cell_ratio = cell_width / cell_height

        # 设置缩放因子，留出空隙（例如，0.9 表示图片尺寸为原来的 90%）
        padding_factor = 0.9

        # 计算缩放倍数（确保图片不超过单元格大小）
        if img_ratio > cell_ratio:
            # 宽度限制
            scale = cell_width / img_width_px * padding_factor
            img_width_resized = cell_width * padding_factor
            img_height_resized = img_height_px * scale
        else:
            # 高度限制
            scale = cell_height / img_height_px * padding_factor
            img_width_resized = img_width_px * scale
            img_height_resized = cell_height * padding_factor

        # 插入图片
        pic = sheet.pictures.add(image_path, left=target_range.left, top=target_range.top, width=img_width_resized, height=img_height_resized)

        # 居中对齐
        pic.left = target_range.left + (target_range.width - pic.width) / 2
        pic.top = target_range.top + (target_range.height - pic.height) / 2

        # 清除单元格文字
        target_range.value = None

        return pic

    except Exception as e:
        target_range.value = cell_value
        send_exception()

    return None

def insert_fixed_scale_image(sheet, cell, image_path, scale=1.0):
    """
    按固定比例放大图片并插入到单元格
    insert_fixed_scale_image(sheet, 'C1', img_path, 1.5)
    参数:
    - sheet: xlwings工作表对象
    - cell: 目标单元格地址
    - image_path: 图片文件路径
    - scale: 缩放倍数(2.0表示放大两倍)
    """
    if not image_path:
        return None

    # 获取目标单元格范围
    target_range = sheet.range(cell)

    if target_range.merge_cells:
        target_range = target_range.merge_area

    cell_value = target_range.value
    try:
        # 插入图片并缩放
        pic = sheet.pictures.add(image_path, left=target_range.left, top=target_range.top, scale=scale)

        # 调整位置使其居中(可选)
        pic.left = target_range.left + (target_range.width - pic.width) / 2
        pic.top = target_range.top + (target_range.height - pic.height) / 2

        target_range.value = None

        return pic
    except Exception as e:
        target_range.value = cell_value
        send_exception()

    return None

def InsertImageV2(sheet, columns=None, platform='shein', img_width=150, img_save_key=None, dir_name=None, cell_height_with_img=False, start_row=2):
    if not columns:
        return

    minimize(sheet.book.app)

    # 清空所有图片
    clear_all_pictures(sheet)

    # 获取每列图片列的列号，并设置列宽
    col_letter_map = {}
    for img_col in columns:
        col_letter = find_column_by_data(sheet, 1, img_col)
        if col_letter is not None:
            col_letter_map[img_col] = col_letter
            # 下载图片
            log(f'批量下载图片: {img_col} => {col_letter}')
            last_row = get_last_row(sheet, col_letter)
            images = sheet.range(f'{col_letter}2:{col_letter}{last_row}').value
            images = images if isinstance(images, list) else [images]
            download_images_concurrently(images, platform)

    # 任意一个列作为主参考列，用来确定行数
    if not col_letter_map:
        return

    ref_col_letter = next(iter(col_letter_map.values()))
    last_row = get_last_row(sheet, ref_col_letter)

    img_key_letter = find_column_by_data(sheet, 1, img_save_key)

    # 预计算所有单元格的合并区域信息 (优化点1)
    area_map = {}
    for row in range(start_row, last_row + 1):
        log(f'计算 {row}/{last_row}')  # 如果数据量非常大，这里的日志会影响性能，可以考虑优化
        for col_letter in col_letter_map.values():
            cell_ref = f'{col_letter}{row}'
            cell_range = sheet.range(cell_ref)
            cell_address = cell_range.address

            if cell_range.merge_cells:
                cell_range = cell_range.merge_area
                cell_address = cell_range.address

            if cell_address not in area_map:
                # 计算合并区域的宽高和位置
                cell_width = cell_range.width
                cell_height = cell_range.height

                # 调整列宽和行高
                if cell_width < img_width:
                    cell_range.column_width = img_width / 6.1

                # 这一行暂时先自动控制宽度
                cell_range.column_width = img_width / 6.1

                if cell_height < img_width:
                    cell_range.row_height = max(150 / 8, img_width / cell_range.rows.count)

                if cell_height_with_img:
                    cell_range.row_height = img_width

                # 计算居中位置
                top = cell_range.top + (cell_range.height - img_width) / 2
                left = cell_range.left + (cell_range.width - img_width) / 2

                area_map[cell_address] = {
                    'top'      : top,
                    'left'     : left,
                    'width'    : img_width,
                    'cell_list': [c.address for c in cell_range]
                }

    # 处理图片插入 (优化点2)
    for row in range(start_row, last_row + 1):
        for img_col_name, col_letter in col_letter_map.items():
            cell_ref = f'{col_letter}{row}'
            cell_range = sheet.range(cell_ref)
            cell_address = cell_range.address

            # 检查合并单元格 (使用预计算的信息)
            if cell_range.merge_cells and cell_address in area_map[cell_range.merge_area.address]['cell_list'][1:]:
                continue

            if cell_range.merge_cells:
                cell_range = cell_range.merge_area
                cell_address = cell_range.address

            # 使用预计算的位置信息
            top = area_map[cell_address]['top']
            left = area_map[cell_address]['left']
            width = area_map[cell_address]['width']

            # 获取图片链接
            if cell_range.merge_cells:
                img_url = cell_range.value[0]
            else:
                img_url = cell_range.value

            if img_url:
                if img_key_letter is not None:
                    image_dir = Path(f'{os.getenv('auto_dir')}/image') / dir_name
                    extension = Path(img_url).suffix
                    filename = str(sheet.range(f'{img_key_letter}{row}').value)
                    img_save_path = image_dir / f"{sanitize_filename(filename)}{extension}"
                else:
                    img_save_path = None

                img_path = download_img_v2(img_url, platform, img_save_path)
                log(f'插入图片 {sheet.name} [{img_col_name}] {row}/{last_row} {img_path}')
                if not img_path:
                    log('跳过:', img_path, img_url)
                    continue
                cell_value = cell_range.value

                # 优化图片插入函数调用 (优化点3)
                try:
                    # 使用预计算的位置直接插入图片
                    sheet.pictures.add(img_path, top=top + 2, left=left + 2, width=width - 4, height=width - 4)
                    cell_range.value = None
                except Exception as e:
                    # 插入图片失败恢复链接地址
                    cell_range.value = cell_value
                    send_exception()
            else:
                log(f'图片地址不存在 [{img_col_name}] : 第{row}行')

def download_images_concurrently(image_urls, platform='shein', img_save_dir=None):
    # 使用线程池执行并发下载
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # 使用 lambda 函数同时传递 url 和 img_save_path
        results = list(executor.map(lambda url: download_img_v2(url, platform, img_save_path=img_save_dir), image_urls))
    return results

def download_img_by_chrome(image_url, save_name):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # 运行时可以看到浏览器
        context = browser.new_context()
        page = context.new_page()
        # 直接通过Playwright下载图片
        response = page.request.get(image_url)
        with open(save_name, 'wb') as f:
            f.write(response.body())  # 将下载的内容保存为文件
        log(f"图片已通过chrome下载并保存为:{save_name}")
        # 关闭浏览器
        browser.close()
    return save_name

def download_img_v2(image_url, platform='shein', img_save_path=None):
    image_url = add_https(image_url)
    if image_url is None or 'http' not in image_url:
        return False

    image_dir = Path(f'{os.getenv('auto_dir')}/image')
    image_dir = os.path.join(image_dir, platform)

    # 确保目录存在，如果不存在则创建（线程安全）
    os.makedirs(image_dir, exist_ok=True)

    file_name = os.path.basename(urlparse(image_url).path)  # 获取 URL 路径中的文件名
    file_path = os.path.join(image_dir, file_name)  # 拼接文件路径

    if os.path.exists(file_path):
        if img_save_path is not None:
            create_file_path(img_save_path)
            copy_file(file_path, img_save_path)
        return file_path

    # http://yituo.obs.cn-south-1.myhuaweicloud.com:80//UPLOAD/100743/2025-05/1747213019M9ujHVHG.jpg?x-image-process=image/resize,m_lfit,h_100,w_100
    # https://ssmp-spmp.oss-cn-shenzhen.aliyuncs.com/4136915/image/spec/wNgR5gFzOYYnu52Jkyez.jpg?x-image-process=image/resize,m_lfit,h_100,w_100
    # 这个域名有浏览器指纹校验 无法通过脚本下载图片
    if any(blocked in image_url for blocked in
           ['myhuaweicloud.com', 'ssmp-spmp.oss-cn-shenzhen.aliyuncs.com', 'image.myqcloud.com', 'kj-img.pddpic.com']):
        return download_img_by_chrome(image_url, file_path)

    # if 'myhuaweicloud.com' in image_url:
    #     return False
    # if 'ssmp-spmp.oss-cn-shenzhen.aliyuncs.com' in image_url:
    #     return False
    # if 'image.myqcloud.com' in image_url:
    #     return False
    # if 'kj-img.pddpic.com' in image_url:
    #     return False

    headers = {
        "User-Agent"     : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept"         : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    # 下载图片
    try:
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()  # 如果响应状态码不是 200，将引发 HTTPError
        # # 成功处理
        log(f"成功获取网络图片: {image_url}")
    except requests.exceptions.HTTPError as e:
        log(f"HTTP 错误: {e} {image_url}")
        return False
    except requests.exceptions.ConnectionError as e:
        log(f"连接错误: {e} {image_url}")
        return False
    except requests.exceptions.Timeout as e:
        log(f"请求超时: {e} {image_url}")
        return False
    except requests.exceptions.RequestException as e:
        log(f"请求异常: {e} {image_url}")
        return False

    # 将图片保存到本地
    with open(file_path, 'wb') as f:
        f.write(response.content)

    if img_save_path is not None:
        create_file_path(img_save_path)
        copy_file(file_path, img_save_path)

    return file_path

# 插入图片函数 注意windows中这个路径反斜杠要是这样的才能插入成功
# C:\Users\Administrator/Desktop/auto/sku_img\K-CPYZB005-1_1734316546.png
def insert_cell_image(sheet, cell, file_path, img_width=120):
    """
    从本地文件居中插入图片到 Excel 指定合并的单元格。
    :param sheet: xlwings 的 Sheet 对象。
    :param cell: 目标单元格地址（如 'A1'）。
    :param file_path: 本地文件路径。
    :param img_width: 插入图片的宽高 图片为正方形 和 row_height 同值
    """
    try:
        # 获取目标单元格区域
        cell_range = sheet.range(cell)

        # 如果是合并区域，获取合并区域
        if cell_range.merge_cells:
            merge_area = cell_range.merge_area
            cell_range = merge_area  # 更新为合并区域

        # 获取合并区域的宽度和高度
        cell_width = cell_range.width  # 单元格宽度
        cell_height = cell_range.height  # 单元格高度

        # 如果单元格的宽度小于图片宽度，增加单元格的宽度
        if cell_width < img_width:
            cell_range.column_width = img_width / 6.1  # 约12.86字符宽度

        # 这一行暂时先自动控制宽度
        cell_range.column_width = img_width / 6.1

        # 如果单元格的高度小于图片高度，增加单元格的高度
        if cell_height < img_width:
            cell_range.row_height = max(150 / 8, img_width / cell_range.rows.count)  # 设置为图片高度

        # 获取合并区域的 top 和 left，计算图片居中的位置
        top = cell_range.top + (cell_range.height - img_width) / 2
        left = cell_range.left + (cell_range.width - img_width) / 2

        # 将图片插入到指定单元格并填充满单元格
        sheet.pictures.add(file_path, top=top + 2, left=left + 2, width=img_width - 4, height=img_width - 4)

    except Exception as e:
        log(f'插入图片失败: {e}, {file_path}')
        send_exception()

# 插入图片函数 注意windows中这个路径反斜杠要是这样的才能插入成功
# C:\Users\Administrator/Desktop/auto/sku_img\K-CPYZB005-1_1734316546.png
def insert_image_from_local(sheet, cell, file_path, cell_width=90, cell_height=90):
    """
    从本地文件插入图片到 Excel 指定单元格。
    :param sheet: xlwings 的 Sheet 对象。
    :param cell: 目标单元格地址（如 'A1'）。
    :param file_path: 本地文件路径。
    """
    try:
        # 打印文件路径以确保正确
        # log(f'插入图片的文件路径: {file_path}')

        # if is_cell_has_image(sheet, cell):
        #     log(f'单元格 {cell} 已有图片，跳过插入。')
        # return

        # 获取单元格位置
        cell_range = sheet.range(cell)
        # cell_width = cell_range.width  # 获取单元格的宽度
        # cell_height = cell_range.height  # 获取单元格的高度
        # log(f'插入图片单元格:{cell} {cell_width} {cell_height}')

        # 设置列宽为 90 磅（近似值）
        cell_range.column_width = cell_width / 6.1  # 约 12.86 字符宽度
        # 设置行高为 90 磅
        cell_range.row_height = cell_height

        # 将图片插入到指定单元格并填充满单元格
        sheet.pictures.add(file_path,
                           top=cell_range.top + 5,
                           left=cell_range.left + 5,
                           width=cell_width - 10, height=cell_height - 10)

        # log(f'图片已成功插入到单元格 {cell}')
    except Exception as e:
        log(f'插入图片失败: {e}, {file_path}')

# 插入图片函数 注意windows中这个路径反斜杠要是这样的才能插入成功
# C:\Users\Administrator/Desktop/auto/sku_img\K-CPYZB005-1_1734316546.png
def insert_skc_image_from_local(sheet, cell, file_path):
    """
    从本地文件插入图片到 Excel 指定单元格。
    :param sheet: xlwings 的 Sheet 对象。
    :param cell: 目标单元格地址（如 'A1'）。
    :param file_path: 本地文件路径。
    """
    try:
        # 打印文件路径以确保正确
        log(f'插入图片的文件路径: {file_path}')

        # if is_cell_has_image(sheet, cell):
        #     log(f'单元格 {cell} 已有图片，跳过插入。')
        # return

        # 获取单元格位置
        cell_range = sheet.range(cell)
        cell_width = cell_range.width  # 获取单元格的宽度
        cell_height = cell_range.height  # 获取单元格的高度

        # 将图片插入到指定单元格并填充满单元格
        sheet.pictures.add(file_path,
                           top=cell_range.top + 2,
                           left=cell_range.left + 2,
                           width=86, height=88)

        log(f'图片已成功插入到单元格 {cell}')
    except Exception as e:
        log(f'插入图片失败: {e}')

# # 设置 A 列和第 1 行为接近 100x100 的正方形
# set_square_cells(sheet, 'A', 1, 100)

def clear_all_pictures(sheet):
    """
    清空 Excel Sheet 中的所有图片。

    :param sheet: xlwings 的 Sheet 对象
    """
    try:
        # 遍历并删除所有图片
        for picture in sheet.pictures:
            picture.delete()
        log("已清空该 Sheet 上的所有图片！")
    except Exception as e:
        send_exception()
        log(f"清空图片失败: {e}")

def get_excel_format(sheet, cell_range):
    rng = sheet.range(cell_range)

    format_settings = {
        "numberFormat": rng.number_format,
        "font"        : {
            "name"  : rng.api.Font.Name,
            "size"  : rng.api.Font.Size,
            "bold"  : rng.api.Font.Bold,
            "italic": rng.api.Font.Italic,
            "color" : rng.api.Font.Color
        },
        "alignment"   : {
            "horizontalAlignment": rng.api.HorizontalAlignment,
            "verticalAlignment"  : rng.api.VerticalAlignment,
            "wrapText"           : rng.api.WrapText
        },
        "borders"     : []
    }

    # 获取所有边框设置（Excel 有 8 种边框）
    for index in range(5, 13):
        border = rng.api.Borders(index)
        format_settings["borders"].append({
            "index"    : index,
            "lineStyle": border.LineStyle,
            "color"    : border.Color,
            "weight"   : border.Weight
        })

    # 获取背景色
    format_settings["background"] = {
        "color": rng.api.Interior.Color
    }

    # 获取锁定和公式隐藏
    format_settings["locked"] = rng.api.Locked
    format_settings["formulaHidden"] = rng.api.FormulaHidden

    return json.dumps(format_settings, indent=2)

def set_excel_format(sheet, cell_range, json_setting):
    settings = json.loads(json_setting)

    # 解析并应用格式
    rng = sheet.range(cell_range)

    # 设置数字格式
    if "numberFormat" in settings:
        rng.number_format = settings["numberFormat"]

    # 设置字体格式
    if "font" in settings:
        font = settings["font"]
        if "name" in font:
            rng.api.Font.Name = font["name"]
        if "size" in font:
            rng.api.Font.Size = font["size"]
        if "bold" in font:
            rng.api.Font.Bold = font["bold"]
        if "italic" in font:
            rng.api.Font.Italic = font["italic"]
        if "color" in font:
            rng.api.Font.Color = font["color"]

    # 设置对齐方式
    if "alignment" in settings:
        alignment = settings["alignment"]
        if "horizontalAlignment" in alignment:
            rng.api.HorizontalAlignment = alignment["horizontalAlignment"]
        if "verticalAlignment" in alignment:
            rng.api.VerticalAlignment = alignment["verticalAlignment"]
        if "wrapText" in alignment:
            rng.api.WrapText = alignment["wrapText"]

    # 设置边框
    if "borders" in settings:
        for border in settings["borders"]:
            index = border["index"]
            line_style = border["lineStyle"]
            color = border["color"]
            weight = border["weight"]

            rng.api.Borders(index).LineStyle = line_style
            rng.api.Borders(index).Color = color
            rng.api.Borders(index).Weight = weight

    # 设置背景
    if "background" in settings:
        bg = settings["background"]
        if "color" in bg:
            rng.api.Interior.Color = bg["color"]

    # 设置锁定和隐藏公式
    if "locked" in settings:
        rng.api.Locked = settings["locked"]
    if "formulaHidden" in settings:
        rng.api.FormulaHidden = settings["formulaHidden"]

# # 获取 A1 单元格格式
# json_format = get_excel_format(sheet, "A1")
# log("Original Format:", json_format)
# # 将格式应用到 B1
# set_excel_format(sheet, json_format, "B1")
# log("Format copied from A1 to B1")

def get_unique_values(sheet, column, start_row, end_row=None):
    """
    获取指定列从指定行开始的不重复值列表，确保读取的值与 Excel 中显示的内容完全一致。

    参数:
    sheet (xlwings.Sheet): Excel 工作表对象。
    column (str): 列字母（例如 'A', 'B' 等）。
    start_row (int): 开始行号。
    end_row (int, optional): 结束行号。如果未提供，则读取到列的最后一行。

    返回:
    list: 不重复的值列表。
    """
    # 获取指定列的区域
    if end_row:
        range_str = f"{column}{start_row}:{column}{end_row}"
    else:
        range_str = f"{column}{start_row}:{column}{sheet.range(f'{column}{start_row}').end('down').row}"

    values = []
    for cell in sheet.range(range_str):
        # 使用 .api 获取底层 Excel 单元格的 Text 属性
        cell_value = cell.api.Text
        values.append(cell_value)
    # 将值转换为字符串并去重
    unique_values = list(set(str(value) if value is not None else "" for value in values))
    return unique_values
    # # 获取 A 列从第 2 行开始的不重复值
    # unique_values = get_unique_values(sheet, 'A', 2)
    # log(unique_values)

def get_unique_values_by_row(sheet, row, start_col, end_col=None):
    """
    获取指定行从指定列开始的不重复值列表，确保读取的值与 Excel 中显示的内容完全一致。

    参数:
    sheet (xlwings.Sheet): Excel 工作表对象。
    row (int): 行号。
    start_col (str): 开始列字母（例如 'A', 'B' 等）。
    end_col (str, optional): 结束列字母。如果未提供，则读取到行的最后一列。

    返回:
    list: 不重复的值列表。
    """
    # 获取指定行的区域
    if end_col:
        range_str = f"{start_col}{row}:{end_col}{row}"
    else:
        range_str = f"{start_col}{row}:{sheet.range(f'{start_col}{row}').end('right').column_letter}{row}"

    values = []
    for cell in sheet.range(range_str):
        # 使用 .api 获取底层 Excel 单元格的 Text 属性
        cell_value = cell.api.Text
        values.append(cell_value)

    # 将值转换为字符串并去重
    unique_values = list(set(str(value) if value is not None else "" for value in values))
    return unique_values
    # 获取第 2 行从 A 列开始的不重复值
    # unique_values = get_unique_values_by_row(sheet, 2, 'A')

def find_rows_by_criteria(sheet, col, search_text, match_type='equals'):
    """
    在指定列中查找符合条件的数据所在行。

    参数:
    sheet (xlwings.Sheet): Excel 工作表对象。
    col (str or int): 查找列号，支持列字母（如 'A'）或列号（如 1），也支持负数（如 -1 表示倒数第一列）。
    search_text (str): 待查找的文本内容。
    match_type (str): 匹配方式，可选 'equals'（完全匹配）或 'contains'（包含匹配）。默认为 'equals'。

    返回:
    list: 包含所有符合查找标准的行号的列表。如果未找到匹配项，则返回空列表 []。
    """
    # 将列号转换为列字母
    if isinstance(col, int):
        if col < 0:
            # 处理负数列号（倒数第几列）
            col = sheet.range((1, 1)).end('right').column + col + 1
        col_letter = xw.utils.col_name(col)
    else:
        col_letter = col.upper()

    # 获取指定列的区域
    start_cell = sheet.range(f"{col_letter}1")
    end_cell = start_cell.end('down')
    range_str = f"{col_letter}1:{col_letter}{end_cell.row}"

    # 查找符合条件的行号
    matched_rows = []
    for cell in sheet.range(range_str):
        cell_value = cell.api.Text  # 获取单元格的显示值
        # log('内部',cell_value,search_text,cell_value == search_text)
        if match_type == 'equals' and cell_value == search_text:
            matched_rows.append(cell.row)
        elif match_type == 'contains' and search_text in cell_value:
            matched_rows.append(cell.row)

    return matched_rows

    # # 示例 1：在 A 列中查找完全匹配 "123" 的行号
    # result_equals = find_rows_by_criteria(sheet, 'A', '123', match_type='equals')
    # log("完全匹配结果:", result_equals)

    # # 示例 2：在 B 列中查找包含 "abc" 的行号
    # result_contains = find_rows_by_criteria(sheet, 2, 'abc', match_type='contains')
    # log("包含匹配结果:", result_contains)

    # # 示例 3：在倒数第一列中查找完全匹配 "xyz" 的行号
    # result_negative_col = find_rows_by_criteria(sheet, -1, 'xyz', match_type='equals')
    # log("倒数第一列匹配结果:", result_negative_col)

def find_columns_by_criteria(sheet, row, search_text, match_type='equals'):
    """
    在指定行中查找符合条件的数据所在列。

    参数:
    sheet (xlwings.Sheet): Excel 工作表对象。
    row (int): 查找行号，支持正数（如 1）或负数（如 -1 表示倒数第一行）。
    search_text (str): 待查找的文本内容。
    match_type (str): 匹配方式，可选 'equals'（完全匹配）或 'contains'（包含匹配）。默认为 'equals'。

    返回:
    list: 包含所有符合查找标准的列字母的列表。如果未找到匹配项，则返回空列表 []。
    """
    # 处理负行号
    if row < 0:
        last_row = sheet.range('A1').end('down').row
        row = last_row + row + 1

    # 获取指定行的区域
    start_cell = sheet.range(f"A{row}")
    end_cell = start_cell.end('right')
    range_str = f"A{row}:{end_cell.column_letter}{row}"

    # 查找符合条件的列字母
    matched_columns = []
    for cell in sheet.range(range_str):
        cell_value = cell.api.Text  # 获取单元格的显示值
        if match_type == 'equals' and cell_value == search_text:
            matched_columns.append(cell.column_letter)
        elif match_type == 'contains' and search_text in cell_value:
            matched_columns.append(cell.column_letter)

    return matched_columns
    # # 示例 1：在第 1 行中查找完全匹配 "123" 的列字母
    # result_equals = find_columns_by_criteria(sheet, 1, '123', match_type='equals')
    # log("完全匹配结果:", result_equals)

    # # 示例 2：在第 2 行中查找包含 "abc" 的列字母
    # result_contains = find_columns_by_criteria(sheet, 2, 'abc', match_type='contains')
    # log("包含匹配结果:", result_contains)

    # # 示例 3：在倒数第一行中查找完全匹配 "xyz" 的列字母
    # result_negative_row = find_columns_by_criteria(sheet, -1, 'xyz', match_type='equals')
    # log("倒数第一行匹配结果:", result_negative_row)

def check_data(data):
    for row in data:
        log(len(row), row)

def write_data(excel_path, sheet_name, data, format_to_text_colunm=None):
    app, wb, sheet = open_excel(excel_path, sheet_name)
    # 清空工作表中的所有数据
    sheet.clear()
    # 某些列以文本格式写入
    format_to_text_v2(sheet, format_to_text_colunm)
    # 写入数据
    # check_data(data)
    sheet.range('A1').value = data
    # 保存
    wb.save()
    close_excel(app, wb)

def colorize_by_field(sheet, field):
    minimize(sheet.book.app)
    # 读取数据
    field_column = find_column_by_data(sheet, 1, field)  # 假设 SPU 在 C 列
    if field_column is None:
        return
    data_range = sheet.range(f"{field_column}1").expand("down")  # 获取 SPU 列的所有数据
    spu_values = data_range.value[:]
    max_column_letter = get_max_column_letter(sheet)
    # 记录 SPU 对应的颜色
    spu_color_map = {}
    for i, spu in enumerate(spu_values):  # 从 Excel 第 2 行开始（第 1 行是标题）
        row = i + 1
        if row < 2:
            continue
        if spu not in spu_color_map:
            spu_color_map[spu] = random_color()  # 生成新的颜色
        bg_color = spu_color_map[spu]
        row_range = sheet.range(f"A{row}:{max_column_letter}{row}")
        row_range.color = bg_color  # 应用背景色
        sheet.range(f"A{row}").api.Font.Bold = True  # 让店铺名称加粗

def add_borders(sheet, lineStyle=1):
    log('添加边框')
    # 获取工作表的整个范围（假设表格的数据是从A1开始）
    last_col = sheet.range('A1').end('right').column  # 获取最后一列
    last_row = get_last_row(sheet, 'A')
    range_to_border = sheet.range((1, 1), (last_row, last_col))  # 定义范围

    # 设置外部边框（所有边都为实线）
    range_to_border.api.Borders(7).LineStyle = lineStyle  # 上边框
    range_to_border.api.Borders(8).LineStyle = lineStyle  # 下边框
    range_to_border.api.Borders(9).LineStyle = lineStyle  # 左边框
    range_to_border.api.Borders(10).LineStyle = lineStyle  # 右边框

    # 设置内部边框
    range_to_border.api.Borders(1).LineStyle = lineStyle  # 内部上边框
    range_to_border.api.Borders(2).LineStyle = lineStyle  # 内部下边框
    range_to_border.api.Borders(3).LineStyle = lineStyle  # 内部左边框
    range_to_border.api.Borders(4).LineStyle = lineStyle  # 内部右边框

def add_range_border(sheet, coor_A=(1, 1), coor_B=(1, 1), lineStyle=1):
    range_to_border = sheet.range(coor_A, coor_B)  # 定义范围

    # 设置外部边框（所有边都为实线）
    range_to_border.api.Borders(7).LineStyle = lineStyle  # 上边框
    range_to_border.api.Borders(8).LineStyle = lineStyle  # 下边框
    range_to_border.api.Borders(9).LineStyle = lineStyle  # 左边框
    range_to_border.api.Borders(10).LineStyle = lineStyle  # 右边框

    # 设置内部边框
    range_to_border.api.Borders(1).LineStyle = lineStyle  # 内部上边框
    range_to_border.api.Borders(2).LineStyle = lineStyle  # 内部下边框
    range_to_border.api.Borders(3).LineStyle = lineStyle  # 内部左边框
    range_to_border.api.Borders(4).LineStyle = lineStyle  # 内部右边框

def open_excel(excel_path, sheet_name='Sheet1'):
    try:
        # 创建新实例
        app = xw.App(visible=True, add_book=False)
        app.display_alerts = False  # 复用时仍然关闭警告
        app.screen_updating = True

        # 打开或新建工作簿
        wb = None
        if os.path.exists(excel_path):
            for book in app.books:
                if book.fullname.lower() == os.path.abspath(excel_path).lower():
                    wb = book
                    break
            else:
                wb = app.books.open(excel_path, read_only=False)
        else:
            wb = app.books.add()
            os.makedirs(os.path.dirname(excel_path), exist_ok=True)
            wb.save(excel_path)

        # 处理 sheet 选择逻辑（支持名称或索引）
        if isinstance(sheet_name, int):  # 如果是整数，按索引获取
            if 0 <= sheet_name < len(wb.sheets):  # 确保索引有效
                sheet = wb.sheets[sheet_name]
            else:
                log(f"索引 {sheet_name} 超出范围，创建新工作表。")
                sheet = wb.sheets.add(after=wb.sheets[-1])
        elif isinstance(sheet_name, str):  # 如果是字符串，按名称获取
            sheet_name_clean = sheet_name.strip().lower()
            sheet_names = [s.name.strip().lower() for s in wb.sheets]
            if sheet_name_clean in sheet_names:
                sheet = wb.sheets[sheet_name]
            else:
                try:
                    sheet = wb.sheets.add(sheet_name, after=wb.sheets[-1])
                except Exception as e:
                    send_exception()
                    return None, None, None
        else:
            send_exception(f"sheet_name 必须是字符串（名称）或整数（索引）:{sheet_name}")
            raise

        sheet.activate()
        file_name = os.path.basename(excel_path)
        log(f"open_excel {file_name} {sheet.name}")
        # 不能在这个地方最小化 容易导致错误
        # 让 Excel 窗口最小化
        # app.api.WindowState = -4140  # -4140 对应 Excel 中的 xlMinimized 常量
        return app, wb, sheet

    except Exception as e:
        send_exception()
        # wxwork.notify_error_msg(f'打开 Excel 失败: {traceback.format_exc()}')
        return None, None, None

def close_excel(app, wb):
    if wb is not None:
        wb.save()
        wb.close()
    if app is not None:
        app.quit()

# 获取某列最后非空行
def get_last_row(sheet, column):
    last_row = sheet.range(column + str(sheet.cells.last_cell.row)).end('up').row
    # 检查当前单元格是否在合并区域中
    cell = sheet.range(f'{column}{last_row}')
    # 如果当前单元格是合并单元格的一部分，获取合并区域的首行
    if cell.merge_cells:
        last_row = cell.merge_area.last_cell.row
    return last_row

# 获取最后一列字母
def get_last_col(sheet):
    # # 获取最后一行的索引
    last_col = index_to_column_name(sheet.range('A1').end('right').column)  # 里面是索引 返回最后一列 如 C
    return last_col

# 获取最大列名字母
def get_max_column_letter(sheet):
    """获取当前 sheet 中最大有数据的列的列名（如 'A', 'B', ..., 'Z', 'AA', 'AB'）"""
    last_col = sheet.used_range.last_cell.column  # 获取最大列索引
    return xw.utils.col_name(last_col)  # 将索引转换为列名

# 随机生成颜色
def random_color():
    return (random.randint(180, 255), random.randint(180, 255), random.randint(180, 255))  # 亮色背景

def get_contrast_text_color(rgb):
    """根据背景色亮度返回适合的字体颜色（黑色或白色）"""
    r, g, b = rgb
    brightness = r * 0.299 + g * 0.587 + b * 0.114  # 亮度计算公式
    return (0, 0, 0) if brightness > 186 else (255, 255, 255)  # 186 是经验值

def rgb_to_long(r, g, b):
    """将 RGB 颜色转换为 Excel Long 类型"""
    return r + (g * 256) + (b * 256 * 256)

def read_excel_to_json(file_path, sheet_name="Sheet1"):
    app, wb, sheet = open_excel(file_path, sheet_name)

    used_range = sheet.used_range
    data = {}
    merged_cells = []
    column_widths = {}  # 存储列宽度
    row_heights = {}  # 存储行高度

    # 记录列宽度
    for col in range(1, used_range.columns.count + 1):
        width = sheet.range((1, col)).column_width
        column_widths[col] = min(max(width, 1), 255)  # ✅ 限制范围，防止错误

    # 记录行高度
    for row in range(1, used_range.rows.count + 1):
        row_heights[row] = sheet.range((row, 1)).row_height  # ✅ 修正行高获取方式

    # 遍历所有单元格
    for row in range(1, used_range.rows.count + 1):
        for col in range(1, used_range.columns.count + 1):
            cell = sheet.cells(row, col)

            # 处理对角线
            diagonal_up = cell.api.Borders(5)  # 左上到右下
            diagonal_down = cell.api.Borders(6)  # 右上到左下

            diagonal_up_info = None
            diagonal_down_info = None

            if diagonal_up.LineStyle == 1:
                diagonal_up_info = {"style": diagonal_up.LineStyle, "color": diagonal_up.Color}

            if diagonal_down.LineStyle == 1:
                diagonal_down_info = {"style": diagonal_down.LineStyle, "color": diagonal_down.Color}

            cell_info = {
                "value"           : cell.value,
                "color"           : cell.color,
                "font_name"       : cell.api.Font.Name,
                "font_size"       : cell.api.Font.Size,
                "bold"            : cell.api.Font.Bold,
                "italic"          : cell.api.Font.Italic,
                "font_color"      : cell.api.Font.Color,
                "horizontal_align": cell.api.HorizontalAlignment,
                "vertical_align"  : cell.api.VerticalAlignment,
                "number_format"   : cell.api.NumberFormat,
                "border"          : {
                    "left"  : {"style": cell.api.Borders(1).LineStyle, "color": cell.api.Borders(1).Color},
                    "right" : {"style": cell.api.Borders(2).LineStyle, "color": cell.api.Borders(2).Color},
                    "top"   : {"style": cell.api.Borders(3).LineStyle, "color": cell.api.Borders(3).Color},
                    "bottom": {"style": cell.api.Borders(4).LineStyle, "color": cell.api.Borders(4).Color},
                }
            }

            if diagonal_up_info:
                cell_info["border"]["diagonal_up"] = diagonal_up_info
            if diagonal_down_info:
                cell_info["border"]["diagonal_down"] = diagonal_down_info

            data[f"{row},{col}"] = cell_info

    # 处理合并单元格
    for merged_range in sheet.api.UsedRange.Cells:
        if merged_range.MergeCells:
            merged_cells.append({
                "merge_range": merged_range.MergeArea.Address.replace("$", "")
            })

    wb.close()
    app.quit()

    final_data = {
        "cells"        : data,
        "merged_cells" : merged_cells,
        "column_widths": column_widths,
        "row_heights"  : row_heights
    }

    with open("excel_data.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=4, ensure_ascii=False)

    print("✅ Excel 数据已存储为 JSON")

def write_json_to_excel(json_file, new_excel="new_test.xlsx", sheet_name="Sheet1"):
    with open(json_file, "r", encoding="utf-8") as f:
        final_data = json.load(f)

    data = final_data["cells"]
    merged_cells = final_data["merged_cells"]
    column_widths = final_data["column_widths"]
    row_heights = final_data["row_heights"]

    app, wb, sheet = open_excel(new_excel, sheet_name)

    for col, width in column_widths.items():
        col_name = xw.utils.col_name(int(col))
        sheet.range(f'{col_name}:{col_name}').column_width = int(width)

    # 恢复行高度
    for row, height in row_heights.items():
        sheet.range((row, 1)).row_height = height  # ✅ 修正行高恢复方式

    for key, cell_info in data.items():
        row, col = map(int, key.split(","))

        cell = sheet.cells(row, col)
        cell.value = cell_info["value"]
        cell.color = cell_info["color"]
        cell.api.Font.Name = cell_info["font_name"]
        cell.api.Font.Size = cell_info["font_size"]
        cell.api.Font.Bold = cell_info["bold"]
        cell.api.Font.Italic = cell_info["italic"]
        cell.api.Font.Color = cell_info["font_color"]
        cell.api.HorizontalAlignment = cell_info["horizontal_align"]
        cell.api.VerticalAlignment = cell_info["vertical_align"]
        cell.api.NumberFormat = cell_info["number_format"]

        # 恢复边框
        for side, border_info in cell_info["border"].items():
            border_index = {"left": 1, "right": 2, "top": 3, "bottom": 4}.get(side)
            if border_index and border_info["style"] not in [None, 0]:
                cell.api.Borders(border_index).LineStyle = border_info["style"]
                cell.api.Borders(border_index).Color = border_info["color"]

        # 恢复对角线
        if "diagonal_up" in cell_info["border"]:
            cell.api.Borders(5).LineStyle = cell_info["border"]["diagonal_up"]["style"]
            cell.api.Borders(5).Color = cell_info["border"]["diagonal_up"]["color"]

        if "diagonal_down" in cell_info["border"]:
            cell.api.Borders(6).LineStyle = cell_info["border"]["diagonal_down"]["style"]
            cell.api.Borders(6).Color = cell_info["border"]["diagonal_down"]["color"]

    wb.save(new_excel)
    # 恢复合并单元格
    for merge in merged_cells:
        merge_range = merge["merge_range"]
        sheet.range(merge_range).merge()

    wb.save(new_excel)
    close_excel(app, wb)

    print(f"✅ 数据已成功写入 {new_excel}")
    time.sleep(2)  # 这里需要一个延时

def safe_expand_down(sheet, start_cell='A2'):
    rng = sheet.range(start_cell)
    if not rng.value:
        return []
    try:
        return rng.expand('down')
    except Exception as e:
        log(f'safe_expand_down failed: {e}')
        return [rng]  # 返回单元格本身

# 初始化一个表格
# data 需要是一个二维列表
def init_progress_ex(key_id, excel_path, sheet_name='Sheet1'):
    app, wb, sheet = open_excel(excel_path, sheet_name)

    # 设置标题与格式
    expected_header = ["任务ID", "处理状态(未完成|已完成)"]
    # 只在首次或不一致时写入标题
    current_header = [sheet.range('A1').value, sheet.range('B1').value]
    if current_header != expected_header:
        sheet.range('A1').value = expected_header
        sheet.range('A:A').number_format = '@'
        log('初始化表头和格式')
    else:
        log('已存在正确表头，跳过初始化')

    # 获取已存在的 keyID（从 A2 开始向下扩展）
    used_range = safe_expand_down(sheet, 'A2')
    existing_ids = [str(c.value) for c in used_range if c.value]

    if str(key_id) in existing_ids:
        log(f'已存在相同任务跳过: {key_id}')
    else:
        # 找到第一列最后一个非空行
        last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row
        new_row = last_row + 1
        sheet.range(f'A{new_row}').value = [key_id, '']
        log(f'写入任务: {key_id}')

    # 设置标题栏样式
    format_header_row(sheet, len(expected_header))

    wb.save()

def init_data_ex(key_id, excel_path, header, sheet_name='Sheet1'):
    app, wb, sheet = open_excel(excel_path, sheet_name)

    # 判断是否需要写入标题和设置格式
    current_header = [sheet.range(f'{index_to_column_name(i + 1)}1').value for i in range(len(header))]
    if current_header != header:
        sheet.range('A1').value = header
        sheet.range('A:A').number_format = '@'
        log('初始化表头和格式')
    else:
        log('表头已存在，跳过初始化')

    # 检查是否已存在相同 key_id
    existing_ids = [str(cell.value) for cell in sheet.range('A2').expand('down') if cell.value]
    if str(key_id) in existing_ids:
        log(f'已初始化主键: {key_id}')
    else:
        last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row
        new_row = last_row + 1
        sheet.range(f'A{new_row}').value = [key_id, '']
        log(f'写入任务: {[key_id, ""]}')

    # 格式化标题栏（如果是第一次设置标题）
    if current_header != header:
        format_header_row(sheet, len(header))

    wb.save()

def format_header_row(sheet, column_count):
    """
    设置标题行样式和列对齐
    """
    for col_index in range(1, column_count + 1):
        col_letter = index_to_column_name(col_index)
        cell = sheet.range(f'{col_letter}1')

        # 设置标题样式
        cell.color = (68, 114, 196)
        cell.font.size = 12
        cell.font.bold = True
        cell.font.color = (255, 255, 255)

        # 设置列居中对齐
        sheet.range(f'{col_letter}:{col_letter}').api.HorizontalAlignment = -4108  # xlCenter
        sheet.range(f'{col_letter}:{col_letter}').api.VerticalAlignment = -4108  # xlCenter

        # 自动调整列宽
        sheet.range(f'{col_letter}:{col_letter}').autofit()

# 初始化一个表格
# data 需要是一个二维列表
def init_progress(excel_path, keyID, sheet_name='Sheet1'):
    app, wb, sheet = open_excel(excel_path, sheet_name)
    # 覆盖写入标题
    sheet.range('A1').value = ["任务ID", "处理状态(未完成|已完成)"]
    # 覆盖写入数据
    sheet.range(f'A:A').number_format = '@'  # 一般先设置格式再写入数据才起到效果 否则需要后触发格式

    data = [[keyID, '']]
    for index, item in enumerate(data):
        keyID = item[0]
        status = item[1]
        flagRecord = True
        # 遍历可用行
        used_range_row = sheet.range('A1').expand('down')
        for i, cell in enumerate(used_range_row):
            row = i + 1
            if row < 2:
                continue
            rowKeyID = sheet.range(f'A{row}').value
            if str(rowKeyID) == str(keyID):
                log(f'已存在相同任务跳过: {keyID}')
                flagRecord = False
                break
        if flagRecord:
            # 获取第一列最后一个非空单元格的行号
            last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row
            sheet.range(f'A{last_row + 1}').value = item
            log(f'写入任务: {item}')

    # 处理标题栏格式
    # 遍历可用列 这个要先遍历 因为要列宽自适应 会破坏前面设置好的宽度属性
    used_range_col = sheet.range('A1').expand('right')
    for j, cell in enumerate(used_range_col):
        col = j + 1
        col_name = index_to_column_name(col)
        col_val = sheet.range(f'{col_name}1').value
        # 设置标题栏字体颜色与背景色
        sheet.range(f'{col_name}1').color = (68, 114, 196)
        sheet.range(f'{col_name}1').font.size = 12
        sheet.range(f'{col_name}1').font.bold = True
        sheet.range(f'{col_name}1').font.color = (255, 255, 255)
        # 所有列水平居中和垂直居中
        sheet.range(f'{col_name}:{col_name}').api.HorizontalAlignment = -4108
        sheet.range(f'{col_name}:{col_name}').api.VerticalAlignment = -4108

        sheet.range(f'{col_name}:{col_name}').autofit()

    wb.save()

def get_progress(excel_path, keyID, sheet_name="Sheet1"):
    app, wb, sheet = open_excel(excel_path, sheet_name)
    # 遍历可用行
    used_range_row = sheet.range('A1').expand('down')
    for i, cell in enumerate(used_range_row):
        row = i + 1
        if row < 2:
            continue
        rowKeyID = sheet.range(f'A{row}').value;
        if rowKeyID == keyID:
            result = sheet.range(f'B{row}').value;
            if result == "已完成":
                return True
            else:
                return False

def get_progress_ex(keyID, excel_path, sheet_name="Sheet1"):
    app, wb, sheet = open_excel(excel_path, sheet_name)
    # 遍历可用行
    used_range_row = sheet.range('A1').expand('down')
    for i, cell in enumerate(used_range_row):
        row = i + 1
        if row < 2:
            continue
        rowKeyID = sheet.range(f'A{row}').value;
        if rowKeyID == keyID:
            result = sheet.range(f'B{row}').value;
            if result == "已完成":
                return True
            else:
                return False
    close_excel(app, wb)

def get_progress_data(excel_path, keyID, sheet_name="Sheet1"):
    app, wb, sheet = open_excel(excel_path, sheet_name)
    # 遍历可用行
    used_range_row = sheet.range('A1').expand('down')
    for i, cell in enumerate(used_range_row):
        row = i + 1
        if row < 2:
            continue
        rowKeyID = sheet.range(f'A{row}').value
        if rowKeyID == keyID:
            result = sheet.range(f'C{row}').value
            return result
    return None

def get_progress_data_ex(keyID, excel_path, sheet_name="Sheet1"):
    app, wb, sheet = open_excel(excel_path, sheet_name)
    # 遍历可用行
    used_range_row = sheet.range('A1').expand('down')
    for i, cell in enumerate(used_range_row):
        row = i + 1
        if row < 2:
            continue
        rowKeyID = sheet.range(f'A{row}').value
        if rowKeyID == keyID:
            result = sheet.range(f'C{row}').value
            return result
    return None

def set_progress(excel_path, keyID, status='已完成', sheet_name="Sheet1"):
    app, wb, sheet = open_excel(excel_path, sheet_name)
    # 遍历可用行
    used_range_row = sheet.range('A1').expand('down')
    for i, cell in enumerate(used_range_row):
        row = i + 1
        if row < 2:
            continue
        rowKeyID = sheet.range(f'A{row}').value
        if str(rowKeyID) == str(keyID):
            sheet.range(f'B{row}').value = status
            wb.save()
            return

def set_progress_ex(keyID, excel_path, status='已完成', sheet_name="Sheet1"):
    app, wb, sheet = open_excel(excel_path, sheet_name)
    # 遍历可用行
    used_range_row = sheet.range('A1').expand('down')
    for i, cell in enumerate(used_range_row):
        row = i + 1
        if row < 2:
            continue
        rowKeyID = sheet.range(f'A{row}').value
        if str(rowKeyID) == str(keyID):
            sheet.range(f'B{row}').value = status
            wb.save()
            close_excel(app, wb)
            return
    close_excel(app, wb)

def set_data_ex(keyID, data, excel_path, sheet_name="Sheet1"):
    app, wb, sheet = open_excel(excel_path, sheet_name)
    # 遍历可用行
    used_range_row = sheet.range('A1').expand('down')
    for i, cell in enumerate(used_range_row):
        row = i + 1
        if row < 2:
            continue
        rowKeyID = sheet.range(f'A{row}').value
        if str(rowKeyID) == str(keyID):
            sheet.range(f'A{row}').value = data
            wb.save()
            return

def set_progress_data(excel_path, keyID, data, sheet_name="Sheet1"):
    app, wb, sheet = open_excel(excel_path, sheet_name)
    # 遍历可用行
    used_range_row = sheet.range('A1').expand('down')
    for i, cell in enumerate(used_range_row):
        row = i + 1
        if row < 2:
            continue
        rowKeyID = sheet.range(f'A{row}').value
        if str(rowKeyID) == str(keyID):
            log('设置数据', data)
            sheet.range(f'C{row}').value = data
            wb.save()
            return

def set_progress_data_ex(keyID, data, excel_path, sheet_name="Sheet1"):
    app, wb, sheet = open_excel(excel_path, sheet_name)
    # 遍历可用行
    used_range_row = sheet.range('A1').expand('down')
    for i, cell in enumerate(used_range_row):
        row = i + 1
        if row < 2:
            continue
        rowKeyID = sheet.range(f'A{row}').value
        if str(rowKeyID) == str(keyID):
            log('设置数据', data)
            sheet.range(f'C{row}').value = data
            wb.save()
            return

def check_progress(excel_path, listKeyID, sheet_name="Sheet1"):
    app, wb, sheet = open_excel(excel_path, sheet_name)
    # 读取整个任务表数据
    data = sheet.used_range.value
    data = [row for row in data if any(row)]  # 过滤掉空行
    # 任务ID和状态列索引
    task_id_col = 0
    status_col = 1
    # 创建任务ID与状态的字典
    task_status_dict = {row[task_id_col]: row[status_col] for row in data[1:] if row[task_id_col]}
    # 找出未完成的任务
    incomplete_tasks = [task_id for task_id in listKeyID if task_status_dict.get(task_id) != "已完成"]
    return len(incomplete_tasks) == 0, incomplete_tasks

def check_progress_ex(listKeyID, excel_path, sheet_name="Sheet1"):
    app, wb, sheet = open_excel(excel_path, sheet_name)
    # 读取整个任务表数据
    data = sheet.used_range.value
    data = [row for row in data if any(row)]  # 过滤掉空行
    # 任务ID和状态列索引
    task_id_col = 0
    status_col = 1
    # 创建任务ID与状态的字典
    task_status_dict = {row[task_id_col]: row[status_col] for row in data[1:] if row[task_id_col]}
    # 找出未完成的任务
    incomplete_tasks = [task_id for task_id in listKeyID if task_status_dict.get(task_id) != "已完成"]
    return len(incomplete_tasks) == 0, incomplete_tasks

def read_excel_sheet_to_list(file_path, sheet_name=None):
    """
    使用 xlwings 读取 Excel 文件中指定工作表的数据，并返回为二维列表。

    :param file_path: Excel 文件路径
    :param sheet_name: 要读取的 sheet 名称（默认读取第一个 sheet）
    :return: 二维列表形式的数据
    """
    app, wb, sheet = open_excel(file_path, sheet_name)
    used_range = sheet.used_range
    data = used_range.value  # 返回为二维列表或一维列表（取决于数据）
    close_excel(app, wb)
    time.sleep(2)
    # 保证返回的是二维列表
    if not data:
        return []
    elif isinstance(data[0], list):
        return data
    else:
        return [data]

def excel_to_dict(excel_path, column_key, column_value, sheet_name=None):
    """
    从 Excel 文件中读取指定两列，生成字典返回（不受中间空行影响）

    :param excel_path: Excel 文件路径
    :param column_key: 键所在列，比如 'A' 或 1（从1开始）
    :param column_value: 值所在列，比如 'B' 或 2
    :param sheet_name: 可选，指定sheet名称，默认第一个sheet
    :return: dict
    """
    app = xw.App(visible=False)
    wb = None
    try:
        wb = app.books.open(excel_path)
        sheet = wb.sheets[sheet_name] if sheet_name else wb.sheets[0]

        # 如果列是数字，转为列字母
        if isinstance(column_key, int):
            column_key = xw.utils.col_name(column_key)
        if isinstance(column_value, int):
            column_value = xw.utils.col_name(column_value)

        # 获取 used range 的总行数
        used_rows = sheet.used_range.last_cell.row

        # 获取整列值（从第2行开始，跳过标题）
        keys = sheet.range(f'{column_key}2:{column_key}{used_rows}').value
        values = sheet.range(f'{column_value}2:{column_value}{used_rows}').value

        # 容错：如果只有一个值会变成单个元素，需变成列表
        if not isinstance(keys, list):
            keys = [keys]
        if not isinstance(values, list):
            values = [values]

        # 构建字典，忽略空键
        result = {
            str(k).strip().lower(): (str(v).strip() if v is not None else '-')
            for k, v in zip(keys, values)
            if k is not None and str(k).strip() != ""
        }
        return result
    finally:
        if wb is not None:
            wb.close()
        app.quit()

def format_to_text_v2(sheet, columns=None):
    if columns is None or len(columns) == 0:
        return
    for col_name in columns:
        if isinstance(col_name, int):
            col_name = xw.utils.col_name(col_name)
            log(f'设置[{col_name}] 文本格式')
        sheet.range(f'{col_name}:{col_name}').number_format = '@'

def format_to_text_v2_safe(sheet, columns=None, data_rows=None):
    """
    更安全的文本格式化函数，避免COM异常
    
    Args:
        sheet: Excel工作表对象
        columns: 要格式化的列名列表
        data_rows: 数据行数，用于限制格式化范围
    """
    if columns is None or len(columns) == 0:
        return

    # 确保columns是列表
    if not isinstance(columns, list):
        columns = [columns]

    for col_name in columns:
        try:
            if isinstance(col_name, int):
                col_name = xw.utils.col_name(col_name)

            log(f'安全设置[{col_name}] 文本格式')

            # 如果指定了数据行数，只格式化有数据的范围
            if data_rows and data_rows > 0:
                # 格式化从第1行到数据行数的范围
                range_str = f'{col_name}1:{col_name}{data_rows}'
                sheet.range(range_str).number_format = '@'
            else:
                # 检查列是否有数据，如果没有则跳过
                try:
                    # 先检查第一个单元格是否存在
                    test_range = sheet.range(f'{col_name}1')
                    if test_range.value is not None or sheet.used_range.last_cell.column >= column_name_to_index(col_name) + 1:
                        sheet.range(f'{col_name}:{col_name}').number_format = '@'
                    else:
                        log(f'列 {col_name} 没有数据，跳过格式化')
                except:
                    log(f'列 {col_name} 格式化失败，跳过')

        except Exception as e:
            log(f'设置列 {col_name} 文本格式失败: {e}，继续处理其他列')

def pre_format_columns_safe(sheet, columns, data_rows):
    """
    预格式化函数：在写入数据前安全地设置列格式
    
    Args:
        sheet: Excel工作表对象
        columns: 要格式化的列名列表
        data_rows: 预期数据行数
    """
    if not columns or not isinstance(columns, list):
        return

    for col_name in columns:
        try:
            if isinstance(col_name, int):
                col_name = xw.utils.col_name(col_name)

            log(f'预格式化列 [{col_name}] 为文本格式')

            # 方法1：先创建最小范围，避免整列操作
            try:
                # 创建足够大的范围来覆盖预期数据
                range_str = f'{col_name}1:{col_name}{max(data_rows, 1000)}'
                sheet.range(range_str).number_format = '@'
                log(f'预格式化成功: {range_str}')
            except Exception as e1:
                log(f'预格式化方法1失败: {e1}')

                # 方法2：逐行设置格式，更安全但稍慢
                try:
                    for row in range(1, data_rows + 1):
                        cell = sheet.range(f'{col_name}{row}')
                        cell.number_format = '@'
                    log(f'逐行预格式化成功: {col_name}')
                except Exception as e2:
                    log(f'逐行预格式化也失败: {e2}')

        except Exception as e:
            log(f'预格式化列 {col_name} 失败: {e}，继续处理其他列')

def post_format_columns_safe(sheet, columns, data_rows):
    """
    后格式化函数：在写入数据后确认列格式
    
    Args:
        sheet: Excel工作表对象
        columns: 要格式化的列名列表
        data_rows: 实际数据行数
    """
    if not columns or not isinstance(columns, list):
        return

    for col_name in columns:
        try:
            if isinstance(col_name, int):
                col_name = xw.utils.col_name(col_name)

            log(f'后格式化列 [{col_name}] 为文本格式')

            # 只对实际有数据的行进行格式化
            if data_rows > 0:
                range_str = f'{col_name}1:{col_name}{data_rows}'
                sheet.range(range_str).number_format = '@'
                log(f'后格式化成功: {range_str}')

        except Exception as e:
            log(f'后格式化列 {col_name} 失败: {e}，继续处理其他列')

def format_to_text(sheet, columns=None):
    if columns is None:
        return
    used_range_col = sheet.range('A1').expand('right')
    for j, cell in enumerate(used_range_col):
        col = j + 1
        col_name = index_to_column_name(col)
        col_val = sheet.range(f'{col_name}1').value
        for c in columns:
            if str(c).lower() in str(col_val).lower():
                log(f'设置[{c}] 文本格式')
                sheet.range(f'{col_name}:{col_name}').number_format = '@'

def format_to_date(sheet, columns=None):
    if columns is None:
        return
    used_range_col = sheet.range('A1').expand('right')
    for j, cell in enumerate(used_range_col):
        col = j + 1
        col_name = index_to_column_name(col)
        col_val = sheet.range(f'{col_name}1').value
        if col_val is None:
            continue
        for c in columns:
            if c in col_val:
                log(f'设置[{c}] 时间格式')
                sheet.range(f'{col_name}:{col_name}').number_format = 'yyyy-mm-dd'

def format_to_datetime(sheet, columns=None):
    if columns is None:
        return
    used_range_col = sheet.range('A1').expand('right')
    for j, cell in enumerate(used_range_col):
        col = j + 1
        col_name = index_to_column_name(col)
        col_val = sheet.range(f'{col_name}1').value
        if col_val is None:
            continue
        for c in columns:
            if c in col_val:
                log(f'设置[{c}] 时间格式')
                sheet.range(f'{col_name}:{col_name}').number_format = 'yyyy-mm-dd hh:mm:ss'

def format_to_month(sheet, columns=None):
    if columns is None:
        return
    used_range_col = sheet.range('A1').expand('right')
    for j, cell in enumerate(used_range_col):
        col = j + 1
        col_name = index_to_column_name(col)
        col_val = sheet.range(f'{col_name}1').value
        for c in columns:
            if c in col_val:
                log(f'设置[{c}] 年月格式')
                sheet.range(f'{col_name}:{col_name}').number_format = 'yyyy-mm'

def add_sum_for_cell(sheet, col_list, row=2):
    last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row
    if last_row > row:
        for col_name in col_list:
            col_letter = find_column_by_data(sheet, 1, col_name)
            sheet.range(f'{col_letter}{row}').formula = f'=SUM({col_letter}{row + 1}:{col_letter}{last_row})'
            sheet.range(f'{col_letter}{row}').api.Font.Color = 255
            sheet.range(f'{col_letter}:{col_letter}').autofit()

def clear_for_cell(sheet, col_list, row=2):
    last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row
    for col_name in col_list:
        col_letter = find_column_by_data(sheet, 1, col_name)
        sheet.range(f'{col_letter}{row}').value = ''

def color_for_column(sheet, col_list, color_name, start_row=2):
    last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row
    for col_name in col_list:
        col_letter = find_column_by_data(sheet, 1, col_name)
        if last_row > start_row:
            sheet.range(f'{col_letter}{start_row}:{col_letter}{last_row}').api.Font.ColorIndex = excel_color_index[
                color_name]

def add_formula_for_column(sheet, col_name, formula, start_row=2):
    last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row
    col_letter = find_column_by_data(sheet, 1, col_name)
    if last_row >= start_row:
        # 第3行公式（填一次）
        sheet.range(f'{col_letter}{start_row}').formula = formula
        if '汇总' in col_name:
            sheet.range(f'{col_letter}{start_row}').api.Font.Color = 255
        if last_row > start_row:
            # AutoFill 快速填充到所有行（start_row 到 last_row）
            sheet.range(f'{col_letter}{start_row}').api.AutoFill(
                sheet.range(f'{col_letter}{start_row}:{col_letter}{last_row}').api)

def autofit_column(sheet, columns=None):
    if columns is None:
        return
    used_range_col = sheet.range('A1').expand('right')
    for j, cell in enumerate(used_range_col):
        col = j + 1
        col_name = index_to_column_name(col)
        col_val = sheet.range(f'{col_name}1').value
        if col_val is None:
            continue
        for c in columns:
            if c in col_val:
                log(f'设置[{c}] 宽度自适应')
                sheet.range(f'{col_name}:{col_name}').api.WrapText = False
                sheet.range(f'{col_name}:{col_name}').autofit()
                sheet.range(f'{col_name}:{col_name}').api.WrapText = True
                sheet.range(f'{col_name}:{col_name}').autofit()

def specify_column_width(sheet, columns=None, width=150):
    if columns is None:
        return
    used_range_col = sheet.range('A1').expand('right')
    for j, cell in enumerate(used_range_col):
        col = j + 1
        col_name = index_to_column_name(col)
        col_val = sheet.range(f'{col_name}1').value
        if col_val is None:
            continue
        for c in columns:
            if c in col_val:
                log(f'设置[{c}]宽度: {width}')
                sheet.range(f'{col_name}:{col_name}').column_width = width

def format_to_money(sheet, columns=None):
    if columns is None:
        return
    used_range_col = sheet.range('A1').expand('right')
    for j, cell in enumerate(used_range_col):
        col = j + 1
        col_name = index_to_column_name(col)
        col_val = sheet.range(f'{col_name}1').value
        if col_val is None:
            continue
        for c in columns:
            if c in col_val:
                log(f'设置[{c}] 金额格式')
                sheet.range(f'{col_name}:{col_name}').number_format = '¥#,##0.00'

def format_to_percent(sheet, columns=None, decimal_places=2):
    if columns is None:
        return
    used_range_col = sheet.range('A1').expand('right')
    for j, cell in enumerate(used_range_col):
        col = j + 1
        col_name = index_to_column_name(col)
        col_val = sheet.range(f'{col_name}1').value
        if col_val is None:
            continue
        for c in columns:
            if c in col_val:
                log(f'设置[{c}] 百分比格式')
                # 根据 decimal_places 决定格式
                if decimal_places == 0:
                    sheet.range(f'{col_name}:{col_name}').number_format = '0%'
                else:
                    sheet.range(f'{col_name}:{col_name}').number_format = f'0.{"0" * decimal_places}%'

def format_to_number(sheet, columns=None, decimal_places=2):
    if not columns or not isinstance(columns, (list, tuple, set)):
        log(f'未提供有效列名列表（{columns}），跳过格式转换')
        return

    decimal_places = max(0, int(decimal_places))  # 确保非负整数
    used_range_col = sheet.range('A1').expand('right')

    for j, cell in enumerate(used_range_col):
        col = j + 1
        col_name = index_to_column_name(col)
        col_val = sheet.range(f'{col_name}1').value

        if col_val is None:
            continue

        col_val = str(col_val)  # 确保转为字符串比较
        for c in columns:
            if c in col_val:
                log(f'设置 [{c}] 列为数字格式，小数位 {decimal_places}')
                number_format = '0' if decimal_places == 0 else f'0.{"0" * decimal_places}'
                sheet.range(f'{col_name}:{col_name}').number_format = number_format
                break  # 如果一列只匹配一个关键词可提前退出

# def format_to_number(sheet, columns=None, decimal_places=2):
#     if columns is None or not isinstance(columns, list):
#         log('跳过格式化成数字', columns)
#         return
#     used_range_col = sheet.range('A1').expand('right')
#     for j, cell in enumerate(used_range_col):
#         col = j + 1
#         col_name = index_to_column_name(col)
#         col_val = sheet.range(f'{col_name}1').value
#         if col_val is None:
#             continue
#         for c in columns:
#             if c in col_val:
#                 log(f'设置[{c}] 数字格式')
#                 # 根据 decimal_places 决定格式
#                 if decimal_places == 0:
#                     sheet.range(f'{col_name}:{col_name}').number_format = '0'
#                 else:
#                     sheet.range(f'{col_name}:{col_name}').number_format = f'0.{"0" * decimal_places}'

def hidden_columns(sheet, columns=None):
    if columns is None:
        return
    used_range_col = sheet.range('A1').expand('right')
    for j, cell in enumerate(used_range_col):
        col = j + 1
        col_name = index_to_column_name(col)
        col_val = sheet.range(f'{col_name}1').value
        if col_val is None:
            continue
        for c in columns:
            if c in col_val:
                log(f'设置[{c}] 隐藏')
                sheet.range(f'{col_name}:{col_name}').column_width = 0

def column_to_right(sheet, columns=None):
    if columns is None:
        return
    used_range_col = sheet.range('A1').expand('right')
    for j, cell in enumerate(used_range_col):
        col = j + 1
        col_name = index_to_column_name(col)
        col_val = sheet.range(f'{col_name}1').value
        if col_val is None:
            continue
        for c in columns:
            if c in col_val:
                # 水平对齐： # -4108：居中 # -4131：左对齐 # -4152：右对齐
                # 垂直对齐： # -4108：居中 # -4160：顶部对齐 # -4107：底部对齐
                # 所有列水平居中和垂直居中
                log(f'设置[{c}] 水平右对齐')
                sheet.range(f'{col_name}:{col_name}').api.HorizontalAlignment = -4152
                sheet.range(f'{col_name}:{col_name}').api.VerticalAlignment = -4108

def column_to_left(sheet, columns=None):
    if columns is None:
        return
    used_range_col = sheet.range('A1').expand('right')
    for j, cell in enumerate(used_range_col):
        col = j + 1
        col_name = index_to_column_name(col)
        col_val = sheet.range(f'{col_name}1').value
        if col_val is None:
            continue
        for c in columns:
            if c in col_val:
                # 水平对齐： # -4108：居中 # -4131：左对齐 # -4152：右对齐
                # 垂直对齐： # -4108：居中 # -4160：顶部对齐 # -4107：底部对齐
                # 所有列水平居中和垂直居中
                log(f'设置[{c}] 左对齐')
                sheet.range(f'{col_name}:{col_name}').api.HorizontalAlignment = -4131
                sheet.range(f'{col_name}:{col_name}').api.VerticalAlignment = -4108

def beautify_title(sheet):
    log('美化标题')
    used_range_col = sheet.range('A1').expand('right')
    for j, cell in enumerate(used_range_col):
        col = j + 1
        col_name = index_to_column_name(col)

        # 设置标题栏字体颜色与背景色
        sheet.range(f'{col_name}1').color = (68, 114, 196)
        sheet.range(f'{col_name}1').font.size = 12
        sheet.range(f'{col_name}1').font.bold = True
        sheet.range(f'{col_name}1').font.color = (255, 255, 255)

        # 所有列水平居中和垂直居中
        sheet.range(f'{col_name}:{col_name}').api.HorizontalAlignment = -4108
        sheet.range(f'{col_name}:{col_name}').api.VerticalAlignment = -4108
    sheet.autofit()

def set_body_style(sheet, row_start, row_end=None):
    if row_end is None:
        row_end = get_last_used_row(sheet)

    range = sheet.range(f'{row_start}:{row_end}')
    # 设置字体名称
    range.font.name = 'Calibri'
    # 设置字体大小
    range.font.size = 11

def set_title_style(sheet, rows=2):
    col = get_max_column_letter(sheet)
    range = sheet.range(f'A1:{col}{rows}')
    # 设置字体名称
    range.font.name = '微软雅黑'
    # 设置字体大小
    range.font.size = 11
    # 设置字体加粗
    range.font.bold = True
    # 设置标题栏字体颜色与背景色
    range.color = (252, 228, 214)
    # 设置行高
    range.row_height = 30

    # 获取已使用范围
    used_range = sheet.used_range
    # 设置水平居中对齐
    used_range.api.HorizontalAlignment = xw.constants.HAlign.xlHAlignCenter
    used_range.api.VerticalAlignment = xw.constants.HAlign.xlHAlignCenter

    sheet.autofit()

def move_sheet_to_position(wb, sheet_name, position):
    # 获取要移动的工作表
    sheet = wb.sheets[sheet_name]
    # 获取目标位置的参考工作表
    if position == 1:
        # 如果目标位置是第一个，将其移至最前
        sheet.api.Move(Before=wb.sheets[0].api)
    else:
        # 如果目标位置不是第一个，将其移至目标位置之前
        sheet.api.Move(Before=wb.sheets[position - 1].api)
    # 保存工作簿
    wb.save()

# Excel 文件锁管理器
import threading
import time
from collections import defaultdict

class ExcelFileLockManager:
    """Excel 文件锁管理器，用于管理不同 Excel 文件的并发访问"""

    def __init__(self):
        self._locks = defaultdict(threading.Lock)
        self._excel_instances = {}  # 存储已打开的 Excel 实例
        self._lock = threading.Lock()  # 保护内部数据结构的锁
        self._waiting_queue = defaultdict(list)  # 等待队列，按文件路径分组
        self._operation_count = defaultdict(int)  # 记录每个文件的操作次数
        self._max_wait_time = 300  # 最大等待时间（秒）

    def get_file_lock(self, excel_path):
        """获取指定 Excel 文件的锁"""
        return self._locks[excel_path]

    def acquire_excel_lock(self, excel_path, timeout=30, priority=0):
        """
        获取 Excel 文件锁，支持超时和优先级

        Args:
            excel_path: Excel 文件路径
            timeout: 超时时间（秒）
            priority: 优先级，数字越小优先级越高

        Returns:
            bool: 是否成功获取锁
        """
        lock = self.get_file_lock(excel_path)

        # 记录等待请求
        with self._lock:
            self._waiting_queue[excel_path].append({
                'priority' : priority,
                'timestamp': time.time(),
                'thread_id': threading.get_ident()
            })
            # 按优先级排序
            self._waiting_queue[excel_path].sort(key=lambda x: (x['priority'], x['timestamp']))

        try:
            acquired = lock.acquire(timeout=timeout)
            if acquired:
                # 记录操作次数
                with self._lock:
                    self._operation_count[excel_path] += 1
                    # 从等待队列中移除
                    self._waiting_queue[excel_path] = [
                        item for item in self._waiting_queue[excel_path]
                        if item['thread_id'] != threading.get_ident()
                    ]
                log(f"成功获取 Excel 文件锁: {os.path.basename(excel_path)} (优先级: {priority})")
                return True
            else:
                log(f"获取 Excel 文件锁超时: {excel_path} (优先级: {priority})")
                return False
        except Exception as e:
            log(f"获取 Excel 文件锁异常: {e}")
            return False

    def release_excel_lock(self, excel_path):
        """释放 Excel 文件锁"""
        lock = self.get_file_lock(excel_path)
        if lock.locked():
            lock.release()
            log(f"释放 Excel 文件锁: {os.path.basename(excel_path)}")

    def get_excel_instance(self, excel_path):
        """获取已打开的 Excel 实例"""
        with self._lock:
            return self._excel_instances.get(excel_path)

    def set_excel_instance(self, excel_path, app, wb):
        """设置 Excel 实例"""
        with self._lock:
            self._excel_instances[excel_path] = (app, wb)

    def remove_excel_instance(self, excel_path):
        """移除 Excel 实例"""
        with self._lock:
            self._excel_instances.pop(excel_path, None)

    def is_excel_open(self, excel_path):
        """检查 Excel 文件是否已打开"""
        return excel_path in self._excel_instances

    def get_waiting_count(self, excel_path):
        """获取等待该文件的线程数量"""
        with self._lock:
            return len(self._waiting_queue[excel_path])

    def get_operation_count(self, excel_path):
        """获取该文件的操作次数"""
        with self._lock:
            return self._operation_count[excel_path]

    def cleanup_old_instances(self, max_age=3600):
        """清理过期的 Excel 实例"""
        current_time = time.time()
        with self._lock:
            expired_files = []
            for excel_path, (app, wb) in self._excel_instances.items():
                # 这里可以添加更复杂的清理逻辑
                # 比如检查文件最后访问时间等
                pass

# 全局 Excel 文件锁管理器实例
excel_lock_manager = ExcelFileLockManager()

def open_excel_with_lock(excel_path, sheet_name='Sheet1', timeout=30):
    """
    带锁的 Excel 打开函数，支持复用已打开的实例

    Args:
        excel_path: Excel 文件路径
        sheet_name: 工作表名称
        timeout: 获取锁的超时时间（秒）

    Returns:
        tuple: (app, wb, sheet) 或 (None, None, None) 如果失败
    """
    if not excel_lock_manager.acquire_excel_lock(excel_path, timeout):
        return None, None, None

    try:
        # 检查是否已有打开的实例
        existing_instance = excel_lock_manager.get_excel_instance(excel_path)
        if existing_instance:
            app, wb = existing_instance
            # 检查工作簿是否仍然有效
            try:
                if wb.name in [book.name for book in app.books]:
                    # 获取指定的工作表
                    if isinstance(sheet_name, int):
                        if 0 <= sheet_name < len(wb.sheets):
                            sheet = wb.sheets[sheet_name]
                        else:
                            sheet = wb.sheets.add(after=wb.sheets[-1])
                    elif isinstance(sheet_name, str):
                        sheet_names = [s.name.strip().lower() for s in wb.sheets]
                        if sheet_name.strip().lower() in sheet_names:
                            sheet = wb.sheets[sheet_name]
                        else:
                            sheet = wb.sheets.add(sheet_name, after=wb.sheets[-1])
                    else:
                        raise ValueError(f"sheet_name 必须是字符串或整数: {sheet_name}")

                    sheet.activate()
                    log(f"复用已打开的 Excel: {os.path.basename(excel_path)} {sheet.name}")
                    return app, wb, sheet
            except Exception as e:
                log(f"复用 Excel 实例失败，重新打开: {e}")
                # 移除无效的实例
                excel_lock_manager.remove_excel_instance(excel_path)

        # 打开新的 Excel 实例
        app, wb, sheet = open_excel(excel_path, sheet_name)
        if app and wb:
            excel_lock_manager.set_excel_instance(excel_path, app, wb)
            log(f"打开新的 Excel 实例: {os.path.basename(excel_path)} {sheet.name}")

        return app, wb, sheet

    except Exception as e:
        log(f"打开 Excel 失败: {e}")
        excel_lock_manager.release_excel_lock(excel_path)
        return None, None, None

def close_excel_with_lock(excel_path, app, wb, force_close=False):
    """
    带锁的 Excel 关闭函数

    Args:
        excel_path: Excel 文件路径
        app: Excel 应用实例
        wb: 工作簿实例
        force_close: 是否强制关闭（即使有其他操作在进行）
    """
    try:
        if force_close:
            # 强制关闭，移除实例记录
            excel_lock_manager.remove_excel_instance(excel_path)
            close_excel(app, wb)
        else:
            # 只保存，不关闭
            if wb:
                wb.save()
            log(f"保存 Excel 文件: {os.path.basename(excel_path)}")
    except Exception as e:
        log(f"关闭 Excel 失败: {e}")
    finally:
        excel_lock_manager.release_excel_lock(excel_path)

def write_data_with_lock(excel_path, sheet_name, data, format_to_text_colunm=None):
    """
    带锁的数据写入函数，复用 Excel 实例

    Args:
        excel_path: Excel 文件路径
        sheet_name: 工作表名称
        data: 要写入的数据
        format_to_text_colunm: 格式化为文本的列
    """
    app, wb, sheet = open_excel_with_lock(excel_path, sheet_name)
    if not app or not wb or not sheet:
        log(f"无法打开 Excel 文件: {excel_path}")
        return False

    try:
        # 清空工作表中的所有数据
        sheet.clear()
        # 某些列以文本格式写入
        format_to_text_v2(sheet, format_to_text_colunm)
        # 写入数据
        sheet.range('A1').value = data
        # 保存
        wb.save()
        log(f"成功写入数据到 {sheet_name}")
        return True
    except Exception as e:
        log(f"写入数据失败: {e}")
        return False

def format_excel_with_lock(excel_path, sheet_name, format_func, *args, **kwargs):
    """
    带锁的 Excel 格式化函数

    Args:
        excel_path: Excel 文件路径
        sheet_name: 工作表名称
        format_func: 格式化函数
        *args, **kwargs: 传递给格式化函数的参数
    """
    app, wb, sheet = open_excel_with_lock(excel_path, sheet_name)
    if not app or not wb or not sheet:
        log(f"无法打开 Excel 文件进行格式化: {excel_path}")
        return False

    try:
        # 执行格式化函数
        format_func(sheet, *args, **kwargs)
        # 保存
        wb.save()
        log(f"成功格式化工作表: {sheet_name}")
        return True
    except Exception as e:
        log(f"格式化失败: {e}")
        return False

# 经过观察 fortmat时 传入函数需要为类函数且第二个参数必须是 sheet
def batch_excel_operations(excel_path, operations):
    """
    批量 Excel 操作函数，自动分批处理，避免一次操作过多sheet导致Excel COM错误
    保持操作的原始顺序执行
    
    Args:
        excel_path: Excel 文件路径
        operations: 操作列表，每个操作是 (sheet_name, operation_type, data, format_func) 的元组
                   operation_type: 'write', 'format', 'delete', 'move', 'active'
                   
    Returns:
        bool: 是否全部操作成功
    """
    if not operations:
        return True

    # 批处理大小设置：每批最多处理8个操作
    MAX_OPERATIONS_PER_BATCH = 8

    try:
        # 计算需要分几批
        total_batches = (len(operations) + MAX_OPERATIONS_PER_BATCH - 1) // MAX_OPERATIONS_PER_BATCH
        log(f"分{total_batches}批执行{len(operations)}个操作，每批最多{MAX_OPERATIONS_PER_BATCH}个，保持原始顺序")

        # 按顺序分批执行
        for batch_idx in range(total_batches):
            start_idx = batch_idx * MAX_OPERATIONS_PER_BATCH
            end_idx = min(start_idx + MAX_OPERATIONS_PER_BATCH, len(operations))
            batch_operations = operations[start_idx:end_idx]

            log(f"执行第{batch_idx + 1}/{total_batches}批操作（{start_idx + 1}-{end_idx}），共{len(batch_operations)}个操作")

            # 重试机制
            max_retries = 3
            for retry in range(max_retries):
                try:
                    # 强制垃圾回收
                    import gc
                    gc.collect()

                    if _execute_operations_batch(excel_path, batch_operations):
                        log(f"第{batch_idx + 1}批操作成功")
                        break
                    else:
                        log(f"第{batch_idx + 1}批操作失败，重试 {retry + 1}/{max_retries}")
                        if retry == max_retries - 1:
                            log(f"第{batch_idx + 1}批操作最终失败")
                            return False
                        import time
                        time.sleep(3)
                except Exception as e:
                    log(f"第{batch_idx + 1}批操作异常: {e}")
                    if retry == max_retries - 1:
                        return False
                    import time
                    time.sleep(3)

            # 批次间延迟
            if batch_idx < total_batches - 1:
                import time
                time.sleep(1)

        log(f"所有批量操作完成: {excel_path}")
        return True

    except Exception as e:
        log(f"批量操作过程异常: {e}")
        return False

def _execute_operations_batch(excel_path, operations):
    """
    执行单个批次的操作
    """
    app, wb, sheet = open_excel_with_lock(excel_path)
    if not app or not wb:
        log(f"无法打开 Excel 文件: {excel_path}")
        return False

    try:
        for sheet_name, operation_type, *args in operations:
            # 根据操作类型决定是否需要获取或创建工作表
            sheet = None

            # 删除操作不需要获取sheet对象
            if operation_type == 'delete':
                log(f'删除sheet: {sheet_name}')
                delete_sheet_if_exists(wb, sheet_name)
                continue

            # 其他操作需要获取或创建工作表
            if isinstance(sheet_name, str):
                sheet_names = [s.name.strip().lower() for s in wb.sheets]
                if sheet_name.strip().lower() in sheet_names:
                    sheet = wb.sheets[sheet_name]
                else:
                    # 只有在需要操作sheet内容时才创建
                    if operation_type in ['write', 'format']:
                        sheet = wb.sheets.add(sheet_name, after=wb.sheets[-1])
                    else:
                        log(f"警告: 操作 {operation_type} 需要的sheet {sheet_name} 不存在，跳过此操作")
                        continue
            else:
                sheet = wb.sheets[sheet_name]

            if sheet:
                sheet.activate()

            if operation_type == 'write':
                data, format_to_text_colunm = args[0], args[1:] if len(args) > 1 else None
                # 清空工作表
                sheet.clear()

                # 先设置文本格式，再写入数据（确保格式生效）
                if format_to_text_colunm and format_to_text_colunm[0]:
                    try:
                        # 使用安全的预格式化方式
                        pre_format_columns_safe(sheet, format_to_text_colunm[0], len(data))
                    except Exception as e:
                        log(f"预格式化失败: {e}，继续执行")

                # 写入数据
                log(f"批量操作,写入数据到: {sheet_name}")
                sheet.range('A1').value = data

                # 写入后再次确认格式（双重保险）
                if format_to_text_colunm and format_to_text_colunm[0]:
                    try:
                        post_format_columns_safe(sheet, format_to_text_colunm[0], len(data))
                    except Exception as e:
                        log(f"后格式化失败: {e}")

            elif operation_type == 'format':
                format_func, format_args = args[0], args[1:] if len(args) > 1 else ()
                # 执行格式化
                format_func(sheet, *format_args)

            elif operation_type == 'move':
                log(f'移动sheet: {sheet_name}')
                position = args[0]
                move_sheet_to_position(wb, sheet_name, position)

            elif operation_type == 'active':
                log(f'激活sheet: {sheet_name}')
                sheet.activate()

        # 保存所有更改
        wb.save()
        return True

    except Exception as e:
        log(f"单批次操作失败: {e}")
        return False
    finally:
        # 释放锁但不关闭 Excel（保持复用）
        excel_lock_manager.release_excel_lock(excel_path)
        close_excel_with_lock(excel_path, app, wb, True)

def close_excel_file(file_path):
    file_path = os.path.abspath(file_path).lower()

    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and proc.info['name'].lower() in ['excel.exe', 'wps.exe']:  # 只找 Excel
            try:
                for f in proc.open_files():
                    if os.path.abspath(f.path).lower() == file_path:
                        print(f"文件被 Excel 占用 (PID: {proc.pid})，正在关闭进程...")
                        proc.terminate()
                        proc.wait(timeout=3)
                        print("已关闭。")
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    print("文件没有被 Excel 占用。")
    return False

def force_close_excel_file(excel_path):
    """
    强制关闭指定的 Excel 文件

    Args:
        excel_path: Excel 文件路径
    """
    try:
        existing_instance = excel_lock_manager.get_excel_instance(excel_path)
        if existing_instance:
            app, wb = existing_instance
            close_excel_with_lock(excel_path, app, wb, force_close=True)
            log(f"强制关闭 Excel 文件: {excel_path}")
    except Exception as e:
        log(f"强制关闭 Excel 文件失败: {e}")

def wait_for_excel_available(excel_path, timeout=60, check_interval=1):
    """
    等待 Excel 文件可用

    Args:
        excel_path: Excel 文件路径
        timeout: 超时时间（秒）
        check_interval: 检查间隔（秒）

    Returns:
        bool: 是否成功获取锁
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if excel_lock_manager.acquire_excel_lock(excel_path, timeout=0):
            return True
        time.sleep(check_interval)

    log(f"等待 Excel 文件可用超时: {excel_path}")
    return False

def smart_excel_operation(excel_path, operation_func, priority=0, timeout=60, max_retries=3):
    """
    智能 Excel 操作函数，支持优先级、重试和更好的错误处理

    Args:
        excel_path: Excel 文件路径
        operation_func: 要执行的操作函数，接收 (app, wb, sheet) 参数
        priority: 优先级，数字越小优先级越高
        timeout: 获取锁的超时时间（秒）
        max_retries: 最大重试次数

    Returns:
        bool: 操作是否成功
    """
    for attempt in range(max_retries):
        try:
            # 检查是否有其他程序正在操作该文件
            waiting_count = excel_lock_manager.get_waiting_count(excel_path)
            if waiting_count > 0:
                log(f"等待其他程序完成操作: {os.path.basename(excel_path)} (等待队列: {waiting_count})")

            # 尝试获取锁
            if not excel_lock_manager.acquire_excel_lock(excel_path, timeout, priority):
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # 递增等待时间
                    log(f"获取锁失败，等待 {wait_time} 秒后重试 (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    log(f"达到最大重试次数，操作失败: {excel_path}")
                    return False

            # 打开 Excel
            app, wb, sheet = open_excel_with_lock(excel_path)
            if not app or not wb:
                log(f"无法打开 Excel 文件: {excel_path}")
                return False

            try:
                # 执行操作
                result = operation_func(app, wb, sheet)

                # 保存更改
                if wb:
                    wb.save()
                    log(f"成功保存 Excel 文件: {os.path.basename(excel_path)}")

                return result

            except Exception as e:
                log(f"Excel 操作失败: {e}")
                return False
            finally:
                # 释放锁但不关闭 Excel（保持复用）
                excel_lock_manager.release_excel_lock(excel_path)

        except Exception as e:
            log(f"智能 Excel 操作异常: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                return False

    return False

def batch_excel_operations_with_priority(excel_path, operations, priority=0, timeout=60):
    """
    带优先级的批量 Excel 操作函数

    Args:
        excel_path: Excel 文件路径
        operations: 操作列表
        priority: 优先级
        timeout: 超时时间

    Returns:
        bool: 是否全部操作成功
    """

    def batch_operation(app, wb, sheet):
        try:
            for sheet_name, operation_type, *args in operations:
                # 获取或创建工作表
                if isinstance(sheet_name, str):
                    sheet_names = [s.name.strip().lower() for s in wb.sheets]
                    if sheet_name.strip().lower() in sheet_names:
                        sheet = wb.sheets[sheet_name]
                    else:
                        sheet = wb.sheets.add(sheet_name, after=wb.sheets[-1])
                else:
                    sheet = wb.sheets[sheet_name]

                sheet.activate()

                if operation_type == 'write':
                    data, format_to_text_colunm = args[:2]
                    # 清空工作表
                    sheet.clear()
                    # 格式化文本列
                    format_to_text_v2(sheet, format_to_text_colunm)
                    # 写入数据
                    sheet.range('A1').value = data
                    log(f"批量操作：写入数据到 {sheet_name}")

                elif operation_type == 'format':
                    format_func, format_args = args[0], args[1:] if len(args) > 1 else ()
                    # 执行格式化
                    format_func(sheet, *format_args)
                    log(f"批量操作：格式化工作表 {sheet_name}")

            return True

        except Exception as e:
            log(f"批量操作失败: {e}")
            return False

    return smart_excel_operation(excel_path, batch_operation, priority, timeout)

def wait_for_excel_available_with_priority(excel_path, timeout=60, check_interval=1, priority=0):
    """
    等待 Excel 文件可用（带优先级）

    Args:
        excel_path: Excel 文件路径
        timeout: 超时时间（秒）
        check_interval: 检查间隔（秒）
        priority: 优先级

    Returns:
        bool: 是否成功获取锁
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if excel_lock_manager.acquire_excel_lock(excel_path, timeout=0, priority=priority):
            return True
        time.sleep(check_interval)

    log(f"等待 Excel 文件可用超时: {excel_path}")
    return False

def get_excel_status(excel_path):
    """
    获取 Excel 文件状态信息

    Args:
        excel_path: Excel 文件路径

    Returns:
        dict: 状态信息
    """
    return {
        'is_open'        : excel_lock_manager.is_excel_open(excel_path),
        'waiting_count'  : excel_lock_manager.get_waiting_count(excel_path),
        'operation_count': excel_lock_manager.get_operation_count(excel_path),
        'has_lock'       : excel_lock_manager.get_file_lock(excel_path).locked()
    }

def get_last_used_row(sheet):
    return sheet.used_range.last_cell.row
