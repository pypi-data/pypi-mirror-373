# -*- coding: UTF-8 -*-
import json
import time
from .feishu_client import FeishuClient

from .fun_base import log

class FeishuBusinessLogic:
    def __init__(self, client: FeishuClient):
        self.client = client

    def get_all_folder_files(self, folder_token: str):
        # 获取文件夹中所有文件（自动处理分页）
        all_files = []
        page_token = None

        while True:
            data = self.client.list_folder_files(folder_token, page_token=page_token)
            files = data.get("files", [])
            all_files.extend(files)

            page_token = data.get("next_page_token")
            if not page_token:
                break

        return all_files

    def get_all_permission_members(self, token: str, type: str):
        # 获取文档所有权限成员（自动处理分页）
        all_members = []
        page_token = None

        while True:
            data = self.client.list_permission_members(token, type, page_token=page_token)
            members = data.get("members", [])
            all_members.extend(members)

            page_token = data.get("next_page_token")
            if not page_token:
                break

        return all_members

    def number_to_excel_column(self, num: int):
        # 将数字转换为Excel列名（1->A, 2->B, 26->Z, 27->AA）
        result = ""
        while num > 0:
            num -= 1
            result = chr(65 + num % 26) + result
            num //= 26
        return result

    def get_existing_column_values(self, spreadsheet_token: str, sheet_id: str, column_name: str, header_row: int = 1):
        # 获取指定列中已存在的所有值
        all_data = self.client.read_sheet_data(spreadsheet_token, sheet_id)
        if not all_data or len(all_data.get("valueRange", {}).get("values", [])) < header_row:
            return set()

        values = all_data["valueRange"]["values"]
        headers = values[header_row - 1] if len(values) >= header_row else []

        column_index = -1
        for i, header in enumerate(headers):
            if str(header).strip() == column_name:
                column_index = i
                break

        if column_index == -1:
            return set()

        existing_values = set()
        for row_index in range(header_row, len(values)):
            row = values[row_index]
            if len(row) > column_index and row[column_index]:
                value = str(row[column_index]).strip()
                if value:
                    existing_values.add(value)

        return existing_values

    def get_existing_row_combinations(self, spreadsheet_token: str, sheet_id: str, key_columns: list, header_row: int = 1):
        # 获取表格中已存在的行数据组合（基于关键字段）
        all_data = self.client.read_sheet_data(spreadsheet_token, sheet_id)
        if not all_data or len(all_data.get("valueRange", {}).get("values", [])) < header_row:
            return set()

        values = all_data["valueRange"]["values"]
        headers = values[header_row - 1] if len(values) >= header_row else []

        key_indices = []
        for col_name in key_columns:
            column_index = -1
            for i, header in enumerate(headers):
                if str(header).strip() == col_name:
                    column_index = i
                    break
            if column_index != -1:
                key_indices.append(column_index)

        if not key_indices:
            return set()

        existing_combinations = set()
        for row_index in range(header_row, len(values)):
            row = values[row_index]
            key_values = []
            for idx in key_indices:
                if len(row) > idx and row[idx] is not None:
                    key_values.append(str(row[idx]).strip())
                else:
                    key_values.append("")

            if all(value for value in key_values):
                combination_key = "|".join(key_values)
                existing_combinations.add(combination_key)

        return existing_combinations

    def append_data_with_deduplication(self, spreadsheet_token: str, sheet_id: str, values: list,
            dedup_columns: list, insert_data_option: str = "INSERT_ROWS", header_row: int = 1,
            reference_column: str = None):
        # 向工作表追加数据，根据指定字段组合去重
        if not values or len(values) < 2:
            return {
                "status"       : "success",
                "message"      : "无数据需要插入",
                "total_rows"   : 0,
                "inserted_rows": 0,
                "skipped_rows" : 0
            }

        # 获取现有数据中的行组合
        existing_combinations = self.get_existing_row_combinations(spreadsheet_token, sheet_id, dedup_columns, header_row)

        headers = values[0]
        data_rows = values[1:]

        # 找到去重字段的索引
        dedup_indices = []
        for col_name in dedup_columns:
            try:
                column_index = headers.index(col_name)
                dedup_indices.append(column_index)
            except ValueError:
                pass

        if not dedup_indices:
            raise Exception(f"在数据表头中未找到任何去重字段: {dedup_columns}")

        # 过滤重复数据 - 只剔除与表格已存在数据重复的记录
        filtered_rows = []
        skipped_count = 0

        for row in data_rows:
            key_values = []
            for idx in dedup_indices:
                if len(row) > idx and row[idx] is not None:
                    key_values.append(str(row[idx]).strip())
                else:
                    key_values.append("")

            if all(value for value in key_values):
                combination_key = "|".join(key_values)
                if combination_key in existing_combinations:
                    skipped_count += 1
                    continue

            filtered_rows.append(row)

        if not filtered_rows:
            return {
                "status"       : "success",
                "message"      : f"所有数据都已存在，共跳过 {skipped_count} 行重复数据",
                "total_rows"   : len(data_rows),
                "inserted_rows": 0,
                "skipped_rows" : skipped_count
            }

        # 插入过滤后的数据
        if reference_column:
            # 使用精确位置插入避免覆盖原有数据
            append_result = self._insert_data_at_precise_position_with_reference_column(
                spreadsheet_token, sheet_id, filtered_rows, headers, reference_column, insert_data_option
            )
        else:
            # 回退到普通追加
            append_result = self.client.write_data_to_range(spreadsheet_token, sheet_id, "A:A", filtered_rows, insert_data_option)

        return {
            "status"       : "success",
            "message"      : f"成功插入 {len(filtered_rows)} 行新数据，跳过 {skipped_count} 行重复数据",
            "total_rows"   : len(data_rows),
            "inserted_rows": len(filtered_rows),
            "skipped_rows" : skipped_count,
            "append_result": append_result
        }

    def analyze_merge_ranges(self, data_rows: list, merge_column_index: int):
        # 分析数据，找出需要合并的行范围
        merge_ranges = []
        current_value = None
        start_row = 0

        for i, row in enumerate(data_rows):
            if len(row) <= merge_column_index:
                continue

            row_value = row[merge_column_index]

            if current_value is None:
                current_value = row_value
                start_row = i
            elif row_value != current_value:
                if i - 1 > start_row:
                    merge_ranges.append({
                        'start_row': start_row,
                        'end_row'  : i - 1,
                        'value'    : current_value
                    })

                current_value = row_value
                start_row = i

        # 处理最后一个合并范围
        if len(data_rows) - 1 > start_row:
            merge_ranges.append({
                'start_row': start_row,
                'end_row'  : len(data_rows) - 1,
                'value'    : current_value
            })

        return merge_ranges

    def _insert_data_at_precise_position_with_reference_column(self, spreadsheet_token: str, sheet_id: str,
            data_rows: list, headers: list, reference_column: str,
            insert_data_option: str = "INSERT_ROWS"):
        # 使用参考列确定准确插入位置的数据插入方法
        log(f"[DEBUG] 使用参考列 '{reference_column}' 进行精确位置插入")

        try:
            # 找到参考列的索引
            try:
                ref_column_index = headers.index(reference_column)
                ref_column_letter = self.number_to_excel_column(ref_column_index + 1)
                log(f"[DEBUG] 参考列索引: {ref_column_index}, 列字母: {ref_column_letter}")
            except ValueError:
                log(f"[DEBUG] 未找到参考列 '{reference_column}'，回退到普通追加")
                return self.client.write_data_to_range(spreadsheet_token, sheet_id, "A:A", data_rows, insert_data_option)

            # 读取参考列的数据来确定当前总行数
            ref_column_range = f"{ref_column_letter}:{ref_column_letter}"
            data = self.client.read_multiple_ranges(spreadsheet_token, sheet_id, [ref_column_range])

            value_ranges = data.get("valueRanges", [])
            if not value_ranges:
                log(f"[DEBUG] 无法读取参考列数据，回退到普通追加")
                return self.client.write_data_to_range(spreadsheet_token, sheet_id, "A:A", data_rows, insert_data_option)

            # 获取参考列所有数据
            first_range = value_ranges[0]
            all_column_values = first_range.get("values", [])

            # 计算当前总行数（包括表头）
            total_rows = len(all_column_values)

            # 新数据的起始行号（表格行号，从1开始）
            insert_start_row = total_rows + 1

            log(f"[DEBUG] 当前总行数: {total_rows}, 新数据起始行: {insert_start_row}")

            # 计算数据范围
            rows_count = len(data_rows)
            cols_count = len(data_rows[0]) if data_rows else 0

            # 构建插入范围
            if cols_count > 0:
                end_col = self.number_to_excel_column(cols_count)
            else:
                end_col = 'A'
            range_str = f"A{insert_start_row}:{end_col}{insert_start_row + rows_count - 1}"

            log(f"[DEBUG] 精确插入位置: {range_str}，插入 {rows_count} 行数据")

            # 使用精确范围写入数据
            result = self.client.write_data_to_range(spreadsheet_token, sheet_id, range_str, data_rows)
            log(f"[DEBUG] 成功在精确位置插入数据")
            return result

        except Exception as e:
            log(f"[DEBUG] 精确位置插入失败，回退到普通追加: {str(e)}")
            return self.client.write_data_to_range(spreadsheet_token, sheet_id, "A:A", data_rows, insert_data_option)

    def _perform_merge_for_empty_sheet(self, spreadsheet_token: str, sheet_id: str, data_list: list,
            merge_column: str, merge_columns: list, dedup_result: dict):
        # 对空表格插入的数据进行合并操作
        log(f"[DEBUG] _perform_merge_for_empty_sheet 开始执行")
        log(f"[DEBUG] data_list 长度: {len(data_list)}")

        try:
            headers = data_list[0]  # 表头
            data_rows = data_list[1:]  # 数据行

            log(f"[DEBUG] 表头: {headers[:5]}...")  # 只显示前5列
            log(f"[DEBUG] 数据行数: {len(data_rows)}")
            log(f"[DEBUG] 第一行数据: {data_rows[0][:5] if data_rows else '无数据'}...")

            # 找到基准列和需要合并的列的索引
            try:
                merge_column_index = headers.index(merge_column)
                log(f"[DEBUG] 找到基准列 '{merge_column}' 的索引: {merge_column_index}")
            except ValueError:
                log(f"[DEBUG] 未找到基准列 '{merge_column}' 在表头中")
                return {
                    "status"      : "success",
                    "message"     : dedup_result.get("message", "") + f"，未找到基准列 '{merge_column}'",
                    "dedup_result": dedup_result,
                    "merge_result": {"merge_count": 0, "message": f"未找到基准列 '{merge_column}'"}
                }

            merge_column_indices = []
            for col_name in merge_columns:
                try:
                    idx = headers.index(col_name)
                    merge_column_indices.append(idx)
                    log(f"[DEBUG] 找到需要合并的列 '{col_name}' 的索引: {idx}")
                except ValueError:
                    log(f"[DEBUG] 未找到需要合并的列 '{col_name}' 在表头中")

            log(f"[DEBUG] 总共找到 {len(merge_column_indices)} 个需要合并的列")

            if not merge_column_indices:
                log(f"[DEBUG] 没有找到任何需要合并的列，退出合并操作")
                return {
                    "status"      : "success",
                    "message"     : dedup_result.get("message", "") + "，未找到需要合并的列",
                    "dedup_result": dedup_result,
                    "merge_result": {"merge_count": 0, "message": "未找到需要合并的列"}
                }

            # 分析合并范围
            log(f"[DEBUG] 开始分析合并范围...")
            merge_ranges = self.analyze_merge_ranges(data_rows, merge_column_index)
            log(f"[DEBUG] 分析完成，找到 {len(merge_ranges)} 个合并范围")

            for i, merge_range in enumerate(merge_ranges):
                log(f"[DEBUG] 合并范围 {i + 1}: 第{merge_range['start_row'] + 1}行到第{merge_range['end_row'] + 1}行，值: {merge_range['value']}")

            # 执行合并操作
            merge_count = 0
            log(f"[DEBUG] 开始执行合并操作...")

            for merge_group in merge_ranges:
                start_row = merge_group['start_row']
                end_row = merge_group['end_row']

                log(f"[DEBUG] 处理合并组: 第{start_row}行到第{end_row}行")

                if end_row > start_row:
                    for col_index in merge_column_indices:
                        col_letter = self.number_to_excel_column(col_index + 1)
                        # 注意：数据从第2行开始（第1行是表头），所以要+2
                        range_str = f"{col_letter}{start_row + 2}:{col_letter}{end_row + 2}"

                        log(f"[DEBUG] 尝试合并单元格范围: {range_str}")

                        try:
                            self.client.merge_cells(spreadsheet_token, sheet_id, "MERGE_ALL", range_str)
                            merge_count += 1
                            log(f"[DEBUG] 成功合并单元格: {range_str}")
                        except Exception as e:
                            log(f"[DEBUG] 合并单元格失败: {range_str}, 错误: {str(e)}")
                else:
                    log(f"[DEBUG] 跳过合并（只有一行）: 第{start_row}行")

            return {
                "status"      : "success",
                "message"     : f"{dedup_result.get('message', '')}，成功合并 {merge_count} 个单元格范围",
                "dedup_result": dedup_result,
                "merge_result": {
                    "merge_count": merge_count,
                    "message"    : f"成功合并 {merge_count} 个单元格范围"
                }
            }

        except Exception as e:
            return {
                "status"      : "success",
                "message"     : dedup_result.get("message", "") + f"，合并操作失败: {str(e)}",
                "dedup_result": dedup_result,
                "merge_result": {"merge_count": 0, "message": f"合并操作失败: {str(e)}"}
            }

    def write_data_and_merge_by_column_with_deduplication(self, spreadsheet_token: str, sheet_id: str,
            data_list: list, dedup_column: str, merge_column: str,
            merge_columns: list, reference_column: str, header_row: int = 1, image_column: str = None):
        # 写入数据并根据指定列的值合并相关列的单元格（带去重功能）
        log(f"[DEBUG] write_data_and_merge_by_column_with_deduplication 开始执行")
        log(f"[DEBUG] 参数: dedup_column={dedup_column}, merge_column={merge_column}")
        log(f"[DEBUG] merge_columns={merge_columns}")
        log(f"[DEBUG] reference_column={reference_column}")
        log(f"[DEBUG] data_list 长度: {len(data_list) if data_list else 0}")

        # 检查表格是否为空
        try:
            log(f"[DEBUG] 检查表格是否为空...")
            first_row_data = self.client.read_multiple_ranges(spreadsheet_token, sheet_id, ["A1:ZZ1"])
            value_ranges = first_row_data.get("valueRanges", [])

            # 更严格的空表格检查：不仅要有数据，还要有非空的内容
            if not value_ranges or not value_ranges[0].get("values"):
                is_empty_sheet = True
                log(f"[DEBUG] 表格完全为空")
            else:
                first_row = value_ranges[0]["values"][0]
                # 检查第一行是否有任何非空值
                has_non_empty_values = any(cell and str(cell).strip() for cell in first_row)
                is_empty_sheet = not has_non_empty_values
                log(f"[DEBUG] 第一行数据: {first_row[:5]}...")
                log(f"[DEBUG] 第一行是否有非空值: {has_non_empty_values}")

            log(f"[DEBUG] 表格空状态检查结果: is_empty_sheet={is_empty_sheet}")
        except Exception as e:
            log(f"[DEBUG] 检查表格空状态时出错: {str(e)}，默认认为是空表格")
            is_empty_sheet = True

        if is_empty_sheet:
            log(f"[DEBUG] 检测到空表格，开始插入数据...")
            log(f"[DEBUG] 数据行数: {len(data_list)} 行")

            # 空表格直接插入所有数据
            self.client.write_data_to_range(spreadsheet_token, sheet_id, "A:A", data_list, "INSERT_ROWS")
            inserted_rows = len(data_list) - 1 if data_list else 0

            log(f"[DEBUG] 数据插入完成，插入了 {inserted_rows} 行数据")

            dedup_result = {
                "total_rows"   : inserted_rows,
                "inserted_rows": inserted_rows,
                "skipped_rows" : 0,
                "message"      : f"成功插入 {inserted_rows} 行新数据（空表格直接插入）"
            }

            # 空表格插入数据后也需要进行合并操作
            if not data_list or len(data_list) < 2:
                log(f"[DEBUG] 数据不足，无需合并。data_list长度: {len(data_list) if data_list else 0}")
                return {
                    "status"      : "success",
                    "message"     : "数据插入完成，但数据不足无需合并",
                    "dedup_result": dedup_result,
                    "merge_result": {"merge_count": 0, "message": "数据不足无需合并"}
                }

            log(f"[DEBUG] 开始对空表格插入的数据进行合并操作...")
            log(f"[DEBUG] 基准列: {merge_column}, 需要合并的列: {merge_columns}")

            # 对空表格插入的数据进行合并操作
            merge_result = self._perform_merge_for_empty_sheet(
                spreadsheet_token, sheet_id, data_list, merge_column, merge_columns, dedup_result
            )

            # 处理图片插入
            if image_column:
                try:
                    image_result = self._insert_images_for_empty_sheet(
                        spreadsheet_token, sheet_id, data_list, image_column
                    )
                    merge_result["image_result"] = image_result
                    merge_result["message"] += f"，{image_result.get('message', '')}"
                except Exception as e:
                    log(f"[DEBUG] 空表格图片插入失败: {str(e)}")
                    merge_result["image_result"] = {"image_count": 0, "message": f"图片插入失败: {str(e)}"}
            else:
                merge_result["image_result"] = {"image_count": 0, "message": "未指定图片列"}

            return merge_result
        else:
            log(f"[DEBUG] 检测到非空表格，进行去重插入...")
            # 非空表格进行去重插入，传递参考列参数
            dedup_result = self.append_data_with_deduplication(
                spreadsheet_token, sheet_id, data_list, [dedup_column], "INSERT_ROWS", header_row, reference_column
            )

        if dedup_result.get("inserted_rows", 0) == 0:
            return {
                "status"      : "success",
                "message"     : dedup_result.get("message", ""),
                "dedup_result": dedup_result,
                "merge_result": {"merge_count": 0, "message": "无需合并"}
            }

        # 执行合并操作
        merge_count = 0
        try:
            # 读取表头
            header_data = self.client.read_multiple_ranges(spreadsheet_token, sheet_id, [f"A{header_row}:ZZ{header_row}"])
            headers = header_data.get("valueRanges", [{}])[0].get("values", [[]])[0] if header_data.get("valueRanges") else []

            if not headers:
                return {
                    "status"      : "success",
                    "message"     : dedup_result.get("message", "") + "，无法读取表头跳过合并",
                    "dedup_result": dedup_result,
                    "merge_result": {"merge_count": 0, "message": "无法读取表头"}
                }

            # 找到基准列和需要合并的列的索引
            merge_column_index = headers.index(merge_column)
            merge_column_indices = []
            for col_name in merge_columns:
                try:
                    merge_column_indices.append(headers.index(col_name))
                except ValueError:
                    pass

            if not merge_column_indices:
                return {
                    "status"      : "success",
                    "message"     : dedup_result.get("message", "") + "，未找到需要合并的列",
                    "dedup_result": dedup_result,
                    "merge_result": {"merge_count": 0, "message": "未找到需要合并的列"}
                }

            # 使用参考列确定总行数
            ref_column_index = headers.index(reference_column)
            ref_column_letter = self.number_to_excel_column(ref_column_index + 1)

            ref_data = self.client.read_multiple_ranges(spreadsheet_token, sheet_id, [f"{ref_column_letter}:{ref_column_letter}"])
            all_column_values = ref_data.get("valueRanges", [{}])[0].get("values", [])
            total_rows = len(all_column_values)

            # 计算新插入数据的范围
            inserted_rows = dedup_result.get("inserted_rows", 0)
            new_data_start_row = total_rows - inserted_rows + 1
            new_data_end_row = total_rows

            # 读取基准列的新插入数据部分
            merge_column_letter = self.number_to_excel_column(merge_column_index + 1)
            base_column_range = f"{merge_column_letter}{new_data_start_row}:{merge_column_letter}{new_data_end_row}"
            base_data = self.client.read_multiple_ranges(spreadsheet_token, sheet_id, [base_column_range])

            base_values = base_data.get("valueRanges", [{}])[0].get("values", [])
            new_data_column_values = [row[0] if row else "" for row in base_values]

            # 分析合并范围 - 需要将列值转换为行数据格式
            data_rows_for_merge = [[value] for value in new_data_column_values]
            merge_ranges = self.analyze_merge_ranges(data_rows_for_merge, 0)
            log(f"[DEBUG] 新插入数据的合并范围: {merge_ranges}")

            # 执行合并操作
            for merge_group in merge_ranges:
                start_row = merge_group['start_row']
                end_row = merge_group['end_row']

                if end_row > start_row:
                    abs_start_row = new_data_start_row + start_row
                    abs_end_row = new_data_start_row + end_row

                    for col_index in merge_column_indices:
                        col_letter = self.number_to_excel_column(col_index + 1)
                        range_str = f"{col_letter}{abs_start_row}:{col_letter}{abs_end_row}"

                        try:
                            self.client.merge_cells(spreadsheet_token, sheet_id, "MERGE_ALL", range_str)
                            merge_count += 1
                        except Exception:
                            pass

        except Exception:
            pass

        # 处理图片插入
        log(f"[DEBUG] 开始处理图片插入，image_column: {image_column}")
        image_result = {"image_count": 0, "message": "未指定图片列"}
        if image_column:
            log(f"[DEBUG] 图片列已指定: {image_column}，开始调用 _insert_images_for_column_with_merge_info")
            try:
                # 传递合并范围信息，避免重新分析
                image_result = self._insert_images_for_column_with_merge_info(
                    spreadsheet_token, sheet_id, data_list, image_column,
                    dedup_result, header_row, reference_column, locals().get('merge_ranges', []), locals().get('new_data_start_row', 0)
                )
                log(f"[DEBUG] _insert_images_for_column_with_merge_info 执行完成，结果: {image_result}")
            except Exception as e:
                log(f"[DEBUG] 图片插入失败: {str(e)}")
                import traceback
                log(f"[DEBUG] 错误堆栈: {traceback.format_exc()}")
                image_result = {"image_count": 0, "message": f"图片插入失败: {str(e)}"}
        else:
            log(f"[DEBUG] 未指定图片列，跳过图片插入")

        log(f"[DEBUG] 最终图片插入结果: {image_result}")

        return {
            "status"      : "success",
            "message"     : f"{dedup_result.get('message', '')}，成功合并 {merge_count} 个单元格范围，{image_result.get('message', '')}",
            "dedup_result": dedup_result,
            "merge_result": {
                "merge_count": merge_count,
                "message"    : f"成功合并 {merge_count} 个单元格范围"
            },
            "image_result": image_result
        }

    def _get_merge_ranges_for_image_insertion(self, data_list: list, headers: list):
        """
        获取合并范围信息，用于图片插入时的判断
        """
        try:
            # 这里使用现有的合并逻辑，但主要是为了获取合并信息
            # 假设我们使用setup_shein_return_spreadsheet中定义的合并列信息
            merge_columns = [
                '退货单号', '签收状态', '店铺信息', '店长', '退货类型', '退货原因',
                'SKC图片', 'SKC信息', '包裹名', '包裹号', '退货计划单号',
                '订单号', '发货单', '退货出库时间', '退回方式', '快递名称',
                '运单号', '退货地址', '商家联系人', '商家手机号', '入库问题图片地址'
            ]

            # 使用退货单号作为基准列来分析合并范围
            merge_column = '退货单号'

            try:
                merge_column_index = headers.index(merge_column)
                data_rows = data_list[1:]  # 排除表头
                return self.analyze_merge_ranges(data_rows, merge_column_index)
            except ValueError:
                log(f"[DEBUG] 未找到基准列 '{merge_column}'，返回空合并范围")
                return []
        except Exception as e:
            log(f"[DEBUG] 获取合并范围信息失败: {str(e)}")
            return []

    def _insert_images_for_empty_sheet(self, spreadsheet_token: str, sheet_id: str, data_list: list, image_column: str):
        """
        为空表格插入的数据处理图片插入，考虑合并单元格情况
        """
        log(f"[DEBUG] _insert_images_for_empty_sheet 开始执行")

        if not data_list or len(data_list) < 2:
            return {"image_count": 0, "message": "数据不足，无法插入图片"}

        headers = data_list[0]
        data_rows = data_list[1:]

        # 找到图片列的索引
        try:
            image_column_index = headers.index(image_column)
            image_column_letter = self.number_to_excel_column(image_column_index + 1)
            log(f"[DEBUG] 图片列 '{image_column}' 索引: {image_column_index}, 列字母: {image_column_letter}")
        except ValueError:
            log(f"[DEBUG] 未找到图片列 '{image_column}'")
            return {"image_count": 0, "message": f"未找到图片列 '{image_column}'"}

        # 分析需要插入图片的行（只在合并组的第一行插入）
        merge_ranges = self._get_merge_ranges_for_image_insertion(data_list, headers)

        image_count = 0
        processed_merge_groups = set()  # 记录已处理的合并组

        for row_index, row in enumerate(data_rows):
            if len(row) > image_column_index and row[image_column_index]:
                image_url = str(row[image_column_index]).strip()
                if image_url and image_url.startswith('http'):
                    # 检查当前行是否在合并组中，且是否为合并组的第一行
                    should_insert = True
                    current_row_number = row_index + 2  # 表格行号（第1行是表头）

                    for merge_group in merge_ranges:
                        merge_start = merge_group['start_row'] + 2  # 转换为表格行号
                        merge_end = merge_group['end_row'] + 2

                        if merge_start <= current_row_number <= merge_end:
                            # 当前行在合并组中
                            if current_row_number == merge_start:
                                # 是合并组的第一行，可以插入
                                if merge_group['value'] not in processed_merge_groups:
                                    processed_merge_groups.add(merge_group['value'])
                                else:
                                    should_insert = False  # 同一个值的合并组已处理过
                            else:
                                # 不是合并组的第一行，跳过
                                should_insert = False
                            break

                    if should_insert:
                        try:
                            # 使用正确的范围格式：A3:A3
                            cell_range = f"{sheet_id}!{image_column_letter}{current_row_number}:{image_column_letter}{current_row_number}"
                            log(f"[DEBUG] 插入图片到单元格: {cell_range}, URL: {image_url}")
                            self.client.write_image(spreadsheet_token, cell_range, image_url)
                            image_count += 1
                        except Exception as e:
                            log(f"[DEBUG] 插入图片失败: {cell_range}, 错误: {str(e)}")
                    else:
                        log(f"[DEBUG] 跳过图片插入（合并单元格非首行）: 第{current_row_number}行")

        return {
            "image_count": image_count,
            "message"    : f"成功插入 {image_count} 张图片"
        }

    def _insert_images_for_column(self, spreadsheet_token: str, sheet_id: str, data_list: list,
            image_column: str, dedup_result: dict, header_row: int, reference_column: str):
        """
        为非空表格新插入的数据处理图片插入，考虑合并单元格情况
        """
        log(f"[DEBUG] _insert_images_for_column 开始执行")
        log(f"[DEBUG] 输入参数检查:")
        log(f"[DEBUG] - spreadsheet_token: {spreadsheet_token}")
        log(f"[DEBUG] - sheet_id: {sheet_id}")
        log(f"[DEBUG] - image_column: {image_column}")
        log(f"[DEBUG] - dedup_result: {dedup_result}")
        log(f"[DEBUG] - header_row: {header_row}")
        log(f"[DEBUG] - reference_column: {reference_column}")
        log(f"[DEBUG] - data_list 长度: {len(data_list) if data_list else 0}")

        # 如果没有插入新数据，直接返回
        inserted_rows = dedup_result.get("inserted_rows", 0)
        log(f"[DEBUG] 检查插入行数: {inserted_rows}")
        if inserted_rows == 0:
            log(f"[DEBUG] 无新数据插入，返回")
            return {"image_count": 0, "message": "无新数据插入，无需处理图片"}

        if not data_list or len(data_list) < 2:
            log(f"[DEBUG] 数据不足，返回")
            return {"image_count": 0, "message": "数据不足，无法插入图片"}

        headers = data_list[0]
        log(f"[DEBUG] 表头: {headers[:10]}...")  # 显示前10列

        # 找到图片列的索引
        try:
            image_column_index = headers.index(image_column)
            image_column_letter = self.number_to_excel_column(image_column_index + 1)
            log(f"[DEBUG] 图片列 '{image_column}' 索引: {image_column_index}, 列字母: {image_column_letter}")
        except ValueError:
            log(f"[DEBUG] 未找到图片列 '{image_column}'，可用列: {headers}")
            return {"image_count": 0, "message": f"未找到图片列 '{image_column}'"}

        try:
            # 使用参考列确定总行数和新插入数据的位置
            log(f"[DEBUG] 查找参考列 '{reference_column}'")
            ref_column_index = headers.index(reference_column)
            ref_column_letter = self.number_to_excel_column(ref_column_index + 1)
            log(f"[DEBUG] 参考列 '{reference_column}' 索引: {ref_column_index}, 列字母: {ref_column_letter}")

            log(f"[DEBUG] 读取参考列数据...")
            ref_data = self.client.read_multiple_ranges(spreadsheet_token, sheet_id, [f"{ref_column_letter}:{ref_column_letter}"])
            log(f"[DEBUG] 参考列原始数据: {ref_data}")
            all_column_values = ref_data.get("valueRanges", [{}])[0].get("values", [])
            total_rows = len(all_column_values)
            log(f"[DEBUG] 表格总行数: {total_rows}")

            # 计算新插入数据的范围
            new_data_start_row = total_rows - inserted_rows + 1
            new_data_end_row = total_rows

            log(f"[DEBUG] 计算得出新插入数据范围: 第{new_data_start_row}行到第{new_data_end_row}行")
            log(f"[DEBUG] 新插入行数: {inserted_rows}，总行数: {total_rows}")

            # 读取新插入数据的所有信息（包括基准列）用于分析合并情况
            merge_column = '退货单号'  # 基准列
            try:
                log(f"[DEBUG] 查找基准列 '{merge_column}'")
                merge_column_index = headers.index(merge_column)
                merge_column_letter = self.number_to_excel_column(merge_column_index + 1)
                log(f"[DEBUG] 基准列 '{merge_column}' 索引: {merge_column_index}, 列字母: {merge_column_letter}")

                # 读取基准列的新插入数据
                merge_column_range = f"{merge_column_letter}{new_data_start_row}:{merge_column_letter}{new_data_end_row}"
                log(f"[DEBUG] 读取基准列范围: {merge_column_range}")
                merge_data = self.client.read_multiple_ranges(spreadsheet_token, sheet_id, [merge_column_range])
                log(f"[DEBUG] 基准列原始数据: {merge_data}")
                merge_values = merge_data.get("valueRanges", [{}])[0].get("values", [])
                log(f"[DEBUG] 基准列值: {merge_values}")

                # 读取图片列的新插入数据部分
                image_column_range = f"{image_column_letter}{new_data_start_row}:{image_column_letter}{new_data_end_row}"
                log(f"[DEBUG] 读取图片列范围: {image_column_range}")
                image_data = self.client.read_multiple_ranges(spreadsheet_token, sheet_id, [image_column_range])
                log(f"[DEBUG] 图片列原始数据: {image_data}")
                image_values = image_data.get("valueRanges", [{}])[0].get("values", [])
                log(f"[DEBUG] 图片列值: {image_values}")

                # 分析合并范围
                log(f"[DEBUG] 开始分析合并范围...")
                merge_input_data = [[row[0]] if row else [""] for row in merge_values]
                log(f"[DEBUG] 合并分析输入数据: {merge_input_data}")
                merge_ranges = self.analyze_merge_ranges(merge_input_data, 0)
                log(f"[DEBUG] 分析得到的合并范围: {merge_ranges}")

                image_count = 0
                processed_merge_groups = set()  # 记录已处理的合并组值

                for row_index, image_row in enumerate(image_values):
                    if image_row and len(image_row) > 0:
                        image_url = str(image_row[0]).strip()
                        if image_url and image_url.startswith('http'):
                            # 检查当前行是否在合并组中，且是否为合并组的第一行
                            should_insert = True
                            current_absolute_row = new_data_start_row + row_index

                            # 获取当前行对应的基准列值
                            if row_index < len(merge_values) and merge_values[row_index]:
                                current_merge_value = str(merge_values[row_index][0]).strip()
                            else:
                                current_merge_value = ""

                            for merge_group in merge_ranges:
                                merge_start_in_new_data = merge_group['start_row']
                                merge_end_in_new_data = merge_group['end_row']

                                if merge_start_in_new_data <= row_index <= merge_end_in_new_data:
                                    # 当前行在合并组中
                                    merge_group_key = f"{merge_group['value']}_{merge_start_in_new_data}"

                                    if row_index == merge_start_in_new_data:
                                        # 是合并组的第一行，可以插入
                                        if merge_group_key not in processed_merge_groups:
                                            processed_merge_groups.add(merge_group_key)
                                        else:
                                            should_insert = False  # 同一个合并组已处理过
                                    else:
                                        # 不是合并组的第一行，跳过
                                        should_insert = False
                                    break

                            if should_insert:
                                try:
                                    # 使用正确的范围格式：A3:A3
                                    cell_range = f"{sheet_id}!{image_column_letter}{current_absolute_row}:{image_column_letter}{current_absolute_row}"
                                    log(f"[DEBUG] 插入图片到单元格: {cell_range}, URL: {image_url}")
                                    self.client.write_image(spreadsheet_token, cell_range, image_url)
                                    image_count += 1
                                except Exception as e:
                                    log(f"[DEBUG] 插入图片失败: {cell_range}, 错误: {str(e)}")
                            else:
                                log(f"[DEBUG] 跳过图片插入（合并单元格非首行）: 第{current_absolute_row}行")

                return {
                    "image_count": image_count,
                    "message"    : f"成功插入 {image_count} 张图片"
                }

            except ValueError:
                log(f"[DEBUG] 未找到基准列 '{merge_column}'，按普通方式处理图片插入")
                # 回退到简单处理方式
                image_column_range = f"{image_column_letter}{new_data_start_row}:{image_column_letter}{new_data_end_row}"
                image_data = self.client.read_multiple_ranges(spreadsheet_token, sheet_id, [image_column_range])
                image_values = image_data.get("valueRanges", [{}])[0].get("values", [])

                image_count = 0
                for row_index, row in enumerate(image_values):
                    if row and len(row) > 0:
                        image_url = str(row[0]).strip()
                        if image_url and image_url.startswith('http'):
                            try:
                                current_absolute_row = new_data_start_row + row_index
                                cell_range = f"{sheet_id}!{image_column_letter}{current_absolute_row}:{image_column_letter}{current_absolute_row}"
                                log(f"[DEBUG] 插入图片到单元格: {cell_range}, URL: {image_url}")
                                self.client.write_image(spreadsheet_token, cell_range, image_url)
                                image_count += 1
                            except Exception as e:
                                log(f"[DEBUG] 插入图片失败: {cell_range}, 错误: {str(e)}")

                return {
                    "image_count": image_count,
                    "message"    : f"成功插入 {image_count} 张图片"
                }

        except Exception as e:
            log(f"[DEBUG] 处理图片插入时出错: {str(e)}")
            return {"image_count": 0, "message": f"处理图片插入时出错: {str(e)}"}

    def _insert_images_for_column_with_merge_info(self, spreadsheet_token: str, sheet_id: str, data_list: list,
            image_column: str, dedup_result: dict, header_row: int,
            reference_column: str, merge_ranges: list, new_data_start_row: int):
        """
        使用已有的合并范围信息为新插入的数据处理图片插入
        """
        log(f"[DEBUG] _insert_images_for_column_with_merge_info 开始执行")
        log(f"[DEBUG] 接收到的合并范围: {merge_ranges}")
        log(f"[DEBUG] 新数据起始行: {new_data_start_row}")

        # 如果没有插入新数据，直接返回
        inserted_rows = dedup_result.get("inserted_rows", 0)
        if inserted_rows == 0:
            log(f"[DEBUG] 无新数据插入，返回")
            return {"image_count": 0, "message": "无新数据插入，无需处理图片"}

        if not data_list or len(data_list) < 2:
            log(f"[DEBUG] 数据不足，返回")
            return {"image_count": 0, "message": "数据不足，无法插入图片"}

        headers = data_list[0]
        data_rows = data_list[1:]

        # 找到图片列的索引
        try:
            image_column_index = headers.index(image_column)
            image_column_letter = self.number_to_excel_column(image_column_index + 1)
            log(f"[DEBUG] 图片列 '{image_column}' 索引: {image_column_index}, 列字母: {image_column_letter}")
        except ValueError:
            log(f"[DEBUG] 未找到图片列 '{image_column}'")
            return {"image_count": 0, "message": f"未找到图片列 '{image_column}'"}

        # 获取过滤后的数据（新插入的数据）
        # 不能重新执行去重逻辑，因为数据已经插入到表格中了
        # 应该直接从表格中读取新插入的数据
        log(f"[DEBUG] 开始处理图片插入，新插入行数: {inserted_rows}")

        # 直接从表格中读取新插入的图片列数据
        try:
            # 使用参考列确定总行数和新插入数据的位置
            ref_column_index = headers.index(reference_column)
            ref_column_letter = self.number_to_excel_column(ref_column_index + 1)

            ref_data = self.client.read_multiple_ranges(spreadsheet_token, sheet_id, [f"{ref_column_letter}:{ref_column_letter}"])
            all_column_values = ref_data.get("valueRanges", [{}])[0].get("values", [])
            total_rows = len(all_column_values)

            # 计算新插入数据的范围
            actual_new_data_start_row = total_rows - inserted_rows + 1
            actual_new_data_end_row = total_rows

            log(f"[DEBUG] 从表格读取新插入数据范围: 第{actual_new_data_start_row}行到第{actual_new_data_end_row}行")

            # 读取图片列的新插入数据部分
            image_column_range = f"{image_column_letter}{actual_new_data_start_row}:{image_column_letter}{actual_new_data_end_row}"
            image_data = self.client.read_multiple_ranges(spreadsheet_token, sheet_id, [image_column_range])
            image_values = image_data.get("valueRanges", [{}])[0].get("values", [])

            log(f"[DEBUG] 从表格读取的图片列数据: {image_values}")

            # 构建图片URL映射，解析JSON格式的URL数据
            image_urls_for_new_rows = []
            for row in image_values:
                if row and len(row) > 0:
                    raw_url_data = str(row[0]).strip()
                    # 解析飞书表格中的URL数据格式
                    parsed_url = self._extract_url_from_feishu_data(raw_url_data)
                    image_urls_for_new_rows.append(parsed_url)
                    log(f"[DEBUG] 解析URL: 原始='{raw_url_data[:100]}...' -> 解析后='{parsed_url}'")
                else:
                    image_urls_for_new_rows.append("")

            log(f"[DEBUG] 实际插入行的图片URL: {image_urls_for_new_rows}")

            # 使用传入的合并范围信息（它们已经是正确的）
            log(f"[DEBUG] 使用传入的合并范围: {merge_ranges}")

        except Exception as e:
            log(f"[DEBUG] 从表格读取图片数据失败: {str(e)}")
            return {"image_count": 0, "message": f"读取图片数据失败: {str(e)}"}

        # 使用合并范围信息决定在哪些行插入图片
        image_count = 0
        processed_merge_groups = set()

        for row_index in range(len(image_urls_for_new_rows)):
            image_url = image_urls_for_new_rows[row_index]
            if not image_url or not image_url.startswith('http'):
                log(f"[DEBUG] 第{row_index}行无有效图片URL: '{image_url}'")
                continue

            should_insert = True
            current_absolute_row = actual_new_data_start_row + row_index  # 使用实际的起始行号

            log(f"[DEBUG] 处理第{row_index}行，绝对行号: {current_absolute_row}, URL: {image_url}")

            # 检查当前行是否在合并组中
            for merge_group in merge_ranges:
                merge_start_in_new_data = merge_group['start_row']
                merge_end_in_new_data = merge_group['end_row']

                log(f"[DEBUG] 检查合并组: {merge_group}, 当前行索引: {row_index}")

                if merge_start_in_new_data <= row_index <= merge_end_in_new_data:
                    # 当前行在合并组中
                    merge_group_key = f"{merge_group['value']}_{merge_start_in_new_data}"

                    if row_index == merge_start_in_new_data:
                        # 是合并组的第一行，可以插入
                        if merge_group_key not in processed_merge_groups:
                            processed_merge_groups.add(merge_group_key)
                            log(f"[DEBUG] 合并组第一行，允许插入: 行{current_absolute_row}, 组{merge_group_key}")
                        else:
                            should_insert = False
                            log(f"[DEBUG] 合并组已处理过，跳过: 行{current_absolute_row}, 组{merge_group_key}")
                    else:
                        # 不是合并组的第一行，跳过
                        should_insert = False
                        log(f"[DEBUG] 合并组非首行，跳过: 行{current_absolute_row}")
                    break
            else:
                # 没有在任何合并组中，可以插入
                log(f"[DEBUG] 独立行，允许插入: 行{current_absolute_row}")

            if should_insert:
                try:
                    # 使用正确的范围格式：A3:A3
                    cell_range = f"{sheet_id}!{image_column_letter}{current_absolute_row}:{image_column_letter}{current_absolute_row}"
                    log(f"[DEBUG] 插入图片到单元格: {cell_range}, URL: {image_url}")
                    self.client.write_image(spreadsheet_token, cell_range, image_url)
                    image_count += 1
                except Exception as e:
                    log(f"[DEBUG] 插入图片失败: {cell_range}, 错误: {str(e)}")
            else:
                log(f"[DEBUG] 跳过图片插入: 行{current_absolute_row}")

        log(f"[DEBUG] 图片插入完成，成功插入 {image_count} 张图片")
        return {
            "image_count": image_count,
            "message"    : f"成功插入 {image_count} 张图片"
        }

    def _extract_url_from_feishu_data(self, raw_data: str):
        """
        从飞书表格的URL数据格式中提取真正的URL
        """
        try:
            # 处理None和空字符串
            if not raw_data or raw_data == 'None':
                return ""

            # 尝试解析JSON格式的数据
            import json
            if raw_data.startswith('[') and raw_data.endswith(']'):
                parsed_data = json.loads(raw_data)
                if isinstance(parsed_data, list) and len(parsed_data) > 0:
                    first_item = parsed_data[0]
                    if isinstance(first_item, dict):
                        # 优先使用link字段，其次使用text字段
                        url = first_item.get('link') or first_item.get('text', '')
                        if url and url.startswith('http'):
                            return url

            # 如果不是JSON格式，检查是否直接是URL
            if raw_data.startswith('http'):
                return raw_data

            return ""
        except Exception as e:
            log(f"[DEBUG] 解析URL数据失败: {str(e)}, 原始数据: {raw_data}")
            # 如果解析失败，尝试直接检查是否包含URL
            if 'http' in raw_data:
                import re
                # 使用正则表达式提取URL
                url_pattern = r'https?://[^\s\'"]*'
                matches = re.findall(url_pattern, raw_data)
                if matches:
                    return matches[0]
            return ""

    def setup_shein_return_spreadsheet(self, monthly_data: list, sheet_title: str):
        """
        希音退货列表业务逻辑 - 按月份分组存储数据
        
        Args:
            monthly_data: 指定月份的数据列表，包含表头和数据行
            sheet_title: 工作表标题（如：202507, 202508）
        """
        log(f"[DEBUG] setup_shein_return_spreadsheet 开始执行")
        log(f"[DEBUG] sheet_title: {sheet_title}")
        log(f"[DEBUG] monthly_data 长度: {len(monthly_data) if monthly_data else 0}")

        # 获取根目录
        root_folder_token = self.client.get_root_folder_meta().get('token')
        all_files = self.get_all_folder_files(folder_token=root_folder_token)

        # 检查是否存在"希音退货列表"表格
        shein_return_spreadsheet_token = None
        shein_return_spreadsheet_url = None
        for file in all_files:
            if file.get("name") == "希音退货列表" and file.get("type") == "sheet":
                shein_return_spreadsheet_token = file.get("token")
                shein_return_spreadsheet_url = file.get("url")
                break

        # 如果不存在则创建
        if not shein_return_spreadsheet_token:
            create_result = self.client.create_spreadsheet(title="希音退货列表", folder_token=root_folder_token)
            shein_return_spreadsheet_token = create_result.get('spreadsheet', {}).get('spreadsheet_token')
            shein_return_spreadsheet_url = create_result.get('spreadsheet', {}).get('url')

        # 获取表格中的所有工作表
        sheets_result = self.client.query_sheets(shein_return_spreadsheet_token)
        sheets = sheets_result.get('sheets', [])

        # 检查是否存在指定的工作表
        target_sheet_title = sheet_title
        target_sheet_id = None

        for sheet in sheets:
            if sheet.get('title') == target_sheet_title:
                target_sheet_id = sheet.get('sheet_id')
                break

        # 如果不存在则创建
        if not target_sheet_id:
            add_sheet_result = self.client.add_sheet(
                spreadsheet_token=shein_return_spreadsheet_token,
                title=target_sheet_title,
                index=0
            )
            replies = add_sheet_result.get('replies', [])
            if replies:
                target_sheet_id = replies[0].get('addSheet', {}).get('properties', {}).get('sheetId')

        # 处理月份数据并写入表格
        try:
            if not monthly_data or len(monthly_data) < 2:
                return {
                    "error"  : "数据不足",
                    "message": f"月份 {sheet_title} 的数据不足，无法处理"
                }

            merge_columns = [
                '退货单号', '签收状态', '店铺信息', '店长', '退货类型', '退货原因',
                'SKC图片', 'SKC信息', '包裹名', '包裹号', '退货计划单号',
                '订单号', '发货单', '退货出库时间', '退回方式', '快递名称',
                '运单号', '退货地址', '商家联系人', '商家手机号', '入库问题图片地址'
            ]

            merge_result = self.write_data_and_merge_by_column_with_deduplication(
                spreadsheet_token=shein_return_spreadsheet_token,
                sheet_id=target_sheet_id,
                data_list=monthly_data,
                dedup_column='退货单号',
                merge_column='退货单号',
                merge_columns=merge_columns,
                reference_column='平台SKU',
                image_column='SKC图片'
            )

            # 设置表格权限
            self.client.batch_create_permission_members(
                token=shein_return_spreadsheet_token,
                type="sheet",
                members=[
                    {
                        "member_type": "openchat",
                        "member_id"  : "oc_c27bcdef75057de2ab720189d34da477",
                        "perm"       : "edit",
                    },
                    {
                        "member_type": "openchat",
                        "member_id"  : "oc_679fabef0a4ac753a4aad58a3777d42f",
                        "perm"       : "edit",
                    },
                    {
                        "member_type": "openchat",
                        "member_id"  : "oc_05f89743bce14feb5b2cdc76401b3066",
                        "perm"       : "edit",
                    },
                ]
            )

            # 设置标题
            self.set_header_row_style(
                spreadsheet_token=shein_return_spreadsheet_token,
                sheet_id=target_sheet_id,
                header_row=1,
                column_count=27
            )

            # 设置对齐
            self.set_column_to_align(
                spreadsheet_token=shein_return_spreadsheet_token,
                sheet_id=target_sheet_id,
                column_names_to_left=['D', 'G', 'I', 'J', 'K', 'M', 'N', 'X', 'Y', 'AA'],
                column_names_to_center=['B', 'C', 'E', 'F', 'L', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'Z'],
                column_names_to_right=['O'],
            )

            # 冻结首行
            self.client.update_sheet_properties(spreadsheet_token=shein_return_spreadsheet_token, properties={
                "sheetId"       : target_sheet_id,
                "frozenRowCount": 1
            })

            log(f"[DEBUG] 月份 {sheet_title} 数据处理完成")

            return {
                'spreadsheet_token': shein_return_spreadsheet_token,
                'sheet_id'         : target_sheet_id,
                'sheet_title'      : target_sheet_title,
                'spreadsheet_url'  : shein_return_spreadsheet_url,
                'merge_result'     : merge_result
            }

        except Exception as e:
            log(f"[DEBUG] 处理月份 {sheet_title} 数据失败: {str(e)}")
            return {"error": f"处理失败: {str(e)}"}

    def process_shein_return_data_by_month(self, json_file_path: str = 'data4.json'):
        """
        按月份分组处理希音退货数据
        
        Args:
            json_file_path: JSON数据文件路径
            
        Returns:
            dict: 处理结果，包含各月份的处理状态
        """
        log(f"[DEBUG] process_shein_return_data_by_month 开始执行")
        log(f"[DEBUG] 读取文件: {json_file_path}")

        try:
            # 读取JSON数据
            with open(json_file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            if not json_data or len(json_data) < 2:
                return {"error": "数据文件为空或数据不足"}

            headers = json_data[0]
            data_rows = json_data[1:]

            # 找到退货出库时间列的索引
            try:
                time_column_index = headers.index('退货出库时间')
                log(f"[DEBUG] 找到退货出库时间列索引: {time_column_index}")
            except ValueError:
                return {"error": "未找到'退货出库时间'列"}

            # 按月份分组数据
            monthly_data = {}

            for row in data_rows:
                if len(row) > time_column_index and row[time_column_index]:
                    # 解析日期时间，格式：2025-08-14 10:50:37
                    date_str = str(row[time_column_index]).strip()
                    try:
                        # 提取年月部分
                        date_part = date_str.split(' ')[0]  # 获取日期部分
                        year_month = date_part.replace('-', '')[:6]  # 转换为YYYYMM格式

                        if year_month not in monthly_data:
                            monthly_data[year_month] = []

                        monthly_data[year_month].append(row)

                    except Exception as e:
                        log(f"[DEBUG] 解析日期失败: {date_str}, 错误: {str(e)}")
                        continue

            log(f"[DEBUG] 数据按月份分组完成，共 {len(monthly_data)} 个月份")
            for month, rows in monthly_data.items():
                log(f"[DEBUG] 月份 {month}: {len(rows)} 行数据")

            # 为每个月份处理数据
            results = {}

            for month, rows in monthly_data.items():
                log(f"[DEBUG] 开始处理月份: {month}")

                # 构建该月份的完整数据（包含表头）
                month_data = [headers] + rows

                log(month, json.dumps(month_data, ensure_ascii=False))
                # 调用原有的函数处理该月份数据
                result = self.setup_shein_return_spreadsheet(month_data, month)
                results[month] = result

                log(f"[DEBUG] 月份 {month} 处理完成")

            result = {
                "status"         : "success",
                "message"        : f"成功处理 {len(results)} 个月份的数据",
                "results"        : results,
                "monthly_summary": {month: len(rows) for month, rows in monthly_data.items()}
            }

            if result.get('status') == 'success':
                print(f"✅ {result['message']}")
                print("\n📊 月份数据统计:")
                for month, count in result['monthly_summary'].items():
                    print(f"  - {month[:4]}年{month[4:]}月: {count} 行数据")

                print("\n📋 处理结果详情:")
                for month, month_result in result['results'].items():
                    if 'error' in month_result:
                        print(f"  ❌ {month}: {month_result['error']}")
                    else:
                        merge_info = month_result.get('merge_result', {})
                        print(f"  ✅ {month}: {merge_info.get('message', '处理完成')}")
            else:
                print(f"❌ 处理失败: {result.get('error')}")

            print("\n" + "=" * 50 + "\n")

        except Exception as e:
            log(f"[DEBUG] process_shein_return_data_by_month 执行失败: {str(e)}")
            return {"error": f"处理失败: {str(e)}"}

    def set_header_row_style(self, spreadsheet_token: str, sheet_id: str, header_row: int = 1,
            end_column: str = None, column_count: int = None):
        """
        设置表格标题行样式
        类似xlwings的样式设置：背景色、字体颜色、加粗、居中对齐
        
        Args:
            spreadsheet_token: 表格token
            sheet_id: 工作表ID
            header_row: 标题行号，默认第1行
            end_column: 结束列名（如'Z'），与column_count二选一
            column_count: 列数，与end_column二选一
        """
        try:
            # 确定范围
            if end_column:
                range_str = f"A{header_row}:{end_column}{header_row}"
            elif column_count:
                end_col = self.number_to_excel_column(column_count)
                range_str = f"A{header_row}:{end_col}{header_row}"
            else:
                # 默认设置前26列（A-Z）
                range_str = f"A{header_row}:Z{header_row}"

                # 定义样式 - 根据飞书官方文档格式
            style_data = {
                "ranges": [f"{sheet_id}!{range_str}"],  # 使用ranges数组
                "style" : {
                    # 背景色：RGB(68, 114, 196) 转换为十六进制
                    "backColor": "#4472C4",
                    # 字体颜色：白色
                    "foreColor": "#FFFFFF",
                    # 字体设置
                    "font"     : {
                        "bold"    : True,
                        "fontSize": "11pt/1.5"  # 字体大小格式
                    },
                    "hAlign"   : 1,
                    "vAlign"   : 1
                }
            }

            # 调用批量设置样式API - 修正参数传递
            result = self.client.batch_set_cell_style(spreadsheet_token, [style_data])
            log(f"[DEBUG] 成功设置标题行样式: {range_str}")
            return {
                "status" : "success",
                "message": f"成功设置标题行样式: {range_str}",
                "result" : result
            }

        except Exception as e:
            log(f"[DEBUG] 设置标题行样式失败: {str(e)}")
            return {
                "status" : "error",
                "message": f"设置标题行样式失败: {str(e)}"
            }

    def set_column_style(self, spreadsheet_token: str, sheet_id: str, column_name: str,
            start_row: int = 1, end_row: int = None, style_config: dict = None):
        """
        设置指定列的样式（支持整列或指定行范围）
        
        Args:
            spreadsheet_token: 表格token
            sheet_id: 工作表ID  
            column_name: 列名（如'A', 'B'等）
            start_row: 开始行号，默认第1行
            end_row: 结束行号，None表示整列
            style_config: 自定义样式配置
        """
        try:
            # 构建范围
            if end_row:
                range_str = f"{column_name}{start_row}:{column_name}{end_row}"
            else:
                range_str = f"{column_name}:{column_name}"

                # 默认样式配置（水平居中和垂直居中）
            default_style = {
                "hAlign": 1,  # 水平居中
                "vAlign": 1  # 垂直居中
            }

            # 合并自定义样式
            final_style = style_config if style_config else default_style

            style_data = {
                "ranges": [f"{sheet_id}!{range_str}"],  # 使用ranges数组
                "style" : final_style
            }

            result = self.client.batch_set_cell_style(spreadsheet_token, [style_data])
            log(f"[DEBUG] 成功设置列样式: {range_str}")
            return {
                "status" : "success",
                "message": f"成功设置列样式: {range_str}",
                "result" : result
            }

        except Exception as e:
            log(f"[DEBUG] 设置列样式失败: {str(e)}")
            return {
                "status" : "error",
                "message": f"设置列样式失败: {str(e)}"
            }

    def set_column_to_align(self, spreadsheet_token: str, sheet_id: str, column_names_to_left: list, column_names_to_center: list, column_names_to_right: list):
        try:
            style_data_left = {
                "ranges": [f"{sheet_id}!{column_name}:{column_name}" for column_name in column_names_to_left],
                "style" : {
                    # 字体设置
                    "font"  : {
                        "bold"    : False,
                        "fontSize": "10pt/1.5"
                    },
                    "hAlign": 0,
                    "vAlign": 1
                }
            }
            style_data_center = {
                "ranges": [f"{sheet_id}!{column_name}:{column_name}" for column_name in column_names_to_center],
                "style" : {
                    # 字体设置
                    "font"  : {
                        "bold"    : False,
                        "fontSize": "10pt/1.5"
                    },
                    "hAlign": 1,
                    "vAlign": 1
                }
            }
            style_data_right = {
                "ranges": [f"{sheet_id}!{column_name}:{column_name}" for column_name in column_names_to_right],
                "style" : {
                    # 字体设置
                    "font"  : {
                        "bold"    : False,
                        "fontSize": "10pt/1.5"
                    },
                    "hAlign": 2,
                    "vAlign": 1
                }
            }
            result = self.client.batch_set_cell_style(spreadsheet_token, [style_data_left, style_data_center, style_data_right])
        except Exception as e:
            log(e)
