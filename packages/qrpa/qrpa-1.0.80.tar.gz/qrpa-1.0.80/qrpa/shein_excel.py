from .fun_excel import *
from .fun_base import *
from .fun_file import read_dict_from_file, read_dict_from_file_ex, write_dict_to_file, write_dict_to_file_ex, delete_file
from .time_utils import TimeUtils
from .wxwork import WxWorkBot
from .shein_daily_report_model import SheinStoreSalesDetailManager, SheinStoreSalesDetail

import pandas as pd
import numpy as np

class SheinExcel:

    def __init__(self, config, bridge=None):
        self.config = config
        self.bridge = bridge
        pass

    def write_week_ntb(self):
        excel_path = create_file_path(self.config.excel_week_report)

        cache_file = f'{self.config.auto_dir}/shein/dict/new_product_to_bak_{TimeUtils.today_date()}.json'
        dict = read_dict_from_file(cache_file)
        # dict_store = read_dict_from_file(config.dict_store_cache)

        summary_excel_data = []
        header = []
        dict_store_bak_stat = {}
        for store_username, excel_data in dict.items():
            # store_name = dict_store.get(store_username)
            if dict_store_bak_stat.get(store_username) is None:
                dict_store_bak_stat[store_username] = [0, 0]
            for item in excel_data[1:]:
                dict_store_bak_stat[store_username][0] += 1
                if int(item[6]) == 1:
                    dict_store_bak_stat[store_username][1] += 1
            header = excel_data[0]
            summary_excel_data += excel_data[1:]
        summary_excel_data = [header] + summary_excel_data
        log(summary_excel_data)
        sheet_name = '新品转备货款明细'

        # write_data(excel_path, sheet_name, summary_excel_data)
        # self.format_week_ntb(excel_path, sheet_name)

        batch_excel_operations(excel_path, [
            (sheet_name, 'write', summary_excel_data),
            (sheet_name, 'format', self.format_week_ntb),
        ])

        dict_key = f'{self.config.auto_dir}/shein/dict/dict_store_bak_stat_{TimeUtils.today_date()}.json'
        write_dict_to_file(dict_key, dict_store_bak_stat)

    def format_week_ntb(self, sheet):
        beautify_title(sheet)
        format_to_date(sheet, ['统计日期'])
        format_to_percent(sheet, ['占比'])
        colorize_by_field(sheet, 'SPU')
        column_to_left(sheet, ['商品信息', '第4周SKC点击率/SKC转化率', '第4周SKC销量/SKC曝光'])
        autofit_column(sheet, ['店铺名称', '商品信息', '第4周SKC点击率/SKC转化率', '第4周SKC销量/SKC曝光'])
        add_borders(sheet)
        InsertImageV2(sheet, ['SKC图片'], 'shein', 120)

    def dealFundsExcelFormat(self, sheet):
        col_a = find_column_by_data(sheet, 1, '店铺名称')
        col_b = find_column_by_data(sheet, 1, '在途商品金额')
        col_c = find_column_by_data(sheet, 1, '在仓商品金额')
        col_d = find_column_by_data(sheet, 1, '待结算金额')
        col_e = find_column_by_data(sheet, 1, '可提现金额')
        col_f = find_column_by_data(sheet, 1, '汇总')
        col_g = find_column_by_data(sheet, 1, '导出时间')
        col_h = find_column_by_data(sheet, 1, '销售出库金额')

        sheet.range(f'{col_a}:{col_a}').column_width = 25
        sheet.range(f'{col_g}:{col_g}').number_format = 'yyyy-mm-dd hh:mm:ss'

        last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row
        sheet.range(f'{col_b}2').formula = f'=SUM({col_b}3:{col_b}{last_row})'
        sheet.range(f'{col_b}2').number_format = '¥#,##0.00'
        cell = sheet.range(f'{col_b}2')
        cell.api.Font.Color = 255  # RGB(255, 0, 0)，红色对应的颜色代码
        cell.api.Font.Bold = True

        sheet.range(f'{col_c}2').formula = f'=SUM({col_c}3:{col_c}{last_row})'
        sheet.range(f'{col_c}2').number_format = '¥#,##0.00'
        cell = sheet.range(f'{col_c}2')
        cell.api.Font.Color = 255  # RGB(255, 0, 0)，红色对应的颜色代码
        cell.api.Font.Bold = True

        sheet.range(f'{col_d}2').formula = f'=SUM({col_d}3:{col_d}{last_row})'
        sheet.range(f'{col_d}2').number_format = '¥#,##0.00'
        cell = sheet.range(f'{col_d}2')
        cell.api.Font.Color = 255  # RGB(255, 0, 0)，红色对应的颜色代码
        cell.api.Font.Bold = True

        sheet.range(f'{col_e}2').formula = f'=SUM({col_e}3:{col_e}{last_row})'
        sheet.range(f'{col_e}2').number_format = '¥#,##0.00'
        cell = sheet.range(f'{col_e}2')
        cell.api.Font.Color = 255  # RGB(255, 0, 0)，红色对应的颜色代码
        cell.api.Font.Bold = True

        sheet.range(f'{col_h}2').formula = f'=SUM({col_h}3:{col_h}{last_row})'
        sheet.range(f'{col_h}2').number_format = '¥#,##0.00'
        cell = sheet.range(f'{col_h}2')
        cell.api.Font.Color = 255  # RGB(255, 0, 0)，红色对应的颜色代码
        cell.api.Font.Bold = True

        # 遍历可用行
        used_range_row = sheet.range('A1').expand('down')
        for i, cell in enumerate(used_range_row):
            row = i + 1
            if row < 2:
                continue
            # 设置数字格式
            sheet.range(f'{col_b}{row}').number_format = '¥#,##0.00'
            sheet.range(f'{col_c}{row}').number_format = '¥#,##0.00'
            sheet.range(f'{col_d}{row}').number_format = '¥#,##0.00'
            sheet.range(f'{col_e}{row}').number_format = '¥#,##0.00'
            sheet.range(f'{col_f}{row}').formula = f'=SUM({col_b}{row}:{col_e}{row})'
            sheet.range(f'{col_f}{row}').number_format = '¥#,##0.00'
            sheet.range(f'{col_f}{row}').api.Font.Color = 255
            sheet.range(f'{col_f}{row}').api.Font.Bold = True

        add_borders(sheet)

    def write_week_finance_report(self):
        cache_file = f'{self.config.auto_dir}/shein/cache/stat_fund_lz_{TimeUtils.today_date()}.json'
        dict = read_dict_from_file(cache_file)
        dict_key = f'{self.config.auto_dir}/shein/dict/dict_store_bak_stat_{TimeUtils.today_date()}.json'
        dict_store_bak_stat = read_dict_from_file(dict_key)
        data = []
        for key, val in dict.items():
            data.append(val)
        log(data)
        for item in data:
            store_username = item[1]
            item[9] = dict_store_bak_stat[store_username][0]
            item[10] = dict_store_bak_stat[store_username][1]

        data.sort(key=lambda row: row[8], reverse=True)
        excel_path = create_file_path(self.config.excel_week_report)
        sheet_name = '按店铺汇总'
        data.insert(0, ['汇总', '', '', '', '', '', '', '', '', '', '', '', ''])
        data.insert(0, ['店铺名称', '店铺账号', '店长', '在途商品金额', '在仓商品金额', '待结算金额', '可提现金额', '汇总',
                        '销售出库金额', '新品上架数量', '成功转备货款', '成功率', '导出时间'])
        write_data(excel_path, sheet_name, data)
        app, wb, sheet = open_excel(excel_path, sheet_name)
        beautify_title(sheet)

        self.dealFundsExcelFormat(sheet)
        format_to_percent(sheet, ['成功率'], 0)
        add_formula_for_column(sheet, '成功率', '=IF(J2=0, 0, k2/J2)', 2)
        add_formula_for_column(sheet, '新品上架数量', "=COUNTIF('新品转备货款明细'!A:A, B3)", 3)
        add_formula_for_column(sheet, '成功转备货款', "=COUNTIFS('新品转备货款明细'!A:A, B3, '新品转备货款明细'!G:G, 1)", 3)
        add_sum_for_cell(sheet, ['新品上架数量', '成功转备货款'])
        column_to_right(sheet, ['金额', '汇总'])
        sheet.autofit()
        delete_sheet_if_exists(wb, 'Sheet1')
        wb.save()
        close_excel(app, wb)

        new_data = data
        new_data = aggregate_by_column(new_data, '店长')
        new_data_sorted = new_data[2:]
        new_data_sorted.sort(key=lambda row: row[8], reverse=True)

        sheet_name = '按店长汇总'
        write_data(excel_path, sheet_name, data[:2] + new_data_sorted)
        app, wb, sheet = open_excel(excel_path, sheet_name)
        add_borders(sheet)
        format_to_money(sheet, ['金额', '成本'])
        format_to_datetime(sheet, ['时间'])
        format_to_percent(sheet, ['成功率'], 0)
        add_formula_for_column(sheet, '成功率', '=IF(J2=0, 0, k2/J2)', 2)
        # 聚合的不能使用这种公式
        # add_formula_for_column(sheet, '新品上架数量',"=COUNTIF('新品转备货款明细'!A:A, B3)",3)
        # add_formula_for_column(sheet, '成功转备货款',"=COUNTIFS('新品转备货款明细'!A:A, B3, '新品转备货款明细'!G:G, 1)",3)
        add_sum_for_cell(sheet, ['在途商品金额', '在仓商品金额', '待结算金额', '可提现金额', '汇总', '销售出库金额',
                                 '新品上架数量', '成功转备货款'])
        clear_for_cell(sheet, ['店铺账号', '导出时间'])
        add_formula_for_column(sheet, '汇总', f'=SUM(D3:G3)', 3)
        set_title_style(sheet)
        column_to_right(sheet, ['金额', '汇总'])
        autofit_column(sheet, ['店铺名称', '店铺账号', '导出时间'])
        wb.save()
        close_excel(app, wb)
        WxWorkBot('b30aaa8d-1a1f-4378-841a-8b0f8295f2d9').send_file(excel_path)

    # 退货列表
    def write_return_list(self, erp, start_date, end_date):
        header = ['退货单号', '退货出库时间', '签收状态', '店铺信息', '店长', '退货类型', '退货原因', 'SKC图片', 'SKC信息', '商家SKU', '属性集', 'SKU退货数量', '平台SKU', 'ERP默认供货商', 'ERP成本', '包裹名', '包裹号', '退货计划单号', '订单号', '发货单', '退回方式', '快递名称', '运单号', '退货地址', '商家联系人', '商家手机号', '入库问题图片地址']
        excel_data = [header]

        dict_store = read_dict_from_file(self.config.shein_store_alias)

        cache_file = f'{self.config.auto_dir}/shein/cache/shein_return_order_list_{start_date}_{end_date}.json'
        dict = read_dict_from_file(cache_file)
        for store_username, shein_back_list in dict.items():
            for item in shein_back_list:

                store_name = dict_store.get(store_username)

                returnOrderId = item['id']
                cache_file = f'{self.config.auto_dir}/shein/cache/shein_return_order_box_detail_{returnOrderId}.json'
                return_detail = read_dict_from_file(cache_file)
                if len(return_detail) == 0:
                    continue

                returnOrderNo = item['returnOrderNo']
                returnOrderTypeName = item['returnOrderTypeName']
                returnOrderStatusName = item['returnOrderStatusName']
                returnReasonTypeName = item['returnReasonTypeName']
                returnReason = item['returnReason']
                waitReturnQuantity = item['waitReturnQuantity']
                skcReturnQuantity = item['returnQuantity']
                returnAmount = item['returnAmount']
                currencyCode = item['currencyCode']
                returnPlanNo = item['returnPlanNo']
                sellerOrderNo = item['sellerOrderNo']
                sellerDeliveryNo = item['sellerDeliveryNo']
                completeTime = item['completeTime']
                returnWayTypeName = item['returnWayTypeName']
                returnExpressCompanyName = item['returnExpressCompanyName']
                expressNoList = item['expressNoList']
                returnAddress = item['returnAddress']
                sellerContract = item['sellerContract']
                sellerContractPhone = item['sellerContractPhone']
                isSign = ['已报废', '已签收', '待签收'][item['isSign']]
                if item['returnScrapType'] == 1:
                    urls = item.get('qc_report_url', '-')
                else:
                    urls = '\n'.join(item['rejectPicUrlList'])

                for box_list in return_detail:
                    for package_list in box_list['boxList']:
                        package_name = package_list['packageName']
                        package_no = package_list['returnBoxNo']
                        for skc_item in package_list['goods']:
                            skc_img = skc_item['imgPath']
                            skc = skc_item['skc']
                            supplierCode = skc_item['supplierCode']
                            for sku_item in skc_item['details']:
                                platformSku = sku_item['platformSku']
                                supplierSku = sku_item['supplierSku']
                                suffixZh = sku_item['suffixZh']
                                returnQuantity = sku_item['returnQuantity']

                                store_info = f'{store_username}\n{store_name}\n处理类型: {returnOrderTypeName}\n退货状态: {returnOrderStatusName}'
                                skc_info = f'SKC: {skc}\n供方货号: {supplierCode}\n预计退货数量/执行退货数量: {waitReturnQuantity}/{skcReturnQuantity}\n预计退货货值: {returnAmount} {currencyCode}'

                                row_item = []
                                row_item.append(returnOrderNo)
                                row_item.append(completeTime)
                                row_item.append(isSign)
                                row_item.append(store_info)
                                row_item.append(self.config.shein_store_manager.get(str(store_username).lower()))
                                row_item.append(returnReasonTypeName)
                                row_item.append(returnReason)
                                row_item.append(skc_img)
                                row_item.append(skc_info)
                                row_item.append(supplierSku)
                                row_item.append(suffixZh)
                                row_item.append(returnQuantity)
                                row_item.append(platformSku)
                                row_item.append(self.bridge.get_sku_supplier(supplierSku, erp))
                                row_item.append(self.bridge.get_sku_cost(supplierSku, erp))
                                row_item.append(package_name)
                                row_item.append(package_no)
                                row_item.append(returnPlanNo)
                                row_item.append(sellerOrderNo)
                                row_item.append(sellerDeliveryNo)
                                row_item.append(returnWayTypeName)
                                row_item.append(returnExpressCompanyName)
                                row_item.append(expressNoList)
                                row_item.append(returnAddress)
                                row_item.append(sellerContract)
                                row_item.append(sellerContractPhone)
                                row_item.append(urls)

                                excel_data.append(row_item)

        cache_file_excel = f'{self.config.auto_dir}/shein/cache/shein_return_order_list_excel_{start_date}_{end_date}.json'
        write_dict_to_file(cache_file_excel, excel_data)

        # sheet_name = '希音退货列表'
        # batch_excel_operations(self.config.excel_return_list, [
        #     (sheet_name, 'write', excel_data, ['W', 'Z']),
        #     (sheet_name, 'format', self.format_return_list)
        # ])

        excel_data = [header]
        cache_file = f'{self.config.auto_dir}/shein/cache/shein_return_order_list_{TimeUtils.today_date()}.json'
        dict = read_dict_from_file(cache_file)
        for store_username, shein_back_list in dict.items():
            for item in shein_back_list:

                store_name = dict_store.get(store_username)

                returnOrderId = item['id']
                cache_file = f'{self.config.auto_dir}/shein/cache/shein_return_order_box_detail_{returnOrderId}.json'
                return_detail = read_dict_from_file(cache_file)
                if len(return_detail) == 0:
                    continue

                returnOrderNo = item['returnOrderNo']
                returnOrderTypeName = item['returnOrderTypeName']
                returnOrderStatusName = item['returnOrderStatusName']
                returnReasonTypeName = item['returnReasonTypeName']
                returnReason = item['returnReason']
                waitReturnQuantity = item['waitReturnQuantity']
                skcReturnQuantity = item['returnQuantity']
                returnAmount = item['returnAmount']
                currencyCode = item['currencyCode']
                returnPlanNo = item['returnPlanNo']
                sellerOrderNo = item['sellerOrderNo']
                sellerDeliveryNo = item['sellerDeliveryNo']
                completeTime = item['completeTime']
                returnWayTypeName = item['returnWayTypeName']
                returnExpressCompanyName = item['returnExpressCompanyName']
                expressNoList = item['expressNoList']
                returnAddress = item['returnAddress']
                sellerContract = item['sellerContract']
                sellerContractPhone = item['sellerContractPhone']
                isSign = ['已报废', '已签收', '待签收'][item['isSign']]
                if item['returnScrapType'] == 1:
                    urls = item.get('qc_report_url', '-')
                else:
                    urls = '\n'.join(item['rejectPicUrlList'])

                for box_list in return_detail:
                    for package_list in box_list['boxList']:
                        package_name = package_list['packageName']
                        package_no = package_list['returnBoxNo']
                        for skc_item in package_list['goods']:
                            skc_img = skc_item['imgPath']
                            skc = skc_item['skc']
                            supplierCode = skc_item['supplierCode']
                            for sku_item in skc_item['details']:
                                platformSku = sku_item['platformSku']
                                supplierSku = sku_item['supplierSku']
                                suffixZh = sku_item['suffixZh']
                                returnQuantity = sku_item['returnQuantity']

                                store_info = f'{store_username}\n{store_name}\n处理类型: {returnOrderTypeName}\n退货状态: {returnOrderStatusName}'
                                skc_info = f'SKC: {skc}\n供方货号: {supplierCode}\n预计退货数量/执行退货数量: {waitReturnQuantity}/{skcReturnQuantity}\n预计退货货值: {returnAmount} {currencyCode}'

                                row_item = []
                                row_item.append(returnOrderNo)
                                row_item.append(completeTime)
                                row_item.append(isSign)
                                row_item.append(store_info)
                                row_item.append(self.config.shein_store_manager.get(str(store_username).lower()))
                                row_item.append(returnReasonTypeName)
                                row_item.append(returnReason)
                                row_item.append(skc_img)
                                row_item.append(skc_info)
                                row_item.append(supplierSku)
                                row_item.append(suffixZh)
                                row_item.append(returnQuantity)
                                row_item.append(platformSku)
                                row_item.append(self.bridge.get_sku_supplier(supplierSku, erp))
                                row_item.append(self.bridge.get_sku_cost(supplierSku, erp))
                                row_item.append(package_name)
                                row_item.append(package_no)
                                row_item.append(returnPlanNo)
                                row_item.append(sellerOrderNo)
                                row_item.append(sellerDeliveryNo)
                                row_item.append(returnWayTypeName)
                                row_item.append(returnExpressCompanyName)
                                row_item.append(expressNoList)
                                row_item.append(returnAddress)
                                row_item.append(sellerContract)
                                row_item.append(sellerContractPhone)
                                row_item.append(urls)

                                excel_data.append(row_item)

        sheet_name = '昨日退货列表'

        cache_file_excel = f'{self.config.auto_dir}/shein/cache/shein_return_order_list_excel_{TimeUtils.today_date()}.json'
        write_dict_to_file(cache_file_excel, excel_data)

        batch_excel_operations(self.config.excel_return_list, [
            (sheet_name, 'write', excel_data, ['W', 'Z']),
            (sheet_name, 'format', self.format_return_list),
            ('Sheet1', 'delete')
        ])

    def format_return_list(self, sheet):
        merge_by_column_v2(sheet, '包裹号', ['包裹名'])
        merge_by_column_v2(sheet, '退货单号', ['签收状态', '店铺信息', '店长', '退货类型', '退货原因', 'SKC图片', 'SKC信息', '退货计划单号', '订单号', '发货单', '退货出库时间', '退回方式', '快递名称', '运单号', '退货地址', '商家联系人', '商家手机号', '入库问题图片地址'])
        beautify_title(sheet)
        add_borders(sheet)
        format_to_datetime(sheet, ['时间'])
        format_to_money(sheet, ['单价', '金额', '成本'])
        column_to_right(sheet, ['单价', '金额', '成本'])
        wrap_column(sheet, ['退货原因', '退货地址', '入库问题图片地址'])
        autofit_column(sheet, ['店铺信息', '店铺别名', 'SKC信息'])
        column_to_left(sheet, ['店铺信息', '商家SKU', '供方货号', '属性集', 'SKC信息', '退货地址'])
        specify_column_width(sheet, ['退货原因', 'SKC信息', '商家SKU', '退货地址'], 200 / 6)
        InsertImageV2(sheet, ['SKC图片'])

    def dealReturn(self, sheet):
        # 遍历可用行
        used_range_row = sheet.range('A1').expand('down')
        last_row = len(used_range_row)

        col_0 = find_column_by_data(sheet, 1, '实际退货/报废总数')
        if last_row < 3:
            fm = f'=SUM({col_0}3:{col_0}3)'
        else:
            fm = f'=SUM({col_0}3:{col_0}{last_row})'

        sheet.range(f'{col_0}2').formula = fm
        sheet.range(f'{col_0}2').font.color = (255, 0, 0)

        for i, cell in enumerate(used_range_row):
            row = i + 1
            if row < 3:
                continue
            sheet.range(f'{row}:{row}').font.name = 'Calibri'
            sheet.range(f'{row}:{row}').font.size = 11

        used_range_col = sheet.range('A1').expand('right')
        for j, cell in enumerate(used_range_col):
            col = j + 1
            col_name = index_to_column_name(col)
            col_val = sheet.range(f'{col_name}1').value
            if col_val not in ['']:
                sheet.range(f'{col_name}:{col_name}').autofit()  # 列宽自适应

            if '价' in col_val or '成本' in col_val or '金额' in col_val or '利润' in col_val:
                sheet.range(f'{col_name}:{col_name}').number_format = '¥#,##0.00'

            if '时间' in col_val:
                sheet.range(f'{col_name}:{col_name}').number_format = 'yyyy-mm-dd hh:mm:ss'

            if '月份' == col_val:
                sheet.range(f'{col_name}:{col_name}').number_format = 'yyyy-mm'

            # # 设置标题栏字体颜色与背景色
            # sheet.range(f'{col_name}1').color = (252,228,214)
            # sheet.range(f'{col_name}1').font.size = 12
            # sheet.range(f'{col_name}1').font.bold = True
            # sheet.range(f'{col_name}1').font.color = (0,0, 0)

            # 所有列水平居中和垂直居中
            sheet.range(f'{col_name}:{col_name}').api.HorizontalAlignment = -4108
            sheet.range(f'{col_name}:{col_name}').api.VerticalAlignment = -4108

            # 水平对齐：
            # -4108：居中
            # -4131：左对齐
            # -4152：右对齐

            # 垂直对齐：
            # -4108：居中
            # -4160：顶部对齐
            # -4107：底部对齐

        add_borders(sheet)

        # 获取第一行和第二行
        rows = sheet.range('1:2')
        # 设置字体名称
        rows.font.name = '微软雅黑'
        # 设置字体大小
        rows.font.size = 11
        # 设置字体加粗
        rows.font.bold = True
        # 设置标题栏字体颜色与背景色
        rows.color = (252, 228, 214)
        # 设置行高
        rows.row_height = 30

    def dealReplenish(self, sheet):
        # 遍历可用行
        used_range_row = sheet.range('A1').expand('down')
        last_row = len(used_range_row)
        # 获取最后一行的索引
        last_col = index_to_column_name(sheet.range('A1').end('right').column)
        # last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row

        col_3 = find_column_by_data(sheet, 1, '总金额')
        if last_row < 3:
            fm = f'=SUM({col_3}3:{col_3}3)'
        else:
            fm = f'=SUM({col_3}3:{col_3}{last_row})'

        sheet.range(f'{col_3}2').formula = fm
        sheet.range(f'{col_3}2').font.color = (255, 0, 0)

        for i, cell in enumerate(used_range_row):
            row = i + 1
            if row < 3:
                continue
            sheet.range(f'{row}:{row}').font.name = 'Calibri'
            sheet.range(f'{row}:{row}').font.size = 11

        used_range_col = sheet.range('A1').expand('right')
        for j, cell in enumerate(used_range_col):
            col = j + 1
            col_name = index_to_column_name(col)
            col_val = sheet.range(f'{col_name}1').value
            if col_val not in ['']:
                sheet.range(f'{col_name}:{col_name}').autofit()  # 列宽自适应

            if '价' in col_val or '成本' in col_val or '金额' in col_val or '利润' in col_val:
                sheet.range(f'{col_name}:{col_name}').number_format = '¥#,##0.00'

            if '时间' in col_val:
                sheet.range(f'{col_name}:{col_name}').number_format = 'yyyy-mm-dd hh:mm:ss'

            if '月份' == col_val:
                sheet.range(f'{col_name}:{col_name}').number_format = 'yyyy-mm'

            # 水平对齐： # -4108：居中 # -4131：左对齐 # -4152：右对齐
            # 垂直对齐： # -4108：居中 # -4160：顶部对齐 # -4107：底部对齐
            # 所有列水平居中和垂直居中
            sheet.range(f'{col_name}:{col_name}').api.HorizontalAlignment = -4108
            sheet.range(f'{col_name}:{col_name}').api.VerticalAlignment = -4108

        add_borders(sheet)

        # === 批量字体设置 ===
        if last_row > 3:
            data_range = sheet.range(f'A3:{last_col}{last_row}')
            data_range.api.Font.Name = "Calibri"
            data_range.api.Font.Size = 11

        # 获取第一行和第二行
        rows = sheet.range('1:2')
        # 设置字体名称
        rows.font.name = '微软雅黑'
        # 设置字体大小
        rows.font.size = 11
        # 设置字体加粗
        rows.font.bold = True
        # 设置标题栏字体颜色与背景色
        rows.color = (252, 228, 214)
        # 设置行高
        rows.row_height = 30

    def dealSheinStock(self, sheet):
        col_0 = find_column_by_data(sheet, 1, '期末库存数量')
        col_1 = find_column_by_data(sheet, 1, '期末库存金额')
        col_2 = find_column_by_data(sheet, 1, '单价成本')
        col_3 = find_column_by_data(sheet, 1, '希音仓成本总额')

        col_4 = find_column_by_data(sheet, 1, '期初库存数量')
        col_5 = find_column_by_data(sheet, 1, '期初库存金额')

        col_6 = find_column_by_data(sheet, 1, '入库数量')
        col_7 = find_column_by_data(sheet, 1, '入库金额')
        col_8 = find_column_by_data(sheet, 1, '出库数量')
        col_9 = find_column_by_data(sheet, 1, '出库金额')

        col_10 = find_column_by_data(sheet, 1, '出库成本总额')
        col_11 = find_column_by_data(sheet, 1, '出库利润')
        col_12 = find_column_by_data(sheet, 1, '出库利润率')

        # 遍历可用行
        used_range_row = sheet.range('A1').expand('down')
        last_row = len(used_range_row)
        # # 获取最后一行的索引
        last_col = index_to_column_name(sheet.range('A1').end('right').column)
        # last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row
        if last_row > 2:
            sheet.range(f'{col_0}2').formula = f'=SUM({col_0}3:{col_0}{last_row})'
            sheet.range(f'{col_0}2').font.color = (225, 0, 0)
            sheet.range(f'{col_1}2').formula = f'=SUM({col_1}3:{col_1}{last_row})'
            sheet.range(f'{col_1}2').font.color = (225, 0, 0)
            sheet.range(f'{col_3}2').formula = f'=SUM({col_3}3:{col_3}{last_row})'
            sheet.range(f'{col_3}2').font.color = (255, 0, 0)

            sheet.range(f'{col_4}2').formula = f'=SUM({col_4}3:{col_4}{last_row})'
            sheet.range(f'{col_4}2').font.color = (225, 0, 0)
            sheet.range(f'{col_5}2').formula = f'=SUM({col_5}3:{col_5}{last_row})'
            sheet.range(f'{col_5}2').font.color = (225, 0, 0)

            sheet.range(f'{col_6}2').formula = f'=SUM({col_6}3:{col_6}{last_row})'
            sheet.range(f'{col_6}2').font.color = (225, 0, 0)
            sheet.range(f'{col_7}2').formula = f'=SUM({col_7}3:{col_7}{last_row})'
            sheet.range(f'{col_7}2').font.color = (225, 0, 0)
            sheet.range(f'{col_8}2').formula = f'=SUM({col_8}3:{col_8}{last_row})'
            sheet.range(f'{col_8}2').font.color = (225, 0, 0)
            sheet.range(f'{col_9}2').formula = f'=SUM({col_9}3:{col_9}{last_row})'
            sheet.range(f'{col_9}2').font.color = (225, 0, 0)

            sheet.range(f'{col_10}2').formula = f'=SUM({col_10}3:{col_10}{last_row})'
            sheet.range(f'{col_10}2').font.color = (225, 0, 0)

            sheet.range(f'{col_11}2').formula = f'=SUM({col_11}3:{col_11}{last_row})'
            sheet.range(f'{col_11}2').font.color = (225, 0, 0)

            if last_row > 3:
                # 设置毛利润和毛利润率列公式与格式
                sheet.range(f'{col_3}3').formula = f'={col_0}3*{col_2}3'
                # AutoFill 快速填充到所有行（3 到 last_row）
                sheet.range(f'{col_3}3').api.AutoFill(sheet.range(f'{col_3}3:{col_3}{last_row}').api)

                sheet.range(f'{col_10}3').formula = f'={col_8}3*{col_2}3'
                sheet.range(f'{col_10}3').api.AutoFill(sheet.range(f'{col_10}3:{col_10}{last_row}').api)

                sheet.range(f'{col_11}3').formula = f'={col_9}3-{col_10}3'
                sheet.range(f'{col_11}3').api.AutoFill(sheet.range(f'{col_11}3:{col_11}{last_row}').api)

                sheet.range(f'{col_12}3').number_format = '0.00%'
                sheet.range(f'{col_12}3').formula = f'=IF({col_9}3 > 0,{col_11}3/{col_9}3,0)'
                sheet.range(f'{col_12}3').api.AutoFill(sheet.range(f'{col_12}3:{col_12}{last_row}').api)

        used_range_col = sheet.range('A1').expand('right')
        for j, cell in enumerate(used_range_col):
            col = j + 1
            col_name = index_to_column_name(col)
            col_val = sheet.range(f'{col_name}1').value
            if col_val not in ['']:
                sheet.range(f'{col_name}:{col_name}').autofit()  # 列宽自适应

            if col_val in ['业务单号']:
                sheet.range(f'{col_name}:{col_name}').number_format = '@'

            if '价' in col_val or '成本' in col_val or '金额' in col_val or ('利润' in col_val and '率' not in col_val):
                sheet.range(f'{col_name}:{col_name}').number_format = '¥#,##0.00'

            if '时间' in col_val:
                sheet.range(f'{col_name}:{col_name}').number_format = 'yyyy-mm-dd hh:mm:ss'

            if '月份' == col_val:
                sheet.range(f'{col_name}:{col_name}').number_format = 'yyyy-mm'

            # 水平对齐： # -4108：居中 # -4131：左对齐 # -4152：右对齐
            # 垂直对齐： # -4108：居中 # -4160：顶部对齐 # -4107：底部对齐
            # 所有列水平居中和垂直居中
            sheet.range(f'{col_name}:{col_name}').api.HorizontalAlignment = -4108
            sheet.range(f'{col_name}:{col_name}').api.VerticalAlignment = -4108

        add_borders(sheet)

        # === 批量字体设置 ===
        if last_row > 3:
            data_range = sheet.range(f'A3:{last_col}{last_row}')
            data_range.api.Font.Name = "Calibri"
            data_range.api.Font.Size = 11

        set_title_style(sheet)

    def dealSalesPercentageExcel(self, sheet):
        col_0 = find_column_by_data(sheet, 1, '商家SKU')
        col_1 = find_column_by_data(sheet, 1, '售出数量')
        col_2 = find_column_by_data(sheet, 1, '销量占比')
        col_3 = find_column_by_data(sheet, 1, '售出金额')
        col_4 = find_column_by_data(sheet, 1, '销售额占比')
        col_5 = find_column_by_data(sheet, 1, '利润')
        col_6 = find_column_by_data(sheet, 1, '利润占比')
        col_7 = find_column_by_data(sheet, 1, 'SKU图片')

        # 遍历可用行
        used_range_row = sheet.range('B1').expand('down')
        last_row = len(used_range_row)
        if last_row > 2:
            sheet.range(f'{col_1}2').formula = f'=SUM({col_1}3:{col_1}{last_row})'
            sheet.range(f'{col_1}2').font.color = (255, 0, 0)
            sheet.range(f'{col_3}2').formula = f'=SUM({col_3}3:{col_3}{last_row})'
            sheet.range(f'{col_3}2').font.color = (255, 0, 0)
            sheet.range(f'{col_5}2').formula = f'=SUM({col_5}3:{col_5}{last_row})'
            sheet.range(f'{col_5}2').font.color = (255, 0, 0)
            # sheet.range(f'{col_7}1:{col_7}2').merge()

        for i, cell in enumerate(used_range_row):
            row = i + 1
            if row < 3:
                continue
            sheet.range(f'{row}:{row}').font.name = 'Calibri'
            sheet.range(f'{row}:{row}').font.size = 11

            sheet.range(f'{col_2}{row}').formula = f'={col_1}{row}/{col_1}2'
            sheet.range(f'{col_4}{row}').formula = f'={col_3}{row}/{col_3}2'
            sheet.range(f'{col_6}{row}').formula = f'={col_5}{row}/{col_5}2'

        used_range_col = sheet.range('A1').expand('right')
        for j, cell in enumerate(used_range_col):
            col = j + 1
            col_name = index_to_column_name(col)
            col_val = sheet.range(f'{col_name}1').value
            if col_val not in ['']:
                sheet.range(f'{col_name}:{col_name}').autofit()  # 列宽自适应

            if col_val in ['占比']:
                sheet.range(f'{col_name}:{col_name}').number_format = '0.00%'

            if ('价' in col_val or '成本' in col_val or '金额' in col_val or '利润' == col_val):
                sheet.range(f'{col_name}:{col_name}').number_format = '¥#,##0.00'

            if '时间' in col_val:
                sheet.range(f'{col_name}:{col_name}').number_format = 'yyyy-mm-dd hh:mm:ss'

            # # 设置标题栏字体颜色与背景色
            # sheet.range(f'{col_name}1').color = (252,228,214)
            # sheet.range(f'{col_name}1').font.size = 12
            # sheet.range(f'{col_name}1').font.bold = True
            # sheet.range(f'{col_name}1').font.color = (0,0, 0)

            # 所有列水平居中和垂直居中
            sheet.range(f'{col_name}:{col_name}').api.HorizontalAlignment = -4108
            sheet.range(f'{col_name}:{col_name}').api.VerticalAlignment = -4108

            # 水平对齐：
            # -4108：居中
            # -4131：左对齐
            # -4152：右对齐

            # 垂直对齐：
            # -4108：居中
            # -4160：顶部对齐
            # -4107：底部对齐

        add_borders(sheet)

        # 获取第一行和第二行
        rows = sheet.range('1:2')
        # 设置字体名称
        rows.font.name = '微软雅黑'
        # 设置字体大小
        rows.font.size = 11
        # 设置字体加粗
        rows.font.bold = True
        # 设置标题栏字体颜色与背景色
        rows.color = (252, 228, 214)
        # 设置行高
        rows.row_height = 30

    def dealMonthNoSettleMentExcel(self, sheet):
        col_0 = find_column_by_data(sheet, 1, '数量')
        col_2 = find_column_by_data(sheet, 1, '金额')
        col_3 = find_column_by_data(sheet, 1, '单价成本')
        col_4 = find_column_by_data(sheet, 1, 'SKU图片')
        col_5 = find_column_by_data(sheet, 1, '结算类型')
        col_8 = find_column_by_data(sheet, 1, '成本总额')

        # 设置格式
        used_range_col = sheet.range('A1').expand('right')
        for j, cell in enumerate(used_range_col):
            col = j + 1
            col_name = index_to_column_name(col)
            col_val = sheet.range(f'{col_name}1').value
            if col_val not in ['']:
                sheet.range(f'{col_name}:{col_name}').autofit()  # 列宽自适应

            if col_val in ['业务单号']:
                sheet.range(f'{col_name}:{col_name}').number_format = '@'

            if '价' in col_val or '成本' in col_val or '金额' in col_val or '利润' in col_val:
                sheet.range(f'{col_name}:{col_name}').number_format = '¥#,##0.00'

            if '时间' in col_val:
                sheet.range(f'{col_name}:{col_name}').number_format = 'yyyy-mm-dd hh:mm:ss'

            # 水平对齐： # -4108：居中 # -4131：左对齐 # -4152：右对齐
            # 垂直对齐： # -4108：居中 # -4160：顶部对齐 # -4107：底部对齐
            # 所有列水平居中和垂直居中
            sheet.range(f'{col_name}:{col_name}').api.HorizontalAlignment = -4108
            sheet.range(f'{col_name}:{col_name}').api.VerticalAlignment = -4108

        # 批量设置公式
        last_col = index_to_column_name(sheet.range('A1').end('right').column)  # 获取最后一行的索引
        last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row
        if last_row > 2:
            # 第3行公式（填一次）
            sheet.range(f'{col_8}2').formula = f'=SUM({col_8}3:{col_8}{last_row})'
            sheet.range(f'{col_8}2').font.color = (255, 0, 0)
            # AutoFill 快速填充到所有行（3 到 last_row）
            sheet.range(f'{col_8}3').formula = f'={col_3}3*{col_0}3'

            if last_row > 3:
                sheet.range(f'{col_8}3').api.AutoFill(sheet.range(f'{col_8}3:{col_8}{last_row}').api)

        sheet.range(f'{col_4}1').column_width = 0

        # 批量设置边框
        add_borders(sheet)

        if last_row > 2:
            # === 批量字体设置 ===
            data_range = sheet.range(f'A3:{last_col}{last_row}')
            data_range.api.Font.Name = "Calibri"
            data_range.api.Font.Size = 11

        set_title_style(sheet)

    def dealMonthBackDetailExcel(self, sheet, summary=0):
        col_0 = find_column_by_data(sheet, 1, '数量')
        col_2 = find_column_by_data(sheet, 1, '金额')
        col_3 = find_column_by_data(sheet, 1, '单价成本')
        col_4 = find_column_by_data(sheet, 1, 'SKU图片')
        col_5 = find_column_by_data(sheet, 1, '结算类型')
        col_8 = find_column_by_data(sheet, 1, '成本总额')

        # 设置格式
        used_range_col = sheet.range('A1').expand('right')
        for j, cell in enumerate(used_range_col):
            col = j + 1
            col_name = index_to_column_name(col)
            col_val = sheet.range(f'{col_name}1').value
            if col_val not in ['']:
                sheet.range(f'{col_name}:{col_name}').autofit()  # 列宽自适应

            if col_val in ['业务单号']:
                sheet.range(f'{col_name}:{col_name}').number_format = '@'

            if '价' in col_val or '成本' in col_val or '金额' in col_val or '利润' in col_val:
                sheet.range(f'{col_name}:{col_name}').number_format = '¥#,##0.00'

            if '时间' in col_val:
                sheet.range(f'{col_name}:{col_name}').number_format = 'yyyy-mm-dd hh:mm:ss'

            # 水平对齐： # -4108：居中 # -4131：左对齐 # -4152：右对齐
            # 垂直对齐： # -4108：居中 # -4160：顶部对齐 # -4107：底部对齐
            # 所有列水平居中和垂直居中
            sheet.range(f'{col_name}:{col_name}').api.HorizontalAlignment = -4108
            sheet.range(f'{col_name}:{col_name}').api.VerticalAlignment = -4108

        # 批量设置公式
        last_col = index_to_column_name(sheet.range('A1').end('right').column)  # 获取最后一行的索引
        last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row
        if summary == 1:
            if last_row > 1:
                sheet.range(f'{col_8}2').formula = f'={col_3}2*{col_0}2'
                if last_row > 2:
                    # AutoFill 快速填充到所有行（3 到 last_row）
                    sheet.range(f'{col_8}3').api.AutoFill(sheet.range(f'{col_8}3:{col_8}{last_row}').api)
        else:
            if last_row > 2:
                # 合计行设置
                sheet.range(f'{col_0}2').formula = f'=SUM({col_0}3:{col_0}{last_row})'
                sheet.range(f'{col_0}2').font.color = (255, 0, 0)

                sheet.range(f'{col_2}2').formula = f'=SUM({col_2}3:{col_2}{last_row})'
                sheet.range(f'{col_2}2').font.color = (255, 0, 0)

                sheet.range(f'{col_8}2').formula = f'=SUM({col_8}3:{col_8}{last_row})'
                sheet.range(f'{col_8}2').font.color = (255, 0, 0)

                # AutoFill 快速填充到所有行（3 到 last_row）
                sheet.range(f'{col_8}3').formula = f'={col_3}3*{col_0}3'

            if last_row > 3:
                sheet.range(f'{col_8}3').api.AutoFill(sheet.range(f'{col_8}3:{col_8}{last_row}').api)

            set_title_style(sheet)

        sheet.range(f'{col_4}1').column_width = 0

        # 批量设置边框
        add_borders(sheet)

        if last_row > 3:
            # === 批量字体设置 ===
            data_range = sheet.range(f'A3:{last_col}{last_row}')
            data_range.api.Font.Name = "Calibri"
            data_range.api.Font.Size = 11

    def dealMonthSalesDetailExcel(self, sheet):
        col_0 = find_column_by_data(sheet, 1, '数量')
        col_1 = find_column_by_data(sheet, 1, '利润')
        col_2 = find_column_by_data(sheet, 1, '金额')
        col_3 = find_column_by_data(sheet, 1, '单价成本')
        col_4 = find_column_by_data(sheet, 1, 'SKU图片')
        col_5 = find_column_by_data(sheet, 1, '结算类型')
        col_6 = find_column_by_data(sheet, 1, '售出数量')
        col_7 = find_column_by_data(sheet, 1, '售出金额')

        # 设置格式
        used_range_col = sheet.range('A1').expand('right')
        for j, cell in enumerate(used_range_col):
            col = j + 1
            col_name = index_to_column_name(col)
            col_val = sheet.range(f'{col_name}1').value
            if col_val not in ['']:
                sheet.range(f'{col_name}:{col_name}').autofit()  # 列宽自适应

            if col_val in ['业务单号']:
                sheet.range(f'{col_name}:{col_name}').number_format = '@'

            if '价' in col_val or '成本' in col_val or '金额' in col_val or '利润' in col_val:
                sheet.range(f'{col_name}:{col_name}').number_format = '¥#,##0.00'

            if '时间' in col_val:
                sheet.range(f'{col_name}:{col_name}').number_format = 'yyyy-mm-dd hh:mm:ss'

            # 水平对齐： # -4108：居中 # -4131：左对齐 # -4152：右对齐
            # 垂直对齐： # -4108：居中 # -4160：顶部对齐 # -4107：底部对齐
            # 所有列水平居中和垂直居中
            sheet.range(f'{col_name}:{col_name}').api.HorizontalAlignment = -4108
            sheet.range(f'{col_name}:{col_name}').api.VerticalAlignment = -4108

        # 批量设置公式
        last_col = index_to_column_name(sheet.range('A1').end('right').column)  # 获取最后一行的索引
        last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row
        if last_row > 2:
            # 第3行公式（填一次）
            sheet.range(
                f'{col_1}3').formula = f'=IF(AND(ISNUMBER({col_3}3),{col_5}3="收入结算"),{col_2}3-{col_3}3*{col_0}3,0)'
            sheet.range(f'{col_6}3').formula = f'=IF(AND(ISNUMBER({col_3}3),{col_5}3="收入结算"),{col_0}3,0)'
            sheet.range(f'{col_7}3').formula = f'=IF(AND(ISNUMBER({col_3}3),{col_5}3="收入结算"),{col_2}3,0)'

            if last_row > 3:
                # AutoFill 快速填充到所有行（3 到 last_row）
                sheet.range(f'{col_1}3').api.AutoFill(sheet.range(f'{col_1}3:{col_1}{last_row}').api)
                sheet.range(f'{col_6}3').api.AutoFill(sheet.range(f'{col_6}3:{col_6}{last_row}').api)
                sheet.range(f'{col_7}3').api.AutoFill(sheet.range(f'{col_7}3:{col_7}{last_row}').api)

            # 合计行设置
            sheet.range(f'{col_0}2').formula = f'=SUM({col_0}3:{col_0}{last_row})'
            sheet.range(f'{col_0}2').font.color = (255, 0, 0)

            sheet.range(f'{col_2}2').formula = f'=SUM({col_2}3:{col_2}{last_row})'
            sheet.range(f'{col_2}2').font.color = (255, 0, 0)

            sheet.range(f'{col_1}2').formula = f'=SUM({col_1}3:{col_1}{last_row})'
            sheet.range(f'{col_1}2').font.color = (255, 0, 0)

            sheet.range(f'{col_6}2').formula = f'=SUM({col_6}3:{col_6}{last_row})'
            sheet.range(f'{col_6}2').font.color = (255, 0, 0)

            sheet.range(f'{col_7}2').formula = f'=SUM({col_7}3:{col_7}{last_row})'
            sheet.range(f'{col_7}2').font.color = (255, 0, 0)

            sheet.range(f'{col_4}1').column_width = 0

        # 批量设置边框
        add_borders(sheet)

        if last_row > 3:
            # === 批量字体设置 ===
            data_range = sheet.range(f'A3:{last_col}{last_row}')
            data_range.api.Font.Name = "Calibri"
            data_range.api.Font.Size = 11
            log(f'设置字体: A3:{col_7}{last_row}')

        # 获取第一行和第二行
        rows = sheet.range('1:2')
        # 设置字体名称
        rows.font.name = '微软雅黑'
        # 设置字体大小
        rows.font.size = 11
        # 设置字体加粗
        rows.font.bold = True
        # 设置标题栏字体颜色与背景色
        rows.color = (252, 228, 214)
        # 设置行高
        rows.row_height = 30

    def calc_month_sales_percentage(self, month_data):
        df = pd.DataFrame(data=month_data[2:], columns=month_data[:1][0])

        # 确保 "商家SKU" 是字符串
        df["商家SKU"] = df["商家SKU"].astype(str).str.strip()

        # 确保 "数量", "金额", "单价成本" 是数值类型
        df["售出数量"] = pd.to_numeric(df["售出数量"], errors="coerce")
        df["售出金额"] = pd.to_numeric(df["售出金额"], errors="coerce")
        df["单价成本"] = pd.to_numeric(df["单价成本"], errors="coerce")

        # 重新计算利润
        df["利润"] = np.where(
            df["结算类型"] == "收入结算",
            df["售出金额"] - (df["单价成本"] * df["售出数量"]),
            0
        )

        # 进行分组统计（求和）
        summary = df.groupby("商家SKU", as_index=False).agg({
            "售出数量": "sum",
            "售出金额": "sum",
            "利润"    : "sum",
            "SKU图片" : "first"
        })

        # 计算总值
        total_quantity = summary["售出数量"].sum()
        total_amount = summary["售出金额"].sum()
        total_profit = summary["利润"].sum()

        # 计算占比
        summary["销量占比"] = summary["售出数量"] / total_quantity * 100
        summary["销售额占比"] = summary["售出金额"] / total_amount * 100
        summary["利润占比"] = summary["利润"] / total_profit * 100

        # 确保显示 2 位小数，并加上百分号
        summary["销量占比"] = summary["销量占比"].map(lambda x: f"{x:.2f}%")
        summary["销售额占比"] = summary["销售额占比"].map(lambda x: f"{x:.2f}%")
        summary["利润占比"] = summary["利润占比"].map(lambda x: f"{x:.2f}%")

        # 重新排序列
        summary = summary[["SKU图片", "商家SKU", "售出数量", "销量占比", "售出金额", "销售额占比", "利润", "利润占比"]]
        summary_list = summary.values.tolist()

        summary_list.insert(0, ['', '合计', '', '', '', '', '', ''])  # 把表头插入到数据列表的第一行
        # 添加标题行（表头）
        header = summary.columns.tolist()
        summary_list.insert(0, header)  # 把表头插入到数据列表的第一行

        return summary_list

    def dealMonthSalesDetailExcel_old(self, sheet):
        col_0 = find_column_by_data(sheet, 1, '数量')
        col_1 = find_column_by_data(sheet, 1, '利润')
        col_2 = find_column_by_data(sheet, 1, '金额')
        col_3 = find_column_by_data(sheet, 1, '单价成本')
        col_4 = find_column_by_data(sheet, 1, 'SKU图片')
        col_5 = find_column_by_data(sheet, 1, '结算类型')
        col_6 = find_column_by_data(sheet, 1, '售出数量')
        col_7 = find_column_by_data(sheet, 1, '售出金额')
        # 遍历可用行
        used_range_row = sheet.range('A1').expand('down')
        last_row = len(used_range_row)
        for i, cell in enumerate(used_range_row):
            row = i + 1
            if row < 3:
                continue
            sheet.range(f'{row}:{row}').font.name = 'Calibri'
            sheet.range(f'{row}:{row}').font.size = 11
            range0 = f'{col_0}{row}'
            range2 = f'{col_2}{row}'
            range3 = f'{col_3}{row}'
            range5 = f'{col_5}{row}'
            # 设置毛利润和毛利润率列公式与格式
            sheet.range(
                f'{col_1}{row}').formula = f'=IF(AND(ISNUMBER({range3}),{range5}="收入结算"),{range2}-{range3}*{range0},0)'
            sheet.range(f'{col_6}{row}').formula = f'=IF(AND(ISNUMBER({range3}),{range5}="收入结算"),{range0},0)'
            sheet.range(f'{col_7}{row}').formula = f'=IF(AND(ISNUMBER({range3}),{range5}="收入结算"),{range2},0)'
            log(f'处理公式: {row}/{last_row}')

        if last_row > 2:
            sheet.range(f'{col_0}2').formula = f'=SUM({col_0}3:{col_0}{last_row})'
            sheet.range(f'{col_0}2').font.color = (255, 0, 0)
            sheet.range(f'{col_2}2').formula = f'=SUM({col_2}3:{col_2}{last_row})'
            sheet.range(f'{col_2}2').font.color = (255, 0, 0)
            sheet.range(f'{col_1}2').formula = f'=SUM({col_1}3:{col_1}{last_row})'
            sheet.range(f'{col_1}2').font.color = (255, 0, 0)
            sheet.range(f'{col_6}2').formula = f'=SUM({col_6}3:{col_6}{last_row})'
            sheet.range(f'{col_6}2').font.color = (255, 0, 0)
            sheet.range(f'{col_7}2').formula = f'=SUM({col_7}3:{col_7}{last_row})'
            sheet.range(f'{col_7}2').font.color = (255, 0, 0)
            sheet.range(f'{col_4}1').column_width = 0
            # # 设置计算模式为自动计算
            # sheet.api.Application.Calculation = -4105  # -4105 代表自动计算模式
            # # 手动触发一次计算
            # sheet.api.Calculate()

        used_range_col = sheet.range('A1').expand('right')
        for j, cell in enumerate(used_range_col):
            col = j + 1
            col_name = index_to_column_name(col)
            col_val = sheet.range(f'{col_name}1').value
            if col_val not in ['']:
                sheet.range(f'{col_name}:{col_name}').autofit()  # 列宽自适应

            if col_val in ['业务单号']:
                sheet.range(f'{col_name}:{col_name}').number_format = '@'

            if '价' in col_val or '成本' in col_val or '金额' in col_val or '利润' in col_val:
                sheet.range(f'{col_name}:{col_name}').number_format = '¥#,##0.00'

            if '时间' in col_val:
                sheet.range(f'{col_name}:{col_name}').number_format = 'yyyy-mm-dd hh:mm:ss'

            # # 设置标题栏字体颜色与背景色
            # sheet.range(f'{col_name}1').color = (252,228,214)
            # sheet.range(f'{col_name}1').font.size = 12
            # sheet.range(f'{col_name}1').font.bold = True
            # sheet.range(f'{col_name}1').font.color = (0,0, 0)

            # 所有列水平居中和垂直居中
            sheet.range(f'{col_name}:{col_name}').api.HorizontalAlignment = -4108
            sheet.range(f'{col_name}:{col_name}').api.VerticalAlignment = -4108

            # 水平对齐：
            # -4108：居中
            # -4131：左对齐
            # -4152：右对齐

            # 垂直对齐：
            # -4108：居中
            # -4160：顶部对齐
            # -4107：底部对齐

        add_borders(sheet)

        # 获取第一行和第二行
        rows = sheet.range('1:2')
        # 设置字体名称
        rows.font.name = '微软雅黑'
        # 设置字体大小
        rows.font.size = 11
        # 设置字体加粗
        rows.font.bold = True
        # 设置标题栏字体颜色与背景色
        rows.color = (252, 228, 214)
        # 设置行高
        rows.row_height = 30

    def write_month_sales_detail(self, store_username, store_name, ledger_list, shein_stock_list, shein_replenish_list, shein_return_list, shein_back_list, shein_no_settlement_list):
        last_month = TimeUtils.get_last_month()

        supplierName = ''

        excel_path_month = str(self.config.excel_shein_finance_month_report).replace('#store_name#', store_name)

        month_data = [[
            '平台SKU', '商家SKU', '属性集', '数量', '单价', '金额', '单价成本', '利润', '售出数量', '售出金额', '添加时间',
            '业务单号', '单据号', '变动类型', '结算类型', 'SKC', '供方货号', '供应商名称', 'SKU图片',
        ], ['合计', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']]
        log('len(ledger_list)', len(ledger_list))
        for month_item in ledger_list:
            row_item = []
            supplierName = month_item['supplierName']
            platform_sku = month_item['sku']
            row_item.append(platform_sku)
            supplier_sku = month_item['supplierSku'] if month_item['supplierSku'] else '-'
            row_item.append(supplier_sku)
            row_item.append(month_item['suffixZh'])
            row_item.append(month_item['quantity'])
            row_item.append(month_item['cost'])
            row_item.append(month_item['amount'])
            row_item.append(month_item['cost_price'])
            row_item.append('')
            row_item.append(
                month_item['quantity'] if month_item['cost_price'] and month_item['settleTypeName'] == '收入结算' else 0)
            row_item.append(
                month_item['amount'] if month_item['cost_price'] and month_item['settleTypeName'] == '收入结算' else 0)
            row_item.append(month_item['addTime'])
            row_item.append(month_item['businessNo'])
            row_item.append(month_item['billNo'])
            row_item.append(month_item['displayChangeTypeName'])
            row_item.append(month_item['settleTypeName'])
            row_item.append(month_item['skc'])
            row_item.append(month_item['supplierCode'])
            row_item.append(month_item['supplierName'])
            row_item.append(month_item['sku_img'])
            month_data.append(row_item)

        sheet_name = f'{last_month}月销售明细'

        write_data(excel_path_month, sheet_name, sort_by_column(month_data, 1, 2, False), ['L'])
        app, wb, sheet = open_excel(excel_path_month, sheet_name)
        set_title_style(sheet, 2)
        set_body_style(sheet, 3)
        add_borders(sheet)
        format_to_money(sheet, ['单价', '金额', '利润'])
        format_to_datetime(sheet, ['时间'])
        add_formula_for_column(sheet, '利润', '=IF(AND(ISNUMBER(G3),O3="收入结算"),F3-G3*D3,0)', 3)
        add_formula_for_column(sheet, '售出数量', '=IF(AND(ISNUMBER(G3),O3="收入结算"),D3,0)', 3)
        add_formula_for_column(sheet, '售出金额', '=IF(AND(ISNUMBER(G3),O3="收入结算"),F3,0)', 3)
        add_sum_for_cell(sheet, ['数量', '金额', '利润', '售出数量', '售出金额'])
        column_to_left(sheet, ['平台SKU', '商家SKU', '属性集'])
        column_to_right(sheet, ['单价', '金额', '利润'])
        hidden_columns(sheet, ['SKU图片'])
        close_excel(app, wb)

        summary_list = self.calc_month_sales_percentage(month_data)

        sheet_name = f'{last_month}月销售占比'

        write_data(excel_path_month, sheet_name, sort_by_column(summary_list, 6, 2))
        app, wb, sheet = open_excel(excel_path_month, sheet_name)
        set_title_style(sheet, 2)
        set_body_style(sheet, 3)
        add_borders(sheet)
        format_to_money(sheet, ['金额', '利润'])
        format_to_percent(sheet, ['占比'])
        add_sum_for_cell(sheet, ['利润', '售出数量', '售出金额'])
        column_to_left(sheet, ['商家SKU'])
        column_to_right(sheet, ['金额', '利润'])
        InsertImageV2(sheet, ['SKU图片'], 'shein', 90, None, None, True, 3)
        close_excel(app, wb)

        stock_data = [[
            '月份', 'SKC', '供方货号', '平台SKU', '商家SKU', '属性集', '期初库存数量', '期初库存金额', '入库数量',
            '入库金额', '出库数量', '出库金额', '期末库存数量', '期末库存金额', '单价成本', '出库成本总额',
            '希音仓成本总额', '出库利润', '出库利润率', '供应商名称', '店铺账号', '店铺别名'
        ], [
            '合计', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''
        ]]

        for stock_item in shein_stock_list:
            row_item = []
            row_item.append(stock_item['reportDate'])
            row_item.append(stock_item['skc'])
            row_item.append(stock_item['supplierCode'])
            row_item.append(stock_item['skuCode'])
            row_item.append(stock_item['supplierSku'])
            row_item.append(stock_item['suffixZh'])
            row_item.append(stock_item['beginBalanceCnt'])
            row_item.append(stock_item['beginBalanceAmount'])
            row_item.append(stock_item['inCnt'])
            row_item.append(stock_item['inAmount'])
            row_item.append(stock_item['outCnt'])
            row_item.append(stock_item['outAmount'])
            row_item.append(stock_item['endBalanceCnt'])
            row_item.append(stock_item['endBalanceAmount'])
            row_item.append(stock_item['cost_price'])
            row_item.append('')
            row_item.append('')
            row_item.append('')
            row_item.append('')
            row_item.append(stock_item['supplierName'])
            row_item.append(store_username)
            row_item.append(store_name)
            stock_data.append(row_item)

        sheet_name = f'{last_month}月库存结余'
        write_dict_to_file_ex(f'{self.config.auto_dir}/shein/cache/sheet_{last_month}_库存结余.json', {store_username: stock_data[:1] + stock_data[2:]}, [store_username])

        write_data(excel_path_month, sheet_name, sort_by_column(stock_data, 11, 2))
        app, wb, sheet = open_excel(excel_path_month, sheet_name)
        set_title_style(sheet, 2)
        set_body_style(sheet, 3)
        add_borders(sheet)
        format_to_money(sheet, ['金额', '总额', '成本', '出库利润'])
        column_to_right(sheet, ['金额', '总额', '成本', '出库利润'])
        format_to_percent(sheet, ['利润率'])
        column_to_left(sheet, ['供方货号', '平台SKU', '商家SKU', '属性集'])
        add_sum_for_cell(sheet, ['期初库存数量', '期初库存金额', '入库数量', '入库金额', '出库数量', '出库金额', '期末库存数量', '期末库存金额', '出库成本总额', '希音仓成本总额', '出库利润'])
        add_formula_for_column(sheet, '出库成本总额', '=K3*O3', 3)
        add_formula_for_column(sheet, '希音仓成本总额', '=M3*O3', 3)
        add_formula_for_column(sheet, '出库利润', '=L3-P3', 3)
        add_formula_for_column(sheet, '出库利润率', '=IF(L3 > 0,R3/L3,0)', 3)
        sheet.autofit()
        close_excel(app, wb)

        replenish_data = [[
            "补扣款单号", "款项类型", "补扣款分类", "对单类型", "关联单据", "单价", "数量", "总金额", "币种", "创建时间",
            "单据状态", "关联报账单", "拒绝原因", "确认/拒绝时间", "操作人", "会计日期", "是否可报账", "申诉单号",
            "公司主体", "出口模式", "备注", "供货商名称", "店铺账号", "店铺别名"
        ], [
            "合计", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
        ]]

        for replenish_item in shein_replenish_list:
            row_item = []
            row_item.append(replenish_item['replenishNo'])
            row_item.append(replenish_item['replenishTypeName'])
            row_item.append(replenish_item['categoryName'])
            row_item.append(replenish_item['toOrderTypeName'])
            row_item.append(replenish_item['relationNo'])
            row_item.append(replenish_item['unitPrice'])
            row_item.append(replenish_item['quantity'])
            row_item.append(replenish_item['amount'])
            row_item.append(replenish_item['currencyCode'])
            row_item.append(replenish_item['addTime'])
            row_item.append(replenish_item['replenishStatusName'])
            row_item.append(replenish_item['reportOrderNo'])
            row_item.append(replenish_item['refuseReason'])
            row_item.append(replenish_item['decisionTime'])
            row_item.append(replenish_item['operator'])
            row_item.append(replenish_item['accountDate'])
            row_item.append(replenish_item['reportableName'])
            row_item.append(replenish_item['billNo'])
            row_item.append(replenish_item['companyName'])
            row_item.append(replenish_item['exportingModeName'])
            row_item.append(replenish_item['remark'])
            row_item.append(supplierName)
            row_item.append(store_username)
            row_item.append(store_name)
            replenish_data.append(row_item)

        sheet_name = f'{last_month}月补扣款列表'

        write_dict_to_file_ex(f'{self.config.auto_dir}/shein/cache/sheet_{last_month}_补扣款列表.json', {store_username: replenish_data[:1] + replenish_data[2:]}, [store_username])

        write_data(excel_path_month, sheet_name, replenish_data)

        app, wb, sheet = open_excel(excel_path_month, sheet_name)
        set_title_style(sheet, 2)
        set_body_style(sheet, 3)
        add_borders(sheet)
        format_to_money(sheet, ['金额', '单价'])
        column_to_right(sheet, ['金额', '单价'])
        format_to_datetime(sheet, ['时间'])
        add_sum_for_cell(sheet, ['总金额'])
        sheet.autofit()
        close_excel(app, wb)

        return_data = [[
            "退货单号", "退货计划单号", "处理类型", "发起原因", "说明", "状态", "退货方式", "退货仓库", "商家货号", "SKC",
            "待退货总数", "实际退货/报废总数", "签收时间", "创建时间", "运单号", "退货联系人", "联系人手机号", "退货地址"
        ], [
            "合计", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
        ]]

        if len(shein_return_list) > 0:
            log(shein_return_list)
            for return_item in shein_return_list:
                row_item = []
                log(return_item)
                row_item.append(return_item['returnOrderNo'])
                row_item.append(return_item['returnPlanNo'])
                row_item.append(return_item['returnOrderTypeName'])
                row_item.append(return_item['returnReasonTypeName'])
                row_item.append(return_item['returnReason'])
                row_item.append(return_item['returnOrderStatusName'])
                row_item.append(return_item['returnWayTypeName'])
                row_item.append(return_item['warehouseName'])
                row_item.append(','.join(return_item['supplierCodeList']))
                row_item.append(','.join(return_item['skcNameList']))
                row_item.append(return_item['waitReturnQuantity'])
                row_item.append(return_item['returnQuantity'])
                row_item.append(return_item['signTime'])
                row_item.append(return_item['addTime'])
                row_item.append(return_item['expressNoList'])
                row_item.append(return_item['sellerContract'])
                row_item.append(return_item['sellerContractPhone'])
                row_item.append(return_item['returnAddress'])
                return_data.append(row_item)

        sheet_name = f'{last_month}月退货与报废单列表'

        write_data(excel_path_month, sheet_name, return_data, ['O', 'Q'])

        app, wb, sheet = open_excel(excel_path_month, sheet_name)
        set_title_style(sheet, 2)
        set_body_style(sheet, 3)
        add_borders(sheet)
        format_to_datetime(sheet, ['时间'])
        add_sum_for_cell(sheet, ['实际退货/报废总数'])
        sheet.autofit()
        close_excel(app, wb)

        ###############################退供#######################################
        month_data = [[
            '平台SKU', '商家SKU', '属性集', '数量', '单价', '金额', '单价成本', '成本总额', '添加时间', '业务单号',
            '单据号', '变动类型', '结算类型', 'SKC', '供方货号', '供应商名称', '店铺账号', '店铺别名', 'SKU图片',
        ], ['合计', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']]
        log('len(back_list)', len(shein_back_list))
        for month_item in shein_back_list:
            row_item = []
            platform_sku = month_item['sku']
            row_item.append(platform_sku)
            supplier_sku = month_item['supplierSku'] if month_item['supplierSku'] else '-'
            row_item.append(supplier_sku)
            row_item.append(month_item['suffixZh'])
            row_item.append(month_item['quantity'])
            row_item.append(month_item['cost'])
            row_item.append(month_item['amount'])
            row_item.append(month_item['cost_price'])
            row_item.append('')
            row_item.append(month_item['addTime'])
            row_item.append(month_item['businessNo'])
            row_item.append(month_item['billNo'])
            row_item.append(month_item['displayChangeTypeName'])
            row_item.append(month_item['settleTypeName'])
            row_item.append(month_item['skc'])
            row_item.append(month_item['supplierCode'])
            row_item.append(month_item['supplierName'])
            row_item.append(store_username)
            row_item.append(store_name)
            row_item.append(month_item['sku_img'])
            month_data.append(row_item)

        sheet_name = f'{last_month}月退供明细'
        write_dict_to_file_ex(f'{self.config.auto_dir}/shein/cache/sheet_{last_month}_退供列表.json', {store_username: month_data[:1] + month_data[2:]}, [store_username])
        write_data(excel_path_month, sheet_name, sort_by_column(month_data, 2, 2))

        app, wb, sheet = open_excel(excel_path_month, sheet_name)
        set_title_style(sheet, 2)
        set_body_style(sheet, 3)
        add_borders(sheet)
        format_to_money(sheet, ['金额', '单价', '总额'])
        column_to_right(sheet, ['金额', '单价', '总额'])
        format_to_datetime(sheet, ['时间'])
        add_sum_for_cell(sheet, ['数量', '金额', '成本总额'])
        add_formula_for_column(sheet, '成本总额', '=G3*D3', 3)
        hidden_columns(sheet, ['SKU图片'])
        sheet.autofit()
        close_excel(app, wb)

        ###############################不结算#######################################
        month_data = [[
            '平台SKU', '商家SKU', '属性集', '数量', '单价', '金额', '单价成本', '成本总额', '添加时间', '业务单号',
            '单据号', '变动类型', '结算类型', 'SKC', '供方货号', '供应商名称', '店铺账号', '店铺别名', 'SKU图片',
        ], ['合计', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''
            ]]
        log('len(shein_no_settlement_list)', len(shein_no_settlement_list))
        for month_item in shein_no_settlement_list:
            row_item = []
            platform_sku = month_item['sku']
            row_item.append(platform_sku)
            supplier_sku = month_item['supplierSku'] if month_item['supplierSku'] else '-'
            row_item.append(supplier_sku)
            row_item.append(month_item['suffixZh'])
            row_item.append(month_item['quantity'])
            row_item.append(month_item['cost'])
            row_item.append(month_item['amount'])
            row_item.append(month_item['cost_price'])
            row_item.append('')
            row_item.append(month_item['addTime'])
            row_item.append(month_item['businessNo'])
            row_item.append(month_item['billNo'])
            row_item.append(month_item['displayChangeTypeName'])
            row_item.append(month_item['settleTypeName'])
            row_item.append(month_item['skc'])
            row_item.append(month_item['supplierCode'])
            row_item.append(month_item['supplierName'])
            row_item.append(store_username)
            row_item.append(store_name)
            row_item.append(month_item['sku_img'])
            month_data.append(row_item)

        sheet_name = f'{last_month}月不结算明细'

        write_dict_to_file_ex(f'{self.config.auto_dir}/shein/cache/sheet_{last_month}_不结算列表.json', {store_username: month_data[:1] + month_data[2:]}, [store_username])

        write_data(excel_path_month, sheet_name, sort_by_column(month_data, 2, 2))

        app, wb, sheet = open_excel(excel_path_month, sheet_name)
        set_title_style(sheet, 2)
        set_body_style(sheet, 3)
        add_borders(sheet)
        format_to_money(sheet, ['金额', '单价', '总额'])
        column_to_right(sheet, ['金额', '单价', '总额'])
        format_to_datetime(sheet, ['时间'])
        add_sum_for_cell(sheet, ['数量', '金额', '成本总额'])
        add_formula_for_column(sheet, '成本总额', '=G3*D3', 3)
        hidden_columns(sheet, ['SKU图片'])
        sheet.autofit()
        close_excel(app, wb)

        sheet_name = f'{last_month}月利润汇总'
        # 建立利润汇总sheet页
        write_json_to_excel('excel_json_profit_detail.json', excel_path_month, sheet_name)

        # 填入数据 销售数量
        app, wb, sheet = open_excel(excel_path_month, sheet_name)
        delete_sheet_if_exists(wb, 'Sheet1')
        move_sheet_to_position(wb, sheet_name, 1)
        wb.save()
        sheet.activate()

        target_month = find_column_by_data(sheet, 2, last_month)
        sheet.range(f'{target_month}3').value = f"='{last_month}月销售明细'!I2"
        sheet.range(f'{target_month}4').number_format = f"¥#,##0.00;¥-#,##0.00"
        sheet.range(f'{target_month}4').value = f"='{last_month}月销售明细'!J2"
        sheet.range(f'{target_month}5').number_format = f"¥#,##0.00;¥-#,##0.00"
        sheet.range(f'{target_month}5').value = f"='{last_month}月销售明细'!H2"
        sheet.range(f'{target_month}6').number_format = f"¥#,##0.00;¥-#,##0.00"
        # sheet.range(f'{target_month}6').value = f"=-'{last_month}月退货与报废单列表'!L2 * 3"
        sheet.range(f'{target_month}7').number_format = f"¥#,##0.00;¥-#,##0.00"
        sheet.range(f'{target_month}7').value = f"=-'{last_month}月补扣款列表'!H2"
        sheet.range(f'{target_month}8').number_format = f"¥#,##0.00;¥-#,##0.00"
        sheet.range(f'{target_month}9').number_format = f"¥#,##0.00;¥-#,##0.00"
        sheet.range(f'{target_month}9').value = f"=SUM({target_month}5:{target_month}8)"
        sheet.range(f'{target_month}10').number_format = f"¥#,##0.00;¥-#,##0.00"
        sheet.range(f'{target_month}10').value = f"='{last_month}月库存结余'!J2"
        sheet.range('A1').value = f'2025年{last_month}月 shein 利润汇总表 {store_name}'
        sheet.range(f'{target_month}:{target_month}').autofit()
        wb.save()
        close_excel(app, wb)
        WxWorkBot('b30aaa8d-1a1f-4378-841a-8b0f8295f2d9').send_file(excel_path_month)

    def write_summary_algorithm_1(self):
        excel_path = self.config.excel_shein_finance_month_report_summary

        sheet_name = '总表-算法1'
        dict_store = read_dict_from_file(self.config.shein_store_alias)
        total_data = []
        header = ['店铺账号', '店铺别名']
        for mall_id, excel_data in dict_store.items():
            total_data += [[mall_id, excel_data]]

        log(total_data)
        filtered_value = [header] + total_data
        log(filtered_value)
        filtered_value = add_suffixed_column(filtered_value, '店长', '')
        filtered_value = add_suffixed_column(filtered_value, '出库金额', '')
        filtered_value = add_suffixed_column(filtered_value, '出库成本', '')
        filtered_value = add_suffixed_column(filtered_value, '不结算金额', '')
        filtered_value = add_suffixed_column(filtered_value, '不结算成本', '')
        filtered_value = add_suffixed_column(filtered_value, '实际出库金额', '')
        filtered_value = add_suffixed_column(filtered_value, '实际出库成本', '')
        filtered_value = add_suffixed_column(filtered_value, '补扣款', '')
        filtered_value = add_suffixed_column(filtered_value, '线下运费', '')
        filtered_value = add_suffixed_column(filtered_value, '侵权扣款', '')
        filtered_value = add_suffixed_column(filtered_value, '希音仓成本总额', '')
        filtered_value = add_suffixed_column(filtered_value, '毛利', '')

        # 匹配店铺店长
        dict_store_manager_shein = self.config.shein_store_manager
        for row in filtered_value:
            mall_name = row[0]
            if mall_name == '店铺账号':
                continue
            row[2] = dict_store_manager_shein.get(str(mall_name).lower())
        self.write_to_one(filtered_value, excel_path, sheet_name)

    def write_summary_algorithm_2(self):
        excel_path = self.config.excel_shein_finance_month_report_summary

        app, wb, sheet = open_excel(excel_path, 2)

        sheet_name = '总表-算法2'
        # 将目标工作表移动到第一个工作表之前
        sheet.api.Move(Before=wb.sheets[0].api)
        wb.save()
        close_excel(app, wb)

        dict_store = read_dict_from_file(self.config.shein_store_alias)
        total_data = []
        header = ['店铺账号', '店铺别名']
        for mall_id, excel_data in dict_store.items():
            total_data += [[mall_id, excel_data]]

        filtered_value = [header] + total_data
        filtered_value = add_suffixed_column(filtered_value, '店长', '')
        filtered_value = add_suffixed_column(filtered_value, '出库金额', '')
        filtered_value = add_suffixed_column(filtered_value, '出库成本', '')
        filtered_value = add_suffixed_column(filtered_value, '退供金额', '')
        filtered_value = add_suffixed_column(filtered_value, '退供成本', '')
        filtered_value = add_suffixed_column(filtered_value, '实际出库金额', '')
        filtered_value = add_suffixed_column(filtered_value, '实际出库成本', '')
        filtered_value = add_suffixed_column(filtered_value, '补扣款', '')
        filtered_value = add_suffixed_column(filtered_value, '线下运费', '')
        filtered_value = add_suffixed_column(filtered_value, '侵权扣款', '')
        filtered_value = add_suffixed_column(filtered_value, '希音仓成本总额', '')
        filtered_value = add_suffixed_column(filtered_value, '毛利', '')

        # 匹配店铺店长
        dict_store_manager_shein = self.config.shein_store_manager
        for row in filtered_value:
            mall_name = row[0]
            if mall_name == '店铺账号':
                continue
            row[2] = dict_store_manager_shein.get(str(mall_name).lower())
        self.write_to_one(filtered_value, excel_path, sheet_name)
        WxWorkBot('b30aaa8d-1a1f-4378-841a-8b0f8295f2d9').send_file(excel_path)

    def sumary_part(self):
        excel_path = self.config.excel_shein_finance_month_report_summary
        src_directory = f'{self.config.auto_dir}/shein/cache'
        for file in os.listdir(src_directory):
            # 检查是否为文件且符合命名模式
            if file.startswith(f"sheet_{TimeUtils.get_last_month()}") and file.endswith(".json"):
                file_path = os.path.join(src_directory, file)
                filename = os.path.basename(file_path)  # 获取 "tool.py"
                name = os.path.splitext(filename)[0]
                sheet_name = name.split('_')[2]
                dict = read_dict_from_file(file_path)
                total_data = []
                header = []
                for mall_id, excel_data in dict.items():
                    header = excel_data[0]
                    if len(excel_data) > 1:
                        total_data += excel_data[1:]

                filtered_value = [header] + total_data
                self.write_to_one(filtered_value, excel_path, f'{sheet_name}-汇总-{TimeUtils.get_last_month()}月')

    def write_to_one(self, data, excel_path, sheet_name="Sheet1", header_column=None):
        write_data(excel_path, sheet_name, data)
        app, wb, sheet = open_excel(excel_path, sheet_name)
        add_borders(sheet)
        format_to_money(sheet, ['金额', '成本'])
        format_to_datetime(sheet, ['时间'])
        if '库存结余' in sheet_name:
            format_to_percent(sheet, ['利润率'])
            format_to_month(sheet, ['月份'])
            add_formula_for_column(sheet, '出库成本总额', f'=IF(ISNUMBER(O2),K2*O2,0)', 2)
            add_formula_for_column(sheet, '希音仓成本总额', f'=IF(ISNUMBER(O2),M2*O2,0)', 2)
            add_formula_for_column(sheet, '出库利润', f'=L2-P2', 2)
            add_formula_for_column(sheet, '出库利润率', f'=IF(L2 > 0,R2/L2,0)', 2)
        if '退供列表' in sheet_name:
            add_formula_for_column(sheet, '成本总额', f'=IF(ISNUMBER(G2),D2*G2,0)', 2)
        if '不结算列表' in sheet_name:
            add_formula_for_column(sheet, '成本总额', f'=IF(ISNUMBER(G2),D2*G2,0)', 2)
        if '总表-算法1' in sheet_name:
            format_to_money(sheet, ['补扣款', '线下运费', '侵权扣款', '毛利'])
            add_formula_for_column(sheet, '出库金额',
                                   f"=SUMIF('库存结余-汇总-{TimeUtils.get_last_month()}月'!U:U,'总表-算法1'!A:A,'库存结余-汇总-{TimeUtils.get_last_month()}月'!L:L)",
                                   2)
            add_formula_for_column(sheet, '出库成本',
                                   f"=SUMIF('库存结余-汇总-{TimeUtils.get_last_month()}月'!U:U,'总表-算法1'!A:A,'库存结余-汇总-{TimeUtils.get_last_month()}月'!P:P)",
                                   2)
            add_formula_for_column(sheet, '不结算金额',
                                   f"=SUMIF('不结算列表-汇总-{TimeUtils.get_last_month()}月'!Q:Q,'总表-算法1'!A:A,'不结算列表-汇总-{TimeUtils.get_last_month()}月'!F:F)",
                                   2)
            add_formula_for_column(sheet, '不结算成本',
                                   f"=SUMIF('不结算列表-汇总-{TimeUtils.get_last_month()}月'!Q:Q,'总表-算法1'!A:A,'不结算列表-汇总-{TimeUtils.get_last_month()}月'!H:H)",
                                   2)
            add_formula_for_column(sheet, '实际出库金额', f"=D2-F2", 2)
            add_formula_for_column(sheet, '实际出库成本', f"=E2-G2", 2)
            add_formula_for_column(sheet, '补扣款',
                                   f"=SUMIF('补扣款列表-汇总-{TimeUtils.get_last_month()}月'!W:W,'总表-算法1'!A:A,'补扣款列表-汇总-{TimeUtils.get_last_month()}月'!H:H)",
                                   2)
            add_formula_for_column(sheet, '希音仓成本总额',
                                   f"=SUMIF('库存结余-汇总-{TimeUtils.get_last_month()}月'!U:U,'总表-算法1'!A:A,'库存结余-汇总-{TimeUtils.get_last_month()}月'!Q:Q)",
                                   2)
            add_formula_for_column(sheet, '毛利', f"=H2-I2-J2-K2-L2", 2)
            # 全是公式 无法排序

        if '总表-算法2' in sheet_name:
            format_to_money(sheet, ['补扣款', '线下运费', '侵权扣款', '毛利'])
            add_formula_for_column(sheet, '出库金额',
                                   f"=SUMIF('库存结余-汇总-{TimeUtils.get_last_month()}月'!U:U,'总表-算法1'!A:A,'库存结余-汇总-{TimeUtils.get_last_month()}月'!L:L)",
                                   2)
            add_formula_for_column(sheet, '出库成本',
                                   f"=SUMIF('库存结余-汇总-{TimeUtils.get_last_month()}月'!U:U,'总表-算法1'!A:A,'库存结余-汇总-{TimeUtils.get_last_month()}月'!P:P)",
                                   2)
            add_formula_for_column(sheet, '退供金额',
                                   f"=SUMIF('退供列表-汇总-{TimeUtils.get_last_month()}月'!Q:Q,'总表-算法1'!A:A,'退供列表-汇总-{TimeUtils.get_last_month()}月'!F:F)",
                                   2)
            add_formula_for_column(sheet, '退供成本',
                                   f"=SUMIF('退供列表-汇总-{TimeUtils.get_last_month()}月'!Q:Q,'总表-算法1'!A:A,'退供列表-汇总-{TimeUtils.get_last_month()}月'!H:H)",
                                   2)
            add_formula_for_column(sheet, '实际出库金额', f"=D2-F2", 2)
            add_formula_for_column(sheet, '实际出库成本', f"=E2-G2", 2)
            add_formula_for_column(sheet, '补扣款',
                                   f"=SUMIF('补扣款列表-汇总-{TimeUtils.get_last_month()}月'!W:W,'总表-算法1'!A:A,'补扣款列表-汇总-{TimeUtils.get_last_month()}月'!H:H)",
                                   2)
            add_formula_for_column(sheet, '希音仓成本总额',
                                   f"=SUMIF('库存结余-汇总-{TimeUtils.get_last_month()}月'!U:U,'总表-算法1'!A:A,'库存结余-汇总-{TimeUtils.get_last_month()}月'!Q:Q)",
                                   2)
            add_formula_for_column(sheet, '毛利', f"=H2-I2-J2-K2-L2", 2)

            move_sheet_to_position(wb, '总表-算法1', 1)
            move_sheet_to_position(wb, '总表-算法2', 1)

        set_title_style(sheet, 1)
        wb.save()
        close_excel(app, wb)

    def format_funds(self, sheet):
        beautify_title(sheet)
        column_to_right(sheet, ['金额', '汇总'])
        format_to_money(sheet, ['金额', '汇总'])
        add_sum_for_cell(sheet, ['在途商品金额', '在仓商品金额', '待结算金额', '可提现金额', '销售出库金额', '汇总'])
        add_formula_for_column(sheet, '汇总', '=SUM(D3:G3)', 3)
        sheet.autofit()

    def format_bad_comment(self, sheet):
        beautify_title(sheet)
        column_to_left(sheet, ['商品信息'])
        autofit_column(sheet, ['买家评价', '时间信息', '标签关键词'])
        specify_column_width(sheet, ['买家评价', '商品信息'], 150 / 6)
        color_for_column(sheet, ['买家评分'], '红色')
        colorize_by_field(sheet, 'skc')
        add_borders(sheet)
        InsertImageV2(sheet, ['商品图片', '图1', '图2', '图3', '图4', '图5'])

    def write_bad_comment(self):
        excel_path = create_file_path(self.config.excel_bad_comment)
        header = ['评价ID', '商品图片', '商品信息', '买家评分', '买家评价', '标签关键词', '区域', '时间信息', '有图', '图1',
                  '图2', '图3', '图4', '图5', 'skc']
        summary_excel_data = [header]

        cache_file = f'{self.config.auto_dir}/shein/dict/comment_list_{TimeUtils.today_date()}.json'
        dict = read_dict_from_file(cache_file)
        dict_store = read_dict_from_file(self.config.shein_store_alias)

        for store_username, comment_list in dict.items():
            store_name = dict_store.get(store_username)
            sheet_name = store_name

            store_excel_data = [header]
            for comment in comment_list:
                row_item = []
                row_item.append(f'{comment['commentId']}\n{store_name}')
                row_item.append(comment['goodsThumb'])
                product_info = f'属性:{comment["goodsAttribute"]}\n货号:{comment["goodSn"]}\nSPU:{comment["spu"]}\nSKC:{comment["skc"]}\nSKU:{comment["sku"]}'
                row_item.append(product_info)
                row_item.append(calculate_star_symbols(comment['goodsCommentStar']))
                row_item.append(comment['goodsCommentContent'])
                qualityLabel = '存在质量问题\n' if comment['isQualityLabel'] == 1 else ''
                bad_comment_label = qualityLabel + '\n'.join([item['labelName'] for item in comment['badCommentLabelList']])

                row_item.append(bad_comment_label)
                row_item.append(comment['dataCenterName'])
                time_info = f'下单时间:{comment["orderTime"]}\n评论时间:{comment["commentTime"]}'
                row_item.append(time_info)

                # 获取图片数量
                image_num = len(comment.get('goodsCommentImages', []))
                # 设置imgFlag值（如果comment中没有imgFlag字段，默认设为0）
                imgFlag = image_num if comment.get('imgFlag') == 1 else 0
                row_item.append(imgFlag)

                images = comment.get('goodsCommentImages', [])
                for i in range(5):
                    row_item.append(images[i] if i < len(images) else '')

                row_item.append(comment['skc'])

                store_excel_data.append(row_item)
                summary_excel_data.append(row_item)

            # write_data(excel_path, sheet_name, store_excel_data)
            # format_bad_comment(excel_path, sheet_name)

        sheet_name = 'Sheet1'

        batch_excel_operations(excel_path, [
            (sheet_name, 'write', summary_excel_data),
            (sheet_name, 'format', self.format_bad_comment),
        ])

    def write_funds(self):
        cache_file = f'{self.config.auto_dir}/shein/cache/stat_fund_{TimeUtils.today_date()}.json'
        dict = read_dict_from_file(cache_file)
        data = []
        for key, val in dict.items():
            data.append(val)

        excel_path = create_file_path(self.config.excel_shein_fund)
        sheet_name = 'Sheet1'
        data.insert(0, ['汇总', '', '', '', '', '', '', '', '', ''])
        data.insert(0, ['店铺名称', '店铺账号', '店长', '在途商品金额', '在仓商品金额', '待结算金额', '可提现金额',
                        '销售出库金额', '汇总', '导出时间'])
        batch_excel_operations(excel_path, [
            ('Sheet1', 'write', sort_by_column(data, 7, 2)),
            ('Sheet1', 'format', self.format_funds),
        ])
        WxWorkBot('b30aaa8d-1a1f-4378-841a-8b0f8295f2d9').send_file(excel_path)

    def format_skc_quality(self, sheet):
        beautify_title(sheet)
        colorize_by_field(sheet, 'skc')
        add_borders(sheet)
        InsertImageV2(sheet, ['商品图片'])

    def sort_site_desc_by_sale_cnt_14d(self, data, reverse=True):
        """
       对data中的site_desc_vo_list按照skc_site_sale_cnt_14d进行排序

       参数:
           data: 包含site_desc_vo_list的字典
           reverse: 是否倒序排序，默认为True（从大到小）

       返回:
           排序后的data（原数据会被修改）
       """
        if 'site_desc_vo_list' in data and isinstance(data['site_desc_vo_list'], list):
            # 处理None值，将它们放在排序结果的最后
            data['site_desc_vo_list'].sort(
                key=lambda x: float('-inf') if x.get('skc_site_sale_cnt_14d') is None else x['skc_site_sale_cnt_14d'],
                reverse=reverse
            )
        return data

    def write_skc_quality_estimate(self):
        excel_path = create_file_path(self.config.excel_skc_quality_estimate)
        header = ['店铺信息', '商品图片', '统计日期', '国家', '当日销量', '14日销量', '14日销量占比', '质量等级',
                  '客评数/客评分', '差评数/差评率', '退货数/退货率', 'skc', 'skc当日销量', 'skc14日销量', 'skc14日销量占比']
        summary_excel_data = [header]

        stat_date = TimeUtils.before_yesterday()
        cache_file = f'{self.config.auto_dir}/shein/dict/googs_estimate_{stat_date}.json'
        dict = read_dict_from_file(cache_file)
        if len(dict) == 0:
            log('昨日质量评估数据不存在')
            return

        dict_store = read_dict_from_file(self.config.shein_store_alias)

        operations = []
        for store_username, skc_list in dict.items():
            store_name = dict_store.get(store_username)
            sheet_name = store_name

            store_excel_data = [header]
            for skc_item in skc_list:
                sorted_skc_item = self.sort_site_desc_by_sale_cnt_14d(skc_item, True)
                # for site in sorted_skc_item['site_desc_vo_list']:
                #     print(f"{site['country_site']}: {site['skc_site_sale_cnt_14d']}")
                # continue
                store_info = f'{store_name}'
                skc = sorted_skc_item['skc']
                sites = sorted_skc_item['site_desc_vo_list']
                skc_sale_cnt = sorted_skc_item['skc_sale_cnt']
                skc_sale_cnt_14d = sorted_skc_item['skc_sale_cnt_14d']
                skc_sale_rate_14d = sorted_skc_item['skc_sale_rate_14d']
                for site in sites:
                    row_item = []
                    row_item.append(store_info)
                    row_item.append(skc_item['goods_image'])
                    row_item.append(stat_date)
                    row_item.append(site['country_site'])
                    row_item.append(site['skc_site_sale_cnt'])
                    cnt_14d = site['skc_site_sale_cnt_14d']
                    if cnt_14d is None or cnt_14d <= 0:
                        continue
                    row_item.append(cnt_14d)
                    row_item.append(site['skc_site_sale_rate_14d'])
                    row_item.append(site['quality_level'])
                    customer_info = f'{site["customer_evaluate_num"]}/{site["customer_evaluate_score"][:-1]}'
                    row_item.append(customer_info)
                    negative_info = f'{site["negative_quantity"]}/{site["negative_percent"]}'
                    row_item.append(negative_info)
                    return_info = f'{site["goods_return_quantity"]}/{site["goods_return_percent"]}'
                    row_item.append(return_info)
                    row_item.append(skc)
                    row_item.append(skc_sale_cnt)
                    row_item.append(skc_sale_cnt_14d)
                    row_item.append(skc_sale_rate_14d)
                    store_excel_data.append(row_item)
                    summary_excel_data.append(row_item)

            operations.append((
                sheet_name, 'write', store_excel_data
            ))
            operations.append((
                sheet_name, 'format', self.format_skc_quality
            ))
        operations.append((
            'Sheet1', 'delete'
        ))
        batch_excel_operations(excel_path, operations)

    # 添加月度sheet操作 - 自定义操作函数
    def write_monthly_data(self, sheet, data, name):
        # 写入数据到A5位置（月度数据从A列开始）
        sheet.range('A5').value = data
        # 设置标题
        sheet.range('A1').value = f'{name}SHEIN{TimeUtils.get_current_month()}月店铺数据'

    def write_sales_data(self):
        yesterday = TimeUtils.get_yesterday()
        model = SheinStoreSalesDetailManager(self.config.database_url)
        records = model.get_one_day_records(yesterday, SheinStoreSalesDetail.sales_amount.desc())
        data_day = []
        dict_store_manager_shein = self.config.shein_store_manager
        dict_store_name = read_dict_from_file(self.config.shein_store_alias)

        # 准备每日汇总数据
        for record in records:
            store_data = []
            store_data.append(dict_store_name.get(record.store_username))
            store_data.append(dict_store_manager_shein.get(str(record.store_username).lower(), '-'))
            store_data.append(record.sales_num)
            store_data.append(record.sales_num_inc)
            store_data.append(record.sales_amount)
            store_data.append(record.sales_amount_inc)
            store_data.append(record.visitor_num)
            store_data.append(record.visitor_num_inc)
            store_data.append(record.bak_A_num)
            store_data.append(record.bak_A_num_inc)
            store_data.append(record.new_A_num)
            store_data.append(record.new_A_num_inc)
            store_data.append(record.on_sales_product_num)
            store_data.append(record.on_sales_product_num_inc)
            store_data.append(record.wait_shelf_product_num)
            store_data.append(record.wait_shelf_product_num_inc)
            store_data.append(record.upload_product_num)
            store_data.append(record.upload_product_num_inc)
            store_data.append(record.sold_out_product_num)
            store_data.append(record.shelf_off_product_num)
            data_day.append(store_data)

        excel_path = create_file_path(self.config.excel_daily_report)
        delete_file(excel_path)
        sheet_name_first = 'SHEIN销售部每日店铺情况'

        # 准备批量操作列表
        base_operations = []

        # 添加每日汇总sheet的操作 - 自定义操作函数
        def write_daily_data(sheet):
            # 写入数据到B5位置，保持原有格式
            sheet.range('B5').value = data_day
            # 设置标题
            sheet.range('A1').value = f'销售部SHEIN{TimeUtils.get_current_month()}月店铺数据'
            # 设置日期和合并
            sheet.range('A4').value = f'{TimeUtils.format_date_cross_platform(yesterday)}\n({TimeUtils.get_chinese_weekday(yesterday)})'

        base_operations.append((sheet_name_first, 'format', write_daily_data))
        base_operations.append((sheet_name_first, 'format', self._format_daily_summary_sheet, yesterday, len(data_day)))
        base_operations.append((sheet_name_first, 'move', 1))
        base_operations.append(('Sheet1', 'delete'))

        # 获取店铺列表并准备月度数据
        store_list = model.get_distinct_store_sales_list()

        # 准备所有店铺的数据
        store_operations_data = []
        for store in store_list:
            store_username = store[0]
            store_name = dict_store_name.get(store_username)
            records = model.get_one_month_records(TimeUtils.get_current_year(), TimeUtils.get_current_month(), store_username)

            data_month = []
            for record in records:
                store_data = []
                store_data.append(record.day)
                store_data.append(record.sales_num)
                store_data.append(record.sales_num_inc)
                store_data.append(record.sales_amount)
                store_data.append(record.sales_amount_inc)
                store_data.append(record.visitor_num)
                store_data.append(record.visitor_num_inc)
                store_data.append(record.bak_A_num)
                store_data.append(record.bak_A_num_inc)
                store_data.append(record.new_A_num)
                store_data.append(record.new_A_num_inc)
                store_data.append(record.on_sales_product_num)
                store_data.append(record.on_sales_product_num_inc)
                store_data.append(record.wait_shelf_product_num)
                store_data.append(record.wait_shelf_product_num_inc)
                store_data.append(record.upload_product_num)
                store_data.append(record.upload_product_num_inc)
                store_data.append(record.sold_out_product_num)
                store_data.append(record.shelf_off_product_num)
                # store_data.append(record.remark)  # 月度数据不包含备注列，保持19列
                data_month.append(store_data)

            store_operations_data.append((store_name, data_month))

        # 构建所有操作列表
        operations = base_operations.copy()

        # 添加店铺操作
        for store_name, data_month in store_operations_data:
            # 清理店铺名称
            clean_store_name = self._clean_sheet_name(store_name)
            operations.append((clean_store_name, 'format', self.write_monthly_data, data_month, clean_store_name))
            operations.append((clean_store_name, 'format', self._format_store_monthly_sheet, clean_store_name, len(data_month)))

        # 添加最后激活操作
        operations.append((sheet_name_first, 'active'))

        # 执行批量操作（内部会自动分批处理）
        success = batch_excel_operations(excel_path, operations)

        if success:
            # 发送文件到企业微信
            WxWorkBot('b30aaa8d-1a1f-4378-841a-8b0f8295f2d9').send_file(excel_path)
            log(f"销售数据写入完成: {excel_path}")
        else:
            log(f"销售数据写入失败: {excel_path}")

    def _clean_sheet_name(self, name):
        """
        清理工作表名称，移除Excel不支持的字符
        """
        if not name:
            return "DefaultSheet"

        # Excel工作表名称限制：不能包含 [ ] : * ? / \ 字符，且长度不超过31字符
        invalid_chars = ['[', ']', ':', '*', '?', '/', '\\']
        clean_name = name

        for char in invalid_chars:
            clean_name = clean_name.replace(char, '_')

        # 限制长度为31字符
        if len(clean_name) > 31:
            clean_name = clean_name[:28] + "..."

        # 确保不为空
        if not clean_name.strip():
            clean_name = "Sheet"

        return clean_name

    def _format_daily_summary_sheet(self, sheet, yesterday, data_length):
        """格式化每日汇总sheet"""
        las_row = data_length + 4  # 数据从第5行开始，4行header

        # 设置数据区域格式（从B5开始，因为数据写入到B5）
        sheet.range(f'B5:U{las_row}').api.Font.Color = 0x000000
        sheet.range(f'B5:U{las_row}').api.Font.Bold = False

        # 设置A4日期列的格式和合并
        sheet.range('A4').column_width = 16
        sheet.range('A4').api.VerticalAlignment = -4160  # 垂直顶部对齐
        sheet.range(f'A4:A{las_row}').merge()

        # 设置负数为红色（E,G,I,K列）
        self._set_negative_numbers_red(sheet, ['E', 'G', 'I', 'K'], 5, las_row)

        # 格式化表头
        self._format_daily_header(sheet, las_row)

        # 设置汇总公式和格式
        self._set_summary_formulas(sheet, las_row)

        # 设置边框
        self._set_borders(sheet, f'A2:U{las_row}')

        sheet.autofit()

    def _format_store_monthly_sheet(self, sheet, store_name, data_length):
        """格式化店铺月度sheet"""
        las_row = data_length + 4  # 数据从第5行开始，4行header

        # 数据已经写入，现在进行格式化
        # 设置数据区域格式（从A5开始到S列，月度数据是19列）
        sheet.range(f'A5:S{las_row}').api.Font.Color = 0x000000
        sheet.range(f'A5:S{las_row}').api.Font.Bold = False

        # 格式化表头
        self._format_monthly_header(sheet, las_row)

        # 设置汇总公式和格式
        self._set_monthly_summary_formulas(sheet, las_row)

        # 设置边框
        self._set_borders(sheet, f'A2:S{las_row}')

        sheet.autofit()

    def _set_negative_numbers_red(self, sheet, columns, start_row, end_row):
        """设置负数为红色"""
        for col in columns:
            column_range = sheet.range(f'{col}{start_row}:{col}{end_row}')
            for cell in column_range:
                if cell.value is not None and cell.value < 0:
                    cell.font.color = (255, 0, 0)

    def _format_daily_header(self, sheet, las_row):
        """格式化每日汇总表头，完全按照原始格式"""
        # 第一行：标题
        range_one = f'A1:U1'
        sheet.range(range_one).merge()
        sheet.range(range_one).api.Font.Size = 24
        sheet.range(range_one).api.Font.Bold = True
        sheet.range(range_one).api.HorizontalAlignment = -4108
        sheet.range(range_one).api.VerticalAlignment = -4108

        # 第二行：分类标题
        range_two_part_1 = f'A2:C2'
        range_two_part_2 = f'D2:O2'
        range_two_part_3 = f'P2:U2'
        sheet.range(range_two_part_1).merge()
        sheet.range(range_two_part_2).merge()
        sheet.range(range_two_part_3).merge()

        sheet.range(f'A2:C3').color = 0x47a100

        sheet.range('D2').value = '店铺的结果和稳定性'
        sheet.range(range_two_part_2).api.Font.Size = 16
        sheet.range(range_two_part_2).api.Font.Color = 0xFFFFFF
        sheet.range(range_two_part_2).api.Font.Bold = True
        sheet.range(range_two_part_2).api.HorizontalAlignment = -4108
        sheet.range(range_two_part_2).api.VerticalAlignment = -4108
        sheet.range(f'D2:O3').color = 0x0000FF

        sheet.range('P2').value = '上新的质量和数量'
        sheet.range(range_two_part_3).api.Font.Size = 16
        sheet.range(range_two_part_3).api.Font.Color = 0xFFFFFF
        sheet.range(range_two_part_3).api.Font.Bold = True
        sheet.range(range_two_part_3).api.HorizontalAlignment = -4108
        sheet.range(range_two_part_3).api.VerticalAlignment = -4108
        sheet.range(f'P2:U3').color = 0x47a100

        # 第三行：列标题
        range_three = f'A3:U3'
        sheet.range('A3').value = ['日期', '店铺', '店长', '昨日单量', '对比前日', '昨日销售额', '对比前日', '昨日访客',
                                   '对比前天', '备货款A', '对比前日', '新款A', '对比前日', '在售商品', '对比前日', '待上架',
                                   '对比前日', '昨日上传', '对比前日', '已售罄', '已下架']
        sheet.range(range_three).api.Font.Size = 11
        sheet.range(range_three).api.Font.Color = 0xFFFFFF
        sheet.range(range_three).api.Font.Bold = True
        sheet.range(range_three).api.HorizontalAlignment = -4108
        sheet.range(range_three).api.VerticalAlignment = -4108

        # 第四行：汇总行
        range_four = f'B4:U4'
        sheet.range('B4').value = '汇总'
        sheet.range('C4').value = '-'
        sheet.range(range_four).api.Font.Size = 11
        sheet.range(range_four).api.HorizontalAlignment = -4108
        sheet.range(range_four).api.VerticalAlignment = -4108
        sheet.range(f'B4:U4').color = 0x50d092

    def _format_monthly_header(self, sheet, las_row):
        """格式化月度表头，完全按照原始格式"""
        # 第一行：标题（合并A1:S1）
        range_one = f'A1:S1'
        sheet.range(range_one).merge()
        sheet.range(range_one).api.Font.Size = 24
        sheet.range(range_one).api.Font.Bold = True
        sheet.range(range_one).api.HorizontalAlignment = -4108
        sheet.range(range_one).api.VerticalAlignment = -4108

        # 第二行：分类标题
        range_two_part_1 = f'A2'
        range_two_part_2 = f'B2:M2'
        range_two_part_3 = f'N2:S2'
        sheet.range(range_two_part_2).merge()
        sheet.range(range_two_part_3).merge()

        sheet.range(f'A2:A3').color = 0x47a100

        sheet.range('B2').value = '店铺的结果和稳定性'
        sheet.range(range_two_part_2).api.Font.Size = 16
        sheet.range(range_two_part_2).api.Font.Color = 0xFFFFFF
        sheet.range(range_two_part_2).api.Font.Bold = True
        sheet.range(range_two_part_2).api.HorizontalAlignment = -4108
        sheet.range(range_two_part_2).api.VerticalAlignment = -4108
        sheet.range(f'B2:M3').color = 0x0000FF

        sheet.range('N2').value = '上新的质量和数量'
        sheet.range(range_two_part_3).api.Font.Size = 16
        sheet.range(range_two_part_3).api.Font.Color = 0xFFFFFF
        sheet.range(range_two_part_3).api.Font.Bold = True
        sheet.range(range_two_part_3).api.HorizontalAlignment = -4108
        sheet.range(range_two_part_3).api.VerticalAlignment = -4108
        sheet.range(f'N2:S3').color = 0x47a100

        # 第三行：列标题
        range_three = f'A3:S3'
        sheet.range('A3').value = ['日期', '昨日单量', '对比前日', '昨日销售额', '对比前日', '昨日访客', '对比前天',
                                   '备货款A', '对比前日', '新款A', '对比前日', '在售商品', '对比前日', '待上架',
                                   '对比前日', '昨日上传', '对比前日', '已售罄', '已下架']
        sheet.range(range_three).api.Font.Size = 11
        sheet.range(range_three).api.Font.Color = 0xFFFFFF
        sheet.range(range_three).api.Font.Bold = True
        sheet.range(range_three).api.HorizontalAlignment = -4108
        sheet.range(range_three).api.VerticalAlignment = -4108

        # 第四行：汇总行
        range_four = f'A4:S4'
        sheet.range('A4').value = '汇总'
        sheet.range(range_four).api.Font.Size = 11
        sheet.range(range_four).api.HorizontalAlignment = -4108
        sheet.range(range_four).api.VerticalAlignment = -4108
        sheet.range(f'A4:S4').color = 0x50d092

    def _set_summary_formulas(self, sheet, las_row):
        """设置汇总公式"""
        for col in range(2, 22):  # B列到U列（跳过A列日期）
            col_letter = xw.utils.col_name(col)
            if col_letter not in ['A', 'B', 'C']:  # A列是日期，B列是汇总，C列是-
                sheet.range(f'{col_letter}4').formula = f'=SUM({col_letter}5:{col_letter}{las_row})'
            # 所有列水平居中和垂直居中
            sheet.range(f'{col_letter}:{col_letter}').api.HorizontalAlignment = -4108
            sheet.range(f'{col_letter}:{col_letter}').api.VerticalAlignment = -4108

    def _set_monthly_summary_formulas(self, sheet, las_row):
        """设置月度汇总公式"""
        for col in range(2, 20):  # B列到S列（对应原始代码的 2 到 20）
            col_letter = xw.utils.col_name(col)
            # 所有列水平居中和垂直居中
            sheet.range(f'{col_letter}:{col_letter}').api.HorizontalAlignment = -4108
            sheet.range(f'{col_letter}:{col_letter}').api.VerticalAlignment = -4108
            # 设置汇总公式（原始代码使用固定的36行）
            sheet.range(f'{col_letter}4').formula = f'=SUM({col_letter}5:{col_letter}36)'

    def _set_borders(self, sheet, range_str):
        """设置边框"""
        range_to_border = sheet.range(range_str)
        # 设置外部边框
        range_to_border.api.Borders(7).LineStyle = 1  # 上边框
        range_to_border.api.Borders(8).LineStyle = 1  # 下边框
        range_to_border.api.Borders(9).LineStyle = 1  # 左边框
        range_to_border.api.Borders(10).LineStyle = 1  # 右边框
        # 设置内部边框
        range_to_border.api.Borders(1).LineStyle = 1  # 内部上边框
        range_to_border.api.Borders(2).LineStyle = 1  # 内部下边框
        range_to_border.api.Borders(3).LineStyle = 1  # 内部左边框
        range_to_border.api.Borders(4).LineStyle = 1  # 内部右边框

    def format_bak_advice(self, excel_path, sheet_name, mode):
        app, wb, sheet = open_excel(excel_path, sheet_name)
        beautify_title(sheet)
        add_borders(sheet)
        column_to_left(sheet,
                       ["商品信息", "备货建议", "近7天SKU销量/SKC销量/SKC曝光", "SKC点击率/SKC转化率",
                        "自主参与活动"])
        autofit_column(sheet, ['店铺名称', '商品信息', '备货建议', "近7天SKU销量/SKC销量/SKC曝光",
                               "SKC点击率/SKC转化率",
                               "自主参与活动"])

        if mode in [2, 5, 6, 7, 8, 9, 10]:
            format_to_number(sheet, ['本地和采购可售天数'], 1)
            add_formula_for_column(sheet, '本地和采购可售天数', '=IF(H2>0, (F2+G2)/H2,0)')
            add_formula_for_column(sheet, '建议采购', '=IF(I2 > J2,0,E2)')

        colorize_by_field(sheet, 'SKC')
        specify_column_width(sheet, ['商品信息'], 180 / 6)
        InsertImageV2(sheet, ['SKC图片', 'SKU图片'])
        wb.save()
        close_excel(app, wb)
        if mode == 4:
            WxWorkBot('b30aaa8d-1a1f-4378-841a-8b0f8295f2d9').send_file(excel_path)

    def write_bak_advice(self, mode_list):
        excel_path_list = [
            [1, self.config.Excel_Bak_Advise],
            [2, self.config.Excel_Purchase_Advise2],
            [3, self.config.Excel_Product_On_Shelf_Yesterday],
            [4, f'{self.config.auto_dir}/shein/昨日出单/昨日出单(#len#)_#store_name#_{TimeUtils.today_date()}.xlsx'],
            [5, self.config.Excel_Purchase_Advise],
            [6, self.config.Excel_Purchase_Advise6],
            [7, self.config.Excel_Purchase_Advise7],
            [8, self.config.Excel_Purchase_Advise8],
            [9, self.config.Excel_Purchase_Advise9],
            [10, self.config.Excel_Purchase_Advise10],
        ]
        mode_excel_path_list = [row for row in excel_path_list if row[0] in mode_list]
        new_excel_path_list = []
        for mode, excel_path in mode_excel_path_list:
            summary_excel_data = []
            cache_file = f'{self.config.auto_dir}/shein/cache/bak_advice_{mode}_{TimeUtils.today_date()}.json'
            dict = read_dict_from_file(cache_file)
            header = []
            new_excel_path = excel_path
            for store_name, excel_data in dict.items():
                sheet_name = store_name
                # 处理每个店铺的数据

                if mode in [2, 4]:
                    new_excel_path = str(excel_path).replace('#len#', str(len(excel_data[1:])))
                    new_excel_path = new_excel_path.replace('#store_name#', store_name)
                    new_excel_path_list.append(new_excel_path)
                    sheet_name = 'Sheet1'

                    log(new_excel_path)
                    if mode in [2]:
                        excel_data = sort_by_column(excel_data, 4, 1)
                    write_data(new_excel_path, sheet_name, excel_data)
                    self.format_bak_advice(new_excel_path, sheet_name, mode)

                # 是否合并表格数据
                if mode in [1, 3]:
                    header = excel_data[0]
                    summary_excel_data += excel_data[1:]

            if mode in [1, 3]:
                sheet_name = 'Sheet1'
                write_data(new_excel_path, sheet_name, [header] + summary_excel_data)
                self.format_bak_advice(new_excel_path, sheet_name, mode)

        return new_excel_path_list

    def write_activity_list(self):
        cache_file = f'{self.config.auto_dir}/shein/activity_list/activity_list_{TimeUtils.today_date()}.json'
        dict_activity = read_dict_from_file(cache_file)
        all_data = []
        header = []
        for store_username, excel_data in dict_activity.items():
            header = excel_data[:1]
            all_data += excel_data[1:]

        all_data = header + all_data

        excel_path = create_file_path(self.config.excel_activity_list)
        sheet_name = 'Sheet1'
        write_data(excel_path, sheet_name, all_data)
        self.format_activity_list(excel_path, sheet_name)

    def format_activity_list(self, excel_path, sheet_name):
        app, wb, sheet = open_excel(excel_path, sheet_name)
        beautify_title(sheet)
        add_borders(sheet)
        column_to_left(sheet, ['活动信息'])
        colorize_by_field(sheet, '店铺名称')
        autofit_column(sheet, ['店铺名称', '活动信息'])
        wb.save()
        close_excel(app, wb)

    def write_jit_data(self):
        excel_path_1 = create_file_path(self.config.Excel_Order_Type_1)
        summary_excel_data_1 = []

        cache_file_1 = f'{self.config.auto_dir}/shein/cache/jit_{TimeUtils.today_date()}_1_{TimeUtils.get_period()}.json'
        dict_1 = read_dict_from_file(cache_file_1)
        dict_store = read_dict_from_file(f'{self.config.auto_dir}/shein_store_alias.json')

        header = []
        for store_username, excel_data in dict_1.items():
            # store_name = dict_store.get(store_username)
            # sheet_name = store_name
            # write_data(excel_path_1, sheet_name, excel_data)
            # self.format_jit(excel_path_1, sheet_name)
            header = excel_data[0]
            summary_excel_data_1 += excel_data[1:]

        if len(summary_excel_data_1) > 0:
            sheet_name = 'Sheet1'
            write_data(excel_path_1, sheet_name, [header] + summary_excel_data_1)
            self.format_jit(excel_path_1, sheet_name)

        excel_path_2 = create_file_path(self.config.Excel_Order_Type_2)
        summary_excel_data_2 = []

        cache_file_2 = f'{self.config.auto_dir}/shein/cache/jit_{TimeUtils.today_date()}_2_{TimeUtils.get_period()}.json'
        dict_2 = read_dict_from_file(cache_file_2)

        header = []
        for store_username, excel_data in dict_2.items():
            # store_name = dict_store.get(store_username)
            # sheet_name = store_name
            # write_data(excel_path_2, sheet_name, excel_data)
            # self.format_jit(excel_path_2, sheet_name)
            header = excel_data[0]
            summary_excel_data_2 += excel_data[1:]

        if len(summary_excel_data_2) > 0:
            sheet_name = 'Sheet1'
            write_data(excel_path_2, sheet_name, [header] + summary_excel_data_2)
            self.format_jit(excel_path_2, sheet_name)

    def format_jit(self, excel_path, sheet_name):
        app, wb, sheet = open_excel(excel_path, sheet_name)
        beautify_title(sheet)
        add_borders(sheet)
        colorize_by_field(sheet, 'SKC')
        column_to_left(sheet, ["商品信息", "近7天SKU销量/SKC销量/SKC曝光", "SKC点击率/SKC转化率", "自主参与活动"])
        autofit_column(sheet,
                       ['店铺名称', '商品信息', "近7天SKU销量/SKC销量/SKC曝光", "SKC点击率/SKC转化率", "自主参与活动"])
        InsertImageV2(sheet, ['SKC图片', 'SKU图片'])
        wb.save()
        close_excel(app, wb)
        WxWorkBot('b30aaa8d-1a1f-4378-841a-8b0f8295f2d9').send_file(excel_path)

    def write_week_report(self):
        excel_path = create_file_path(self.config.excel_week_sales_report)
        log(excel_path)

        cache_file = f'{self.config.auto_dir}/shein/cache/week_sales_{TimeUtils.today_date()}.json'
        dict = read_dict_from_file(cache_file)

        summary_excel_data = []
        header = []
        for store_name, excel_data in dict.items():
            # sheet_name = store_name
            # write_data(excel_path, sheet_name, excel_data)
            # self.format_week_report(excel_path, sheet_name)
            header = excel_data[0]
            summary_excel_data += excel_data[1:]
        summary_excel_data = [header] + summary_excel_data
        sheet_name = 'Sheet1'
        write_data(excel_path, sheet_name, summary_excel_data)
        self.format_week_report(excel_path, sheet_name)

    def format_week_report(self, excel_path, sheet_name):
        app, wb, sheet = open_excel(excel_path, sheet_name)
        beautify_title(sheet)
        column_to_left(sheet, ['商品信息'])
        format_to_money(sheet, ['申报价', '成本价', '毛利润', '利润'])
        format_to_percent(sheet, ['支付率', '点击率', '毛利率'])
        self.dealFormula(sheet)  # 有空再封装优化
        colorize_by_field(sheet, 'SPU')
        autofit_column(sheet, ['商品信息', '店铺名称', 'SKC点击率/SKC转化率', '自主参与活动'])
        column_to_left(sheet, ['店铺名称', 'SKC点击率/SKC转化率', '自主参与活动'])
        specify_column_width(sheet, ['商品标题'], 150 / 6)
        add_borders(sheet)
        InsertImageV2(sheet, ['SKC图片', 'SKU图片'], 'shein', 120, None, None, True)
        wb.save()
        close_excel(app, wb)

    # 处理公式计算
    def dealFormula(self, sheet):
        # 增加列 周销增量 月销增量
        col_week_increment = find_column_by_data(sheet, 1, '周销增量')
        if col_week_increment is None:
            col_week_increment = find_column_by_data(sheet, 1, '远30天销量')
            log(f'{col_week_increment}:{col_week_increment}')
            sheet.range(f'{col_week_increment}:{col_week_increment}').insert('right')
            sheet.range(f'{col_week_increment}1').value = '周销增量'
            log('已增加列 周销增量')

        col_month_increment = find_column_by_data(sheet, 1, '月销增量')
        if col_month_increment is None:
            col_month_increment = find_column_by_data(sheet, 1, '总销量')
            log(f'{col_month_increment}:{col_month_increment}')
            sheet.range(f'{col_month_increment}:{col_month_increment}').insert('right')
            sheet.range(f'{col_month_increment}1').value = '月销增量'
            log('已增加列 月销增量')

        col_month_profit = find_column_by_data(sheet, 1, '近30天利润')
        if col_month_profit is None:
            col_month_profit = find_column_by_data(sheet, 1, '总利润')
            sheet.range(f'{col_month_profit}:{col_month_profit}').insert('right')
            log((f'{col_month_profit}:{col_month_profit}'))
            sheet.range(f'{col_month_profit}1').value = '近30天利润'
            log('已增加列 近30天利润')

        col_week_profit = find_column_by_data(sheet, 1, '近7天利润')
        if col_week_profit is None:
            col_week_profit = find_column_by_data(sheet, 1, '近30天利润')
            sheet.range(f'{col_week_profit}:{col_week_profit}').insert('right')
            log((f'{col_week_profit}:{col_week_profit}'))
            sheet.range(f'{col_week_profit}1').value = '近7天利润'
            log('已增加列 近7天利润')

        # return

        # 查找 申报价，成本价，毛利润，毛利润率 所在列
        col_verify_price = find_column_by_data(sheet, 1, '申报价')
        col_cost_price = find_column_by_data(sheet, 1, '成本价')
        col_gross_profit = find_column_by_data(sheet, 1, '毛利润')
        col_gross_margin = find_column_by_data(sheet, 1, '毛利率')

        col_week_1 = find_column_by_data(sheet, 1, '近7天销量')
        col_week_2 = find_column_by_data(sheet, 1, '远7天销量')
        col_month_1 = find_column_by_data(sheet, 1, '近30天销量')
        col_month_2 = find_column_by_data(sheet, 1, '远30天销量')

        # 遍历可用行
        used_range_row = sheet.range('A1').expand('down')
        for i, cell in enumerate(used_range_row):
            row = i + 1
            if row < 2:
                continue
            rangeA = f'{col_verify_price}{row}'
            rangeB = f'{col_cost_price}{row}'

            rangeC = f'{col_week_increment}{row}'
            rangeD = f'{col_month_increment}{row}'

            # rangeE = f'{col_total_profit}{row}'
            rangeF = f'{col_month_profit}{row}'
            rangeG = f'{col_week_profit}{row}'

            # 设置毛利润和毛利润率列公式与格式
            sheet.range(f'{col_gross_profit}{row}').formula = f'=IF(ISNUMBER({rangeB}),{rangeA}-{rangeB},"")'
            sheet.range(f'{col_gross_profit}{row}').number_format = '0.00'
            sheet.range(f'{col_gross_margin}{row}').formula = f'=IF(ISNUMBER({rangeB}),({rangeA}-{rangeB})/{rangeA},"")'
            sheet.range(f'{col_gross_margin}{row}').number_format = '0.00%'

            sheet.range(rangeC).formula = f'={col_week_1}{row}-{col_week_2}{row}'
            sheet.range(rangeC).number_format = '0'
            sheet.range(rangeD).formula = f'={col_month_1}{row}-{col_month_2}{row}'
            sheet.range(rangeD).number_format = '0'

            # sheet.range(rangeE).formula = f'=IF(ISNUMBER({rangeB}),{col_total}{row}*{col_gross_profit}{row},"")'
            # sheet.range(rangeE).number_format = '0.00'
            sheet.range(rangeF).formula = f'=IF(ISNUMBER({rangeB}),{col_month_1}{row}*{col_gross_profit}{row},"")'
            sheet.range(rangeF).number_format = '0.00'
            sheet.range(rangeG).formula = f'=IF(ISNUMBER({rangeB}),{col_week_1}{row}*{col_gross_profit}{row},"")'
            sheet.range(rangeG).number_format = '0.00'
