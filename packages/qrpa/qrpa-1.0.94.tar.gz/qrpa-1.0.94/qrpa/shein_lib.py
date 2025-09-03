from .fun_file import read_dict_from_file, write_dict_to_file, read_dict_from_file_ex, write_dict_to_file_ex
from .fun_base import log, send_exception, md5_string, get_safe_value, NetWorkIdleTimeout
from .fun_web import fetch, fetch_get, full_screen_shot, safe_goto
from .time_utils import TimeUtils
from .wxwork import WxWorkBot

from .shein_sqlite import insert_sales, get_last_week_sales, get_near_week_sales, get_near_month_sales, get_last_month_sales

import math
import time
import json, traceback
from datetime import datetime
from playwright.sync_api import Page

from .shein_daily_report_model import SheinStoreSalesDetailManager

class SheinLib:

    def __init__(self, config, bridge, web_page: Page, store_username, store_name):
        self.config = config
        self.bridge = bridge
        self.store_username = store_username
        self.store_name = store_name
        self.web_page = web_page
        self.dt = None
        self.DictQueryTime = {}

        self.deal_auth()

    # 处理鉴权
    def deal_auth(self):
        web_page = self.web_page

        # 等待页面稳定并处理导航
        for attempt in range(3):
            try:
                current_url = web_page.url
                log(f"尝试获取页面信息 - URL: {current_url}", self.store_username, self.store_name)

                # 检查是否在认证页面，如果是则直接跳转到目标页面
                if '/auth/SSLS' in current_url:
                    log("检测到SSLS认证页面，直接跳转到首页", self.store_username, self.store_name)
                    web_page.goto('https://sso.geiwohuo.com/#/home', wait_until='domcontentloaded', timeout=15000)
                    web_page.wait_for_timeout(3000)
                    current_url = web_page.url
                    log(f"跳转后URL: {current_url}", self.store_username, self.store_name)

                # 等待导航完成
                web_page.wait_for_load_state("domcontentloaded", timeout=6000)

                final_url = web_page.url
                final_title = web_page.title()
                log(f"页面稳定 - URL: {final_url}, 标题: {final_title}", self.store_username, self.store_name)
                break

            except Exception as e:
                log(f"第{attempt + 1}次等待页面稳定失败: {e}", self.store_username, self.store_name)
                if "crashed" in str(e) or "Target" in str(e):
                    log("页面稳定检查时崩溃，直接继续", self.store_username, self.store_name)
                    break
                elif "destroyed" in str(e) or "navigation" in str(e):
                    log("检测到导航中断，等待导航完成", self.store_username, self.store_name)
                    web_page.wait_for_timeout(4000)
                    continue
                elif attempt == 2:
                    log("页面稳定等待最终失败，继续执行", self.store_username, self.store_name)
                    break
                web_page.wait_for_timeout(2000)

        web_page.wait_for_timeout(2000)

        # 定义最大重试次数
        MAX_RETRIES = 5
        retries = 0
        wait_count = 0
        is_send = False

        # close_modal(web_page) # 不能开启 需要勾选协议弹窗

        while retries < MAX_RETRIES:
            try:

                retries += 1

                while not web_page.locator('//div[contains(text(),"商家后台")]').nth(1).is_visible():

                    try:
                        current_url = web_page.url
                        current_title = web_page.title()
                        log(f"循环检查 - URL: {current_url}, 标题: {current_title}", self.store_username, self.store_name)

                        # 如果在认证页面且出现问题，直接跳转
                        if '/auth/SSLS' in current_url:
                            log("在主循环中检测到SSLS认证页面，跳转到首页", self.store_username, self.store_name)
                            web_page.goto('https://sso.geiwohuo.com/#/home', wait_until='domcontentloaded', timeout=15000)
                            web_page.wait_for_timeout(3000)
                            continue

                    except Exception as status_error:
                        log(f"获取页面状态失败: {status_error}", self.store_username, self.store_name)
                        if "crashed" in str(status_error):
                            break

                    if web_page.locator('xpath=//div[@id="container" and @alita-name="gmpsso"]//button[@type="button" and @id]').nth(0).is_visible():
                        if 'https://sso.geiwohuo.com/#/home' not in web_page.url:
                            log("鉴权确定按钮可见 点击'确定'按钮", web_page.title(), web_page.url, self.store_username, self.store_name)
                            web_page.locator('xpath=//div[@id="container" and @alita-name="gmpsso"]//button[@type="button" and @id]').nth(0).click()
                            web_page.wait_for_timeout(5000)

                    while web_page.locator('//div[text()="验证码"]').is_visible():
                        log(f'等待输入验证码: {wait_count}', self.store_username, self.store_name)
                        if not is_send:
                            is_send = True
                            img_path = full_screen_shot(web_page, self.config)
                            WxWorkBot(self.config.wxwork_bot_exception).send_img(img_path)
                            WxWorkBot(self.config.wxwork_bot_exception).send_text(f'{self.store_username},{self.store_name} 需要登录验证码')
                        time.sleep(5)
                        wait_count += 1

                    if web_page.locator('//div[contains(text(),"同意签署协议")]').count() > 0:
                        while web_page.locator('//div[contains(text(),"同意签署协议")]').count() == 0:
                            log('等待协议内容出现')
                            web_page.wait_for_timeout(1000)

                    if web_page.locator('//div[contains(text(),"同意签署协议")]').count() > 0:
                        log('检测到同意签署协议')
                        web_page.wait_for_timeout(1000)
                        log('点击同意复选框')
                        web_page.locator('//i[@class="so-checkinput-indicator so-checkinput-checkbox"]').click()
                        web_page.wait_for_timeout(1000)
                        log('点击同意按钮')
                        web_page.locator('//button[span[text()="同意"]]').click()

                    if web_page.locator('//input[@name="username"]').is_visible():
                        log("用户名输入框可见 等待5秒点击'登录'按钮", self.store_username, self.store_name)
                        web_page.wait_for_timeout(5000)
                        log('点击"登录"', self.store_username, self.store_name)
                        web_page.locator('//button[contains(@class,"login_btn")]').click()

                        log('再延时5秒', self.store_username, self.store_name)
                        web_page.wait_for_timeout(5000)

                    if web_page.locator('//span[contains(text(),"商品管理")]').nth(1).is_visible():
                        log('商品管理菜单可见 退出鉴权处理', self.store_username, self.store_name)
                        return

                    log('商家后台不可见', web_page.title(), web_page.url, self.store_username, self.store_name)
                    if 'https://sso.geiwohuo.com/#/home' in web_page.url:
                        web_page.wait_for_timeout(5000)
                        web_page.reload()

                    # while r'=/CN' in web_page.url:
                    #     safe_goto(web_page, 'https://sso.geiwohuo.com/#/home?q=0')
                    #
                    #     web_page.wait_for_timeout(5000)
                    #     if web_page.locator('//input[@name="username"]').is_visible():
                    #         log("用户名输入框可见 等待5秒点击'登录'按钮", self.store_username, self.store_name)
                    #         web_page.wait_for_timeout(5000)
                    #         log('点击"登录"', self.store_username, self.store_name)
                    #         web_page.locator('//button[contains(@class,"login_btn")]').click()
                    #
                    #         log('再延时5秒', self.store_username, self.store_name)
                    #         web_page.wait_for_timeout(5000)

                    web_page.wait_for_timeout(3000)

                    if 'https://sso.geiwohuo.com/#/home' in web_page.url:

                        if 'SHEIN全球商家中心' in web_page.title() or '后台首页' in web_page.title() or '商家后台' in web_page.title():
                            log(web_page.title(), '中断循环', self.store_username, self.store_name)
                            web_page.wait_for_timeout(5000)
                            break

                    if 'mrs.biz.sheincorp.cn' in web_page.url and '商家后台' in web_page.title():
                        try:
                            web_page.goto('https://sso.geiwohuo.com/#/home?q=1', wait_until='domcontentloaded', timeout=10000)
                            web_page.wait_for_timeout(3000)
                        except Exception as nav_error:
                            log(f"导航失败，尝试重新加载: {nav_error}", self.store_username, self.store_name)
                            web_page.reload(wait_until='domcontentloaded', timeout=10000)
                            web_page.wait_for_timeout(5000)

                    if web_page.locator('//h1[contains(text(),"鉴权")]').is_visible():
                        log('检测到鉴权 刷新页面', self.store_username, self.store_name)
                        web_page.reload()
                        web_page.wait_for_timeout(5000)
                        web_page.reload()
                        web_page.wait_for_timeout(5000)

                    if web_page.title() == 'SHEIN':
                        try:
                            web_page.goto('https://sso.geiwohuo.com/#/home?q=2', wait_until='domcontentloaded', timeout=10000)
                            web_page.wait_for_timeout(3000)
                        except Exception as nav_error:
                            log(f"导航失败，尝试重新加载: {nav_error}", self.store_username, self.store_name)
                            web_page.reload(wait_until='domcontentloaded', timeout=10000)
                            web_page.wait_for_timeout(5000)

                break
            except Exception as e:
                log(f"错误发生: {e}, 重试中...({self.store_username}, {self.store_name})")
                log(traceback.format_exc())

                # 收集崩溃时的详细信息
                try:
                    crash_url = web_page.url
                    crash_title = web_page.title()
                    log(f"崩溃时页面信息 - URL: {crash_url}, 标题: {crash_title}", self.store_username, self.store_name)

                    # 尝试截图保存崩溃现场
                    try:
                        screenshot_path = f"crash_screenshot_{self.store_username}_{int(time.time())}.png"
                        web_page.screenshot(path=screenshot_path)
                        log(f"已保存崩溃截图: {screenshot_path}", self.store_username, self.store_name)
                    except:
                        log("无法截取崩溃时的页面截图", self.store_username, self.store_name)

                except:
                    log("无法获取崩溃时的页面信息", self.store_username, self.store_name)

                # 检查特定类型的错误
                if any(keyword in str(e).lower() for keyword in ['memory', 'out of memory', 'oom']):
                    log("检测到内存相关崩溃", self.store_username, self.store_name)

                if "destroyed" in str(e) or "navigation" in str(e):
                    log("检测到导航中断，等待页面稳定后重试", self.store_username, self.store_name)
                    web_page.wait_for_timeout(5000)
                    continue

                if 'crashed' in str(e) or 'Target' in str(e):
                    log("检测到页面或目标崩溃，直接退出当前循环", self.store_username, self.store_name)
                    raise e
                retries += 1
                if retries >= MAX_RETRIES:
                    log(f"达到最大重试次数，停止尝试({self.store_username}, {self.store_name})")
                    break
                time.sleep(2)  # 错误时等待2秒后重试

        log('鉴权处理结束')
        # web_page.wait_for_load_state("load")
        # web_page.wait_for_load_state("networkidle")
        web_page.wait_for_timeout(3000)

    # 获取用户信息
    def get_user(self, uuid=None):
        log(f'获取用户信息:{self.store_username} {self.store_name}')

        # 生成 uuid 参数，如果没有提供则使用时间戳
        if uuid is None:
            import time
            uuid = str(int(time.time() * 1000))

        url = f"https://sso.geiwohuo.com/sso-prefix/auth/getUser?uuid={uuid}"

        # 设置请求头，根据 Chrome 请求
        headers = {
            "gmpsso-language": "CN",
            "origin-url"     : "https://sso.geiwohuo.com/#/home/",
            "x-sso-scene"    : "gmpsso"
        }

        # 特定于此请求的配置
        fetch_config = {
            "credentials"   : "omit",
            "referrer"      : "https://sso.geiwohuo.com/",
            "referrerPolicy": "strict-origin-when-cross-origin"
        }

        response_text = fetch_get(self.web_page, url, headers, fetch_config)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        info = response_text.get('info', {})
        log(info)
        cache_file = f'{self.config.auto_dir}/shein_user.json'
        info['store_username'] = self.store_username
        info['store_name'] = self.store_name
        write_dict_to_file_ex(cache_file, {self.store_username: info}, [self.store_username])

        return info

    # 获取质检报告pdf地址
    def get_qc_report_url(self, deliverCode, purchaseCode):
        log(f'获取质检报告:{deliverCode} {purchaseCode}')
        url = f"https://sso.geiwohuo.com/pfmp/returnPlan/queryQcReport"
        payload = {
            "deliverCode" : deliverCode,
            "purchaseCode": purchaseCode
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        qc_report_url = (response_text.get('info', {}).get('data') or [{'qcReportUrl': '质检报告生成中,请稍后查看'}])[0].get('qcReportUrl')
        log(qc_report_url)
        return qc_report_url

    # 获取稽查报表
    def get_inspect_report_url(self, returnOrderId):
        log(f'获取稽查报告:{returnOrderId}')
        url = f"https://sso.geiwohuo.com/pfmp/returnOrder/queryInspectReport"
        payload = {
            "returnOrderId": returnOrderId,
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        log(response_text)
        report_url = response_text.get('info', {}).get('reportUrl')
        return report_url

    def get_return_order_box_detail(self, returnOrderId):
        log(f'获取退货包裹详情: {returnOrderId}')
        url = f"https://sso.geiwohuo.com/pfmp/returnOrder/getReturnOrderBoxDetail"
        payload = {
            "returnOrderId": returnOrderId,
            "page"         : 1,
            "perPage"      : 50
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        list_item = response_text['info']['data']

        for item in list_item:
            # 遍历每个快递单的包裹列表
            for box in item.get('boxList', []):
                # 遍历每个包裹中的商品列表
                for good in box.get('goods', []):
                    # 遍历每个商品的详情列表（包含platformSku的层级）
                    for detail in good.get('details', []):
                        # 在这里添加新字段
                        # 示例：添加一个"status"字段，值为"processed"
                        supplier_sku = detail.get('supplierSku')
                        erp_supplier_name = self.bridge.get_sku_supplier(supplier_sku, self.config.erp_source)
                        log(self.config.erp_source, supplier_sku, erp_supplier_name)
                        if erp_supplier_name != '-':
                            detail['erp_supplier_name'] = erp_supplier_name
                        erp_cost_price = self.bridge.get_sku_cost(supplier_sku, self.config.erp_source)
                        log(self.config.erp_source, supplier_sku, erp_cost_price)
                        if erp_cost_price != '-':
                            detail['erp_cost_price'] = erp_cost_price

        log(list_item)
        cache_file = f'{self.config.auto_dir}/shein/cache/shein_return_order_box_detail_{returnOrderId}.json'
        write_dict_to_file(cache_file, list_item)
        return list_item

    def get_return_order_list(self, start_date, end_date, only_yesterday=1):

        log(f'获取退货列表: {self.store_username} {self.store_name} {start_date} {end_date}')

        page_num = 1
        page_size = 200  # 列表最多返回200条数据 大了没有用

        url = f"https://sso.geiwohuo.com/pfmp/returnOrder/page"
        payload = {
            "returnOrderType": 1,  # 只查询退货
            "addTimeStart"   : f"{start_date} 00:00:00",
            "addTimeEnd"     : f"{end_date} 23:59:59",
            "page"           : page_num,
            "perPage"        : page_size
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        list_item = response_text['info']['data']
        total = response_text['info']['meta']['count']
        totalPage = math.ceil(total / page_size)

        for page in range(2, totalPage + 1):
            log(f'获取退供列表 第{page}/{totalPage}页 共{total}条记录')
            payload['page'] = page
            response_text = fetch(self.web_page, url, payload)
            spu_list_new = response_text['info']['data']
            list_item += spu_list_new
            time.sleep(0.1)

        all_list_item = []
        today_list_item = []
        # 过滤 退货出库时间 是昨天的
        for item in list_item:
            returnOrderId = item['id']
            item['store_username'] = self.store_username
            item['store_name'] = self.store_name
            item['store_manager'] = self.config.shein_store_manager.get(str(self.store_username).lower())

            item['qc_report_url'] = ''
            if int(item['returnScrapType']) == 1:
                purchaseCode = item['sellerOrderNo']
                delivery_code = item['sellerDeliveryNo']
                item['qc_report_url'] = self.get_qc_report_url(delivery_code, purchaseCode)

            item['report_url'] = ''
            if int(item['returnScrapType']) == 2:
                item['report_url'] = self.get_inspect_report_url(returnOrderId)

            item['return_box_detail'] = []

            has_valid_package = item.get('hasPackage') == 1
            if has_valid_package:
                return_box_detail = self.get_return_order_box_detail(returnOrderId)
                if len(return_box_detail) > 0:
                    item['return_box_detail'] = return_box_detail

                    all_list_item.append(item)
                    is_valid_yesterday = TimeUtils.is_yesterday(item['completeTime'], None) if item.get('completeTime') else False
                    if is_valid_yesterday:
                        today_list_item.append(item)

        cache_file = f'{self.config.auto_dir}/shein/cache/shein_return_order_list_{TimeUtils.today_date()}.json'
        write_dict_to_file_ex(cache_file, {self.store_username: today_list_item}, [self.store_username])

        cache_file = f'{self.config.auto_dir}/shein/cache/shein_return_order_list_{start_date}_{end_date}.json'
        write_dict_to_file_ex(cache_file, {self.store_username: all_list_item}, [self.store_username])

        return list_item

    # 获取希音退供明细 和 台账明细一个接口
    def get_back_list(self, source='mb'):
        page_num = 1
        page_size = 200  # 列表最多返回200条数据 大了没有用

        first_day, last_day = TimeUtils.get_last_month_range()

        cache_file = f'{self.config.auto_dir}/shein/cache/return_detail_{self.store_username}_{first_day}_{last_day}.json'
        list_item = read_dict_from_file(cache_file, 3600 * 24 * 20)
        if len(list_item) > 0:
            return list_item

        url = f"https://sso.geiwohuo.com/mils/changeDetail/page"
        payload = {
            "displayChangeTypeList": ["10"],
            "addTimeStart"         : f"{first_day} 00:00:00",
            "addTimeEnd"           : f"{last_day} 23:59:59",
            "pageNumber"           : page_num,
            "pageSize"             : page_size,
            "changeTypeIndex"      : "2"
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        list_item = response_text['info']['data']['list']
        total = response_text['info']['data']['count']
        totalPage = math.ceil(total / page_size)

        for page in range(2, totalPage + 1):
            log(f'获取台账明细列表 第{page}/{totalPage}页')
            payload['pageNumber'] = page
            response_text = fetch(self.web_page, url, payload)
            spu_list_new = response_text['info']['data']['list']
            list_item += spu_list_new
            time.sleep(0.1)

        # cost_price =
        for item in list_item:
            supplierSku = item['supplierSku']
            item['cost_price'] = self.bridge.get_sku_cost(supplierSku, source)
            item['sku_img'] = self.bridge.get_sku_img(supplierSku, source)

        write_dict_to_file(cache_file, list_item)

        return list_item

    # 不结算列表
    def get_no_settlement_list(self, source='mb'):
        page_num = 1
        page_size = 200  # 列表最多返回200条数据 大了没有用

        first_day, last_day = TimeUtils.get_last_month_range()

        cache_file = f'{self.config.auto_dir}/shein/cache/no_settlement_{self.store_username}_{first_day}_{last_day}.json'
        list_item = read_dict_from_file(cache_file, 3600 * 24 * 20)
        if len(list_item) > 0:
            return list_item

        url = f"https://sso.geiwohuo.com/mils/changeDetail/page"
        payload = {
            "addTimeStart"         : f"{first_day} 00:00:00",
            "addTimeEnd"           : f"{last_day} 23:59:59",
            "pageNumber"           : page_num,
            "pageSize"             : page_size,
            "changeTypeIndex"      : "2",
            "settleTypeList"       : ["1"],  # 不结算
            "displayChangeTypeList": ["6", "7", "9", "10", "11", "12", "13", "16", "18", "19"]  # 出库
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        list_item = response_text['info']['data']['list']
        total = response_text['info']['data']['count']
        totalPage = math.ceil(total / page_size)

        for page in range(2, totalPage + 1):
            log(f'获取台账明细列表 第{page}/{totalPage}页')
            payload['pageNumber'] = page
            response_text = fetch(self.web_page, url, payload)
            spu_list_new = response_text['info']['data']['list']
            list_item += spu_list_new
            time.sleep(0.1)

        # cost_price =
        for item in list_item:
            supplierSku = item['supplierSku']
            item['cost_price'] = self.bridge.get_sku_cost(supplierSku, source)
            item['sku_img'] = self.bridge.get_sku_img(supplierSku, source)

        write_dict_to_file(cache_file, list_item)

        return list_item

    def get_ledger_list(self, source='mb'):
        page_num = 1
        page_size = 200  # 列表最多返回200条数据 大了没有用

        first_day, last_day = TimeUtils.get_last_month_range()

        cache_file = f'{self.config.auto_dir}/shein/cache/sales_detail_{self.store_username}_{first_day}_{last_day}.json'
        list_item = read_dict_from_file(cache_file, 3600 * 24 * 20)
        if len(list_item) > 0:
            return list_item

        url = f"https://sso.geiwohuo.com/mils/changeDetail/page"
        payload = {
            "displayChangeTypeList": ["6", "7", "9", "10", "11", "12", "13", "16", "18", "19"],  # 出库
            "addTimeStart"         : f"{first_day} 00:00:00",
            "addTimeEnd"           : f"{last_day} 23:59:59",
            "pageNumber"           : page_num,
            "pageSize"             : page_size,
            "changeTypeIndex"      : "2"
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        list_item = response_text['info']['data']['list']
        total = response_text['info']['data']['count']
        totalPage = math.ceil(total / page_size)

        for page in range(2, totalPage + 1):
            log(f'获取台账明细列表 第{page}/{totalPage}页')
            payload['pageNumber'] = page
            response_text = fetch(self.web_page, url, payload)
            spu_list_new = response_text['info']['data']['list']
            list_item += spu_list_new
            time.sleep(0.1)

        # cost_price =
        for item in list_item:
            supplierSku = item['supplierSku']
            item['cost_price'] = self.bridge.get_sku_cost(supplierSku, source)
            item['sku_img'] = self.bridge.get_sku_img(supplierSku, source)

        write_dict_to_file(cache_file, list_item)

        return list_item

    def get_shein_stock_list(self, source='mb'):
        page_num = 1
        page_size = 200  # 列表最多返回200条数据 大了没有用

        first_day, last_day = TimeUtils.get_last_month_range()

        cache_file = f'{self.config.auto_dir}/shein/cache/stock_detail_{self.store_username}_{first_day}_{last_day}.json'
        list_item = read_dict_from_file(cache_file, 3600 * 24 * 20)
        if len(list_item) > 0:
            return list_item

        url = f"https://sso.geiwohuo.com/mils/report/month/detail/list"
        payload = {
            "reportDateStart": first_day,
            "reportDateEnd"  : last_day,
            "pageNumber"     : page_num,
            "pageSize"       : page_size,
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        list_item = response_text['info']['data']['list']
        total = response_text['info']['data']['count']
        totalPage = math.ceil(total / page_size)

        for page in range(2, totalPage + 1):
            log(f'获取库存结余明细列表 第{page}/{totalPage}页')
            page_num = page
            payload = {
                "reportDateStart": first_day,
                "reportDateEnd"  : last_day,
                "pageNumber"     : page_num,
                "pageSize"       : page_size,
            }
            response_text = fetch(self.web_page, url, payload)
            spu_list_new = response_text['info']['data']['list']
            list_item += spu_list_new
            time.sleep(0.1)

        for item in list_item:
            supplierSku = item['supplierSku']
            item['cost_price'] = self.bridge.get_sku_cost(supplierSku, source)
            item['sku_img'] = self.bridge.get_sku_img(supplierSku, source)

        write_dict_to_file(cache_file, list_item)

        return list_item

    def get_replenish_list(self):
        page_num = 1
        page_size = 50
        first_day, last_day = TimeUtils.get_last_month_range()

        cache_file = f'{self.config.auto_dir}/cache/replenish_list_{self.store_username}_{first_day}_{last_day}.json'
        list_item = read_dict_from_file(cache_file, 3600 * 24 * 20)
        if len(list_item) > 0:
            return list_item

        url = f"https://sso.geiwohuo.com/gsfs/finance/selfReplenish/list"
        payload = {
            "page"        : page_num,
            "perPage"     : page_size,
            "tabType"     : 2,
            "addTimeStart": f"{first_day} 00:00:00",
            "addTimeEnd"  : f"{last_day} 23:59:59"
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        list_item = response_text['info']['data']
        total = response_text['info']['meta']['count']
        totalPage = math.ceil(total / page_size)

        for page in range(2, totalPage + 1):
            log(f'获取不扣款列表 第{page}/{totalPage}页')
            page_num = page
            payload = {
                "page"        : page_num,
                "perPage"     : page_size,
                "tabType"     : 2,
                "addTimeStart": f"{first_day} 00:00:00",
                "addTimeEnd"  : f"{last_day} 23:59:59"
            }
            response_text = fetch(self.web_page, url, payload)
            spu_list_new = response_text['info']['data']
            list_item += spu_list_new
            time.sleep(0.1)

        write_dict_to_file(cache_file, list_item)

        return list_item

    def get_return_list(self):
        page_num = 1
        page_size = 200
        first_day, last_day = TimeUtils.get_last_month_range()

        cache_file = f'{self.config.auto_dir}/cache/return_list_{self.store_username}_{first_day}_{last_day}.json'
        list_item = read_dict_from_file(cache_file, 3600 * 24 * 20)
        if len(list_item) > 0:
            return list_item

        url = f"https://sso.geiwohuo.com/pfmp/returnOrder/page"
        payload = {
            "addTimeStart"         : f"{first_day} 00:00:00",
            "addTimeEnd"           : f"{last_day} 23:59:59",
            "returnOrderStatusList": [4],
            "page"                 : page_num,
            "perPage"              : page_size
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))

        list_item = response_text['info']['data']
        total = response_text['info']['meta']['count']
        totalPage = math.ceil(total / page_size)

        for page in range(2, totalPage + 1):
            log(f'获取不扣款列表 第{page}/{totalPage}页')
            page_num = page
            payload = {
                "addTimeStart"         : f"{first_day} 00:00:00",
                "addTimeEnd"           : f"{last_day} 23:59:59",
                "returnOrderStatusList": [4],
                "page"                 : page_num,
                "perPage"              : page_size
            }
            response_text = fetch(self.web_page, url, payload)
            spu_list_new = response_text['info']['data']
            list_item += spu_list_new
            time.sleep(0.1)

        write_dict_to_file(cache_file, list_item)

        return list_item

    def get_comment_list(self):
        cache_file = f'{self.config.auto_dir}/shein/dict/comment_list_{TimeUtils.today_date()}.json'
        comment_list = read_dict_from_file_ex(cache_file, self.store_username, 3600)
        if len(comment_list) > 0:
            return comment_list

        page_num = 1
        page_size = 50

        yesterday = TimeUtils.get_yesterday()

        url = f"https://sso.geiwohuo.com/gsp/goods/comment/list"
        payload = {
            "page"            : page_num,
            "perPage"         : page_size,
            "startCommentTime": f"{yesterday} 00:00:00",
            "commentEndTime"  : f"{yesterday} 23:59:59",
            "commentStarList" : ["3", "2", "1"]
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))

        comment_list = response_text['info']['data']
        total = response_text['info']['meta']['count']
        totalPage = math.ceil(total / page_size)

        for page in range(2, totalPage + 1):
            log(f'获取评价列表 第{page}/{totalPage}页')
            page_num = page
            payload['page'] = page_num
            response_text = fetch(self.web_page, url, payload)
            comment_list = response_text['info']['data']
            time.sleep(0.1)

        write_dict_to_file_ex(cache_file, {self.store_username: comment_list}, [self.store_username])
        return comment_list

    def get_last_month_outbound_amount(self):
        url = "https://sso.geiwohuo.com/mils/report/month/list"
        start, end = TimeUtils.get_current_year_range()
        payload = {
            "reportDateStart": start, "reportDateEnd": end, "pageNumber": 1, "pageSize": 50
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        info = response_text.get('info')
        lst = info.get('data', {}).get('list', [])
        if not lst:
            log(f'⚠️ {self.store_name} 最近一个月无出库记录，金额为0')
            return 0

        last_item = lst[-1]
        log(f'正在获取 {self.store_name} 最近一个月出库金额: {last_item["totalCustomerAmount"]}')
        return last_item['totalCustomerAmount']

    def query_attribute_multi(self, attribute_id_list):
        url = "https://sso.geiwohuo.com/spmp-api-prefix/spmp/attribute/query_attribute_multi"
        payload = {
            "attribute_id_list": attribute_id_list,
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        info = response_text.get('info')
        lst = info.get('data', {})
        return lst

    def get_product_attr(self, spu, attr_name):
        try:
            product_detail = self.get_product_detail(spu)
            product_type_id = product_detail.get('product_type_id')
            category_id = product_detail.get('category_id')

            if not product_type_id or not category_id:
                return None  # 或者根据需要返回一个默认值

            attribute_template = self.get_attribute_templates(spu, category_id, [product_type_id])
            attr_info = attribute_template.get('attribute_infos', [])

            # 查找材质属性映射，防止没有匹配项
            attr_item = next((item for item in attr_info if item.get('attribute_name') == attr_name), None)
            if not attr_item:
                return None  # 或者返回一个默认值

            attr_id = attr_item.get('attribute_id')

            # 拿到产品材质的属性值ID
            product_attribute_list = product_detail.get('product_attribute_list', [])
            attribute_value_id = next((item['attribute_value_id'] for item in product_attribute_list if item.get('attribute_id') == attr_id), None)
            if not attribute_value_id:
                return None  # 或者返回一个默认值

            # 获取属性值名称
            attr_value = next((item['attribute_value'] for item in attr_item.get('attribute_value_info_list', []) if item.get('attribute_value_id') == attribute_value_id), None)
            return attr_value  # 返回找到的属性值
        except Exception as e:
            log(f"Error occurred: {e}")
            send_exception()
            return None  # 或者返回一个默认值

    def get_attribute_templates(self, spu_name, category_id, product_type_id_list):
        log(f'正在获取 {spu_name} 商品属性模板')

        if not isinstance(product_type_id_list, list):
            raise '参数错误: product_type_id_list 需要是列表'

        cache_file = f'{self.config.auto_dir}/shein/attribute/attribute_template_{spu_name}.json'
        attr_list = read_dict_from_file(cache_file, 3600 * 24 * 7)
        if len(attr_list) > 0:
            return attr_list

        url = f"https://sso.geiwohuo.com/spmp-api-prefix/spmp/basic/query_attribute_templates"
        payload = {
            "category_id"         : category_id,
            "for_update"          : True,
            "product_type_id_list": product_type_id_list,
            "spu_name"            : spu_name
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        info = response_text.get('info')

        data = info.get('data')[0]
        write_dict_to_file(cache_file, data)
        return data

    def get_product_detail(self, spu_name):
        cache_file = f'{self.config.auto_dir}/shein/product_detail/product_detail_{spu_name}.json'
        info = read_dict_from_file(cache_file, 3600 * 24 * 7)
        if len(info) > 0:
            return info

        log(f'正在获取 {spu_name} 商品详情')
        url = f"https://sso.geiwohuo.com/spmp-api-prefix/spmp/product/get_product_detail"
        payload = {
            "spu_name": spu_name
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        info = response_text.get('info')

        # 获取 area_attribute_id
        sample_sku_back_size = info.get('sample_sku_back_size', None)
        if sample_sku_back_size is not None:
            area_attribute_ids = [item['area_attribute_id'] for item in sample_sku_back_size.get('area_info_list', [])]
            attribute_multi = self.query_attribute_multi(area_attribute_ids)
            info["attribute_multi"] = attribute_multi

        write_dict_to_file(cache_file, info)
        return info

    # 存储商品库
    def store_product_info(self):
        # todo 商品详情 属性 规格 图片 重量 与 尺寸
        skc_list = self.get_bak_base_info()
        cache_file = f'{self.config.auto_dir}/shein/sku_price/sku_price_{self.store_username}.json'
        dict_sku = read_dict_from_file(cache_file)
        dict_product_detail = []
        for skc_item in skc_list:
            skc_item['store_username'] = self.store_username
            skc_item['store_name'] = self.store_name
            skc_item['store_manager'] = self.config.shein_store_manager.get(str(self.store_username).lower())
            spu = skc_item['spu']
            if spu not in dict_product_detail:
                dict_product_detail.append(spu)
                material = self.get_product_attr(spu, '材质')
                log(material)  # 这一步是为了获取 spu 详情和属性

            # 倒序遍历 skuList，安全删除
            for i in range(len(skc_item['skuList']) - 1, -1, -1):
                sku_item = skc_item['skuList'][i]
                if sku_item['skuCode'] == '合计':
                    del skc_item['skuList'][i]  # 删除“合计”
                    continue
                sku_item['price'] = dict_sku[sku_item['skuCode']]
                cost_price = self.bridge.get_sku_cost(sku_item['supplierSku'], self.config.erp_source)
                sku_item['erp_cost_price'] = cost_price if isinstance(cost_price, (int, float)) else None
                sku_item['erp_supplier_name'] = self.bridge.get_sku_supplier(sku_item['supplierSku'], self.config.erp_source)
                stock = self.bridge.get_sku_stock(sku_item['supplierSku'], self.config.erp_source)
                sku_item['erp_stock'] = stock if isinstance(stock, (int, float)) else None

        cache_file = f'{self.config.auto_dir}/shein/product/skc_list_{self.store_username}.json'
        write_dict_to_file_ex(cache_file, {self.store_username: skc_list}, [self.store_username])

        skc_file = f'{self.config.auto_dir}/shein/product/skc_list_file.json'
        write_dict_to_file_ex(skc_file, {self.store_username: cache_file}, [self.store_username])

        detail_file = f'{self.config.auto_dir}/shein/product/product_detail_file.json'
        write_dict_to_file_ex(detail_file, {self.store_username: dict_product_detail}, [self.store_username])

    # 获取备货信息列表
    def get_bak_base_info(self):
        log(f'获取备货信息列表 {self.store_name} {self.store_username}')
        url = "https://sso.geiwohuo.com/idms/goods-skc/list"
        pageNumber = 1
        pageSize = 100
        payload = {
            "pageNumber"            : pageNumber,
            "pageSize"              : pageSize,
            "supplierCodes"         : "",
            "skcs"                  : "",
            "spu"                   : "",
            "c7dSaleCntBegin"       : "",
            "c7dSaleCntEnd"         : "",
            "goodsLevelIdList"      : [],
            "supplyStatus"          : "",
            "shelfStatus"           : "",
            "categoryIdList"        : [],
            "skcStockBegin"         : "",
            "skcStockEnd"           : "",
            "skuStockBegin"         : "",
            "skuStockEnd"           : "",
            "skcSaleDaysBegin"      : "",
            "skcSaleDaysEnd"        : "",
            "skuSaleDaysBegin"      : "",
            "skuSaleDaysEnd"        : "",
            "planUrgentCountBegin"  : "",
            "planUrgentCountEnd"    : "",
            "skcAvailableOrderBegin": "",
            "skcAvailableOrderEnd"  : "",
            "skuAvailableOrderBegin": "",
            "skuAvailableOrderEnd"  : "",
            "shelfDateBegin"        : "",
            "shelfDateEnd"          : "",
            "stockWarnStatusList"   : [],
            "labelFakeIdList"       : [],
            "sheinSaleByInventory"  : "",
            "tspIdList"             : [],
            "adviceStatus"          : [],
            "sortBy7dSaleCnt"       : 2
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))

        spu_list = response_text['info']['list']

        skc_list = [item['skc'] for item in spu_list]
        self.get_activity_label(skc_list)
        self.get_preemption_list(skc_list)
        self.get_sku_price_v2(skc_list)
        self.get_stock_advice(skc_list)

        total = response_text['info']['count']
        totalPage = math.ceil(total / pageSize)
        for page in range(2, totalPage + 1):
            log(f'获取备货信息商品列表 第{page}/{totalPage}页')
            payload['pageNumber'] = page
            response_text = fetch(self.web_page, url, payload)

            new_spu_list = response_text['info']['list']
            spu_list += new_spu_list

            skc_list = [item['skc'] for item in new_spu_list]
            self.get_activity_label(skc_list)
            self.get_preemption_list(skc_list)
            self.get_sku_price_v2(skc_list)
            self.get_stock_advice(skc_list)

            time.sleep(0.3)

        key = f'{self.store_username}'
        cache_file = f'{self.config.auto_dir}/shein/cache/bak_info_list_{key}.json'
        write_dict_to_file_ex(cache_file, {key: spu_list}, [key])

        return spu_list

    def get_skc_week_sale_list(self, spu, skc, start_from=None):
        dict_skc = self.get_dict_skc_week_trend_v2(spu, skc, start_from)
        date_list = TimeUtils.get_past_7_days_list(start_from)
        saleCnt7d = 0
        sales_detail = []
        for date in date_list:
            saleCnt = get_safe_value(dict_skc.get(date, {}), 'saleCnt', 0)
            epsUvIdx = get_safe_value(dict_skc.get(date, {}), 'epsUvIdx', 0)

            saleCnt7d += saleCnt
            sales_detail.append(f'{date}({TimeUtils.get_weekday_name(date)}): {saleCnt}/{epsUvIdx}')

        sales_data = []
        for date in date_list:
            goodsUvIdx = get_safe_value(dict_skc.get(date, {}), 'goodsUvIdx', 0)  # 商详访客
            epsGdsCtrIdx = get_safe_value(dict_skc.get(date, {}), 'epsGdsCtrIdx', 0)  # 点击率

            payUvIdx = get_safe_value(dict_skc.get(date, {}), 'payUvIdx', 0)  # 支付人数
            gdsPayCtrIdx = get_safe_value(dict_skc.get(date, {}), 'gdsPayCtrIdx', 0)  # 转化率

            sales_data.append(f'{date}({TimeUtils.get_weekday_name(date)}): {epsGdsCtrIdx:.2%}({goodsUvIdx})/{gdsPayCtrIdx:.2%}({payUvIdx})')

        return sales_detail, sales_data, saleCnt7d

    def stat_new_product_to_bak(self):
        # 直接调用 get_skc_week_actual_sales 來获取周销 计算是否能转成备货款
        skc_list = self.get_bak_base_info()  # 这个地方 不要加已上架和正常供货参数 直接取所有的skc列表
        # 以算昨日7.2日为例 上架天数为29天(转换成上架日期),且过去7天销量达到类目备货标准和没有达到备货标准的skc数量
        # 1.计算某个skc的上架日期
        # 2.计算某个skc的基于某个日期的过去7天销量
        # 3.获取叶子类目的备货标准
        header = ['店铺账号', '店铺名称', '店长', '统计日期', 'SKC图片', '商品信息', '新品成功转备货款', '第4周SKC销量/SKC曝光', '第4周SKC点击率/SKC转化率', 'SKC', 'SPU']
        excel_data = []
        stat_date_list = TimeUtils.get_dates_from_first_of_month_to_yesterday()
        for stat_date in stat_date_list:
            # 计算 stat_date 这天 的上架日期 是 filter_shelf_date
            filter_shelf_date = TimeUtils.get_past_nth_day(29, stat_date)
            log(f'stat_date:{stat_date},filter_shelf_date:{filter_shelf_date}')
            # 筛选 上架日期是 filter_shelf_date 这天的skc有哪些
            filter_skc_list = [skc_item for skc_item in skc_list if skc_item['shelfDate'] == filter_shelf_date]
            # 再统计 这些skc 在 stat_date 这天的 前7天销量
            # 看看这个7天销量是否达到了类目的备货标准 统计 计数
            for skc_item in filter_skc_list:
                skc = skc_item['skc']
                spu = skc_item['spu']
                log(f'skc:{skc}, spu:{spu}')

                row_item = []
                row_item.append(self.store_username)

                status_cn = skc_item.get('shelfStatus').get('name')
                goods_level = skc_item['goodsLevel']['name']
                goods_label = [label["name"] for label in skc_item['goodsLabelList']]
                store_info = f'{self.store_name}\n({status_cn})\n{goods_level}\n{",".join(goods_label).strip()}\n{stat_date_list[-1]}\n{stat_date_list[0]}'
                row_item.append(store_info)
                store_manager = self.config.shein_store_manager.get(str(self.store_username).lower())
                row_item.append(store_manager)
                row_item.append(stat_date)
                row_item.append(skc_item['picUrl'])

                standard_value = (skc_item.get('stockStandard') or {}).get('value') or 0

                sale_detail, sale_rate, sale_num = self.get_skc_week_sale_list(spu, skc, stat_date)
                success = int(standard_value > 0 and sale_num >= standard_value)

                categoryName = skc_item['categoryName']
                shelfDate = skc_item['shelfDate']
                product_info = (
                    f'SPU: {spu}\n'
                    f'SKC: {skc}\n'
                    f'上架日期: {shelfDate}\n'
                    f'类目: {categoryName}\n'
                    f'备货标准/第4周销: {standard_value}/{sale_num}\n'
                )
                row_item.append(product_info)
                row_item.append(success)
                row_item.append("\n".join(sale_detail))
                row_item.append("\n".join(sale_rate))
                row_item.append(skc)
                row_item.append(spu)
                excel_data.append(row_item)

        cache_file = f'{self.config.auto_dir}/shein/dict/new_product_to_bak_{TimeUtils.today_date()}.json'
        write_dict_to_file_ex(cache_file, {self.store_username: [header] + excel_data}, [self.store_username])

    def get_funds_data_lz(self):
        log(f'正在获取 {self.store_name} 财务数据')
        url = "https://sso.geiwohuo.com/sso/homePage/dataOverview/v2/detail"
        payload = {
            "metaIndexIds": [
                298,
                67,
                70,
                72
            ],
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        info = response_text.get('info')
        num298 = 0  # 在途商品金额
        num67 = 0  # 在仓商品金额
        num70 = 0  # 待结算金额
        num72 = 0  # 可提现金额
        for item in info['list']:
            if item['metaIndexId'] == 298:
                num298 = item['count']
            if item['metaIndexId'] == 67:
                num67 = item['count']
            if item['metaIndexId'] == 70:
                num70 = item['count']
            if item['metaIndexId'] == 72:
                num72 = item['count']

        outAmount = self.get_last_month_outbound_amount()
        store_manager = self.config.shein_store_manager.get(str(self.store_username).lower())
        NotifyItem = [f'{self.store_name}', self.store_username, store_manager, num298, num67, num70, num72, '', outAmount, '', '', '', TimeUtils.current_datetime()]
        log(NotifyItem)
        cache_file = f'{self.config.auto_dir}/shein/cache/stat_fund_lz_{TimeUtils.today_date()}.json'
        write_dict_to_file_ex(cache_file, {self.store_username: NotifyItem}, [self.store_username])
        return NotifyItem

    def get_funds_data(self):
        log(f'正在获取 {self.store_name} 财务数据')
        url = "https://sso.geiwohuo.com/sso/homePage/dataOverview/v2/detail"
        payload = {
            "metaIndexIds": [
                298,
                67,
                70,
                72
            ],
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        info = response_text.get('info')
        num298 = 0  # 在途商品金额
        num67 = 0  # 在仓商品金额
        num70 = 0  # 待结算金额
        num72 = 0  # 可提现金额
        for item in info['list']:
            if item['metaIndexId'] == 298:
                num298 = item['count']
            if item['metaIndexId'] == 67:
                num67 = item['count']
            if item['metaIndexId'] == 70:
                num70 = item['count']
            if item['metaIndexId'] == 72:
                num72 = item['count']

        outAmount = self.get_last_month_outbound_amount()
        dict_store = read_dict_from_file(self.config.shein_store_alias)
        store_manager = dict_store.get(str(self.store_username).lower())
        NotifyItem = [f'{self.store_name}', self.store_username, store_manager, num298, num67, num70, num72, outAmount, '',
                      TimeUtils.current_datetime()]

        cache_file = f'{self.config.auto_dir}/shein/cache/stat_fund_{TimeUtils.today_date()}.json'
        write_dict_to_file_ex(cache_file, {self.store_username: NotifyItem}, [self.store_username])
        return NotifyItem

    def getQueryDate(self):
        query_time = self.DictQueryTime.get(self.store_username, None)
        if query_time is not None:
            log(f'从字典获取query_time: {query_time}')
            return query_time
        log('获取日期范围')
        url = "https://sso.geiwohuo.com/mgs-api-prefix/estimate/queryDateRange"
        payload = {}
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        query_time = response_text.get('info').get('quality_goods_query_time')
        self.DictQueryTime.update({self.store_username: query_time})
        log(f'query_time: {query_time}')
        return query_time

    def get_goods_quality_estimate_list(self, query_date):
        cache_file = f'{self.config.auto_dir}/shein/dict/googs_estimate_{query_date}.json'
        estimate_list = read_dict_from_file_ex(cache_file, self.store_username, 3600 * 8)
        if len(estimate_list) > 0:
            return estimate_list

        page_num = 1
        page_size = 100

        url = f"https://sso.geiwohuo.com/mgs-api-prefix/estimate/queryNewQualityGoodsList"
        payload = {
            "page_no"   : page_num,
            "page_size" : page_size,
            "start_date": query_date,
            "end_date"  : query_date,
            "order_col" : "skc_sale_cnt_14d",
            "order_type": "desc"
        }
        response_text = fetch(self.web_page, url, payload, {'lan': 'CN'})
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))

        estimate_list = response_text['info']['data']
        total = response_text['info']['meta']['count']
        totalPage = math.ceil(total / page_size)

        for page in range(2, totalPage + 1):
            log(f'获取质量评估列表 第{page}/{totalPage}页')
            page_num = page
            payload['page'] = page_num
            response_text = fetch(self.web_page, url, payload)
            estimate_list = response_text['info']['data']
            time.sleep(0.1)

        write_dict_to_file_ex(cache_file, {self.store_username: estimate_list}, [self.store_username])
        return estimate_list

    # 已上架备货款A数量
    def get_product_bak_A_count(self):
        url = "https://sso.geiwohuo.com/idms/goods-skc/list"
        payload = {
            "pageNumber"            : 1,
            "pageSize"              : 10,
            "supplierCodes"         : "",
            "skcs"                  : "",
            "spu"                   : "",
            "c7dSaleCntBegin"       : "",
            "c7dSaleCntEnd"         : "",
            "goodsLevelIdList"      : [
                61,
                90
            ],
            "supplyStatus"          : "",
            "shelfStatus"           : 1,
            "categoryIdList"        : [],
            "skcStockBegin"         : "",
            "skcStockEnd"           : "",
            "skuStockBegin"         : "",
            "skuStockEnd"           : "",
            "skcSaleDaysBegin"      : "",
            "skcSaleDaysEnd"        : "",
            "skuSaleDaysBegin"      : "",
            "skuSaleDaysEnd"        : "",
            "planUrgentCountBegin"  : "",
            "planUrgentCountEnd"    : "",
            "skcAvailableOrderBegin": "",
            "skcAvailableOrderEnd"  : "",
            "skuAvailableOrderBegin": "",
            "skuAvailableOrderEnd"  : "",
            "shelfDateBegin"        : "",
            "shelfDateEnd"          : "",
            "stockWarnStatusList"   : [],
            "labelFakeIdList"       : [],
            "sheinSaleByInventory"  : "",
            "tspIdList"             : [],
            "adviceStatus"          : [],
            "sortBy7dSaleCnt"       : 2,
            "goodsLevelFakeIdList"  : [
                3
            ]
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        info = response_text.get('info')
        count = info.get('count', 0)
        log('获取已上架备货款A数量', count)
        return count

    # 已上架备货款B数量
    def get_product_bak_B_count(self):
        url = "https://sso.geiwohuo.com/idms/goods-skc/list"
        payload = {
            "pageNumber"            : 1,
            "pageSize"              : 10,
            "supplierCodes"         : "",
            "skcs"                  : "",
            "spu"                   : "",
            "c7dSaleCntBegin"       : "",
            "c7dSaleCntEnd"         : "",
            "goodsLevelIdList"      : [
                62,
                227,
                12,
                230,
                80,
                58,
                224
            ],
            "supplyStatus"          : "",
            "shelfStatus"           : 1,
            "categoryIdList"        : [],
            "skcStockBegin"         : "",
            "skcStockEnd"           : "",
            "skuStockBegin"         : "",
            "skuStockEnd"           : "",
            "skcSaleDaysBegin"      : None,
            "skcSaleDaysEnd"        : "",
            "skuSaleDaysBegin"      : "",
            "skuSaleDaysEnd"        : "",
            "planUrgentCountBegin"  : "",
            "planUrgentCountEnd"    : "",
            "skcAvailableOrderBegin": "",
            "skcAvailableOrderEnd"  : "",
            "skuAvailableOrderBegin": None,
            "skuAvailableOrderEnd"  : "",
            "shelfDateBegin"        : "",
            "shelfDateEnd"          : "",
            "stockWarnStatusList"   : [],
            "labelFakeIdList"       : [],
            "sheinSaleByInventory"  : "",
            "tspIdList"             : [],
            "adviceStatus"          : [],
            "sortBy7dSaleCnt"       : 2,
            "goodsLevelFakeIdList"  : [
                4
            ]
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        info = response_text.get('info')
        count = info.get('count', 0)
        log('获取已上架备货款B数量', count)
        return count

    # 已上架新款A数量
    def get_product_A_count(self):
        url = "https://sso.geiwohuo.com/idms/goods-skc/list"
        payload = {
            "pageNumber"            : 1,
            "pageSize"              : 10,
            "supplierCodes"         : "",
            "skcs"                  : "",
            "spu"                   : "",
            "c7dSaleCntBegin"       : "",
            "c7dSaleCntEnd"         : "",
            "goodsLevelIdList"      : [
                107
            ],
            "supplyStatus"          : "",
            "shelfStatus"           : 1,
            "categoryIdList"        : [],
            "skcStockBegin"         : "",
            "skcStockEnd"           : "",
            "skuStockBegin"         : "",
            "skuStockEnd"           : "",
            "skcSaleDaysBegin"      : None,
            "skcSaleDaysEnd"        : "",
            "skuSaleDaysBegin"      : "",
            "skuSaleDaysEnd"        : "",
            "planUrgentCountBegin"  : "",
            "planUrgentCountEnd"    : "",
            "skcAvailableOrderBegin": "",
            "skcAvailableOrderEnd"  : "",
            "skuAvailableOrderBegin": None,
            "skuAvailableOrderEnd"  : "",
            "shelfDateBegin"        : "",
            "shelfDateEnd"          : "",
            "stockWarnStatusList"   : [],
            "labelFakeIdList"       : [],
            "sheinSaleByInventory"  : "",
            "tspIdList"             : [],
            "adviceStatus"          : [],
            "sortBy7dSaleCnt"       : 2,
            "goodsLevelFakeIdList"  : [
                2
            ]
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        info = response_text.get('info')
        count = info.get('count', 0)
        log('获取已上架新款A数量', count)
        return count

    # 本周已上架数量
    def get_week_shelf_product_count(self, start_date, end_date):
        url = "https://sso.geiwohuo.com/idms/goods-skc/list"
        payload = {
            "pageNumber"            : 1,
            "pageSize"              : 10,
            "supplierCodes"         : "",
            "skcs"                  : "",
            "spu"                   : "",
            "c7dSaleCntBegin"       : "",
            "c7dSaleCntEnd"         : "",
            "goodsLevelIdList"      : [],
            "supplyStatus"          : "",
            "shelfStatus"           : 1,
            "categoryIdList"        : [],
            "skcStockBegin"         : "",
            "skcStockEnd"           : "",
            "skuStockBegin"         : "",
            "skuStockEnd"           : "",
            "skcSaleDaysBegin"      : "",
            "skcSaleDaysEnd"        : "",
            "skuSaleDaysBegin"      : "",
            "skuSaleDaysEnd"        : "",
            "planUrgentCountBegin"  : "",
            "planUrgentCountEnd"    : "",
            "skcAvailableOrderBegin": "",
            "skcAvailableOrderEnd"  : "",
            "skuAvailableOrderBegin": "",
            "skuAvailableOrderEnd"  : "",
            "shelfDateBegin"        : start_date,
            "shelfDateEnd"          : end_date,
            "stockWarnStatusList"   : [],
            "labelFakeIdList"       : [],
            "sheinSaleByInventory"  : "",
            "tspIdList"             : [],
            "adviceStatus"          : [],
            "sortBy7dSaleCnt"       : 2
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        info = response_text.get('info')
        count = info.get('count', 0)
        log('获取本周上架数量')
        return count

    # 已上架数量
    def get_shelf_product_count(self):
        log('获取所有已上架数量')
        url = "https://sso.geiwohuo.com/spmp-api-prefix/spmp/product/list?page_num=1&page_size=10"
        payload = {
            "language"              : "zh-cn",
            "only_recommend_resell" : False,
            "only_spmb_copy_product": False,
            "search_abandon_product": False,
            "shelf_type"            : "ON_SHELF",
            "sort_type"             : 1
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))

        info = response_text.get('info')
        customObj = info.get('meta').get('customObj')
        # 将数据转换成字典
        result = {item["shelf_status"]: item["count"] for item in customObj}
        return result

    def get_yesterday_upload_product_count(self, dt=None):
        url = "https://sso.geiwohuo.com/spmp-api-prefix/spmp/product/publish/record/page_list?page_num=1&page_size=100"
        payload = {
            "edit_type"                   : 0,
            "language"                    : "zh-cn",
            "only_current_month_recommend": False,
            "only_spmb_copy_product"      : False,
            "query_time_out"              : False,
            "search_diy_custom"           : False
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        info = response_text.get('info')
        count = 0
        for item in info.get('data', {}):
            if TimeUtils.is_yesterday(item['create_time'], dt):
                count += 1
        log('获取昨日已上传数量', count)
        return count

    def get_week_sales_stat_detail(self):
        dt = self.get_dt_time()
        yesterday = TimeUtils.get_yesterday(dt)
        date_7_days_ago = TimeUtils.get_past_nth_day(6, None, '%Y-%m-%d')
        log('-7', date_7_days_ago)
        date_1_days_ago = TimeUtils.get_past_nth_day(1, None, '%Y-%m-%d')
        log('-1', date_1_days_ago)

        url = "https://sso.geiwohuo.com/sbn/index/get_critical_indicator_curve_chart"
        payload = {
            "areaCd"     : "cn",
            "dt"         : dt,
            "countrySite": [
                "shein-all"
            ],
            "startDate"  : date_7_days_ago,
            "endDate"    : date_1_days_ago,
            "queryType"  : 1,
            "pageNum"    : 1,
            "pageSize"   : 100
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        info = response_text.get('info', {})

        last_item = SheinStoreSalesDetailManager(self.config.database_url).get_records_as_dict(self.store_username, yesterday)
        log('last_item', last_item)
        day_item = info[-1]
        item = {}
        item["store_username"] = self.store_username
        item["store_name"] = self.store_name
        item["day"] = day_item["dataDate"]
        item["sales_num"] = day_item["saleCnt1d"]
        item['sales_num_inc'] = item['sales_num'] - last_item.get('sales_num', 0)
        item['sales_amount'] = day_item['dealAmt1d']
        item['sales_amount_inc'] = item['sales_amount'] - float(last_item.get('sales_amount', 0))
        item['visitor_num'] = day_item['idxShopGoodsUv1d']
        item['visitor_num_inc'] = item['visitor_num'] - last_item.get('visitor_num', 0)
        item['bak_A_num'] = self.get_product_bak_A_count()
        item['bak_A_num_inc'] = item['bak_A_num'] - last_item.get('bak_A_num', 0)
        item['new_A_num'] = self.get_product_A_count()
        item['new_A_num_inc'] = item['new_A_num'] - last_item.get('new_A_num', 0)
        dictProduct = self.get_shelf_product_count()
        item['on_sales_product_num'] = dictProduct.get('ON_SHELF')
        item['on_sales_product_num_inc'] = item['on_sales_product_num'] - last_item.get('on_sales_product_num', 0)
        item['wait_shelf_product_num'] = dictProduct.get('WAIT_SHELF')
        item['wait_shelf_product_num_inc'] = item['wait_shelf_product_num'] - last_item.get('wait_shelf_product_num', 0)
        item['upload_product_num'] = self.get_yesterday_upload_product_count()
        item['upload_product_num_inc'] = item['upload_product_num'] - last_item.get('upload_product_num', 0)
        item['sold_out_product_num'] = dictProduct.get('SOLD_OUT')
        item['shelf_off_product_num'] = dictProduct.get('OUT_SHELF')

        SheinStoreSalesDetailManager(self.config.database_url).insert_data([item])

    def get_delivery_order_list(self, orderType=2):
        page_num = 1
        page_size = 200

        url = f"https://sso.geiwohuo.com/pfmp/order/list"
        payload = {}
        if orderType == 1:
            payload = {
                "orderType": orderType,
                "page"     : page_num,
                "perPage"  : page_size,
                "status"   : [2],
            }
        elif orderType == 2:
            payload = {
                "orderType" : orderType,
                "page"      : page_num,
                "perPage"   : page_size,
                "status"    : [2],
                "isJitOrder": 2
            }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))

        spu_list = response_text['info']['data']
        total = response_text['info']['meta']['count']
        totalPage = math.ceil(total / page_size)

        skc_list = [item['goods']['skcName'] for item in spu_list]
        self.get_activity_label(skc_list)

        for page in range(2, totalPage + 1):
            log(f'获取订单列表 第{page}/{totalPage}页')
            page_num = page
            if orderType == 1:
                payload = {
                    "orderType": orderType,
                    "page"     : page_num,
                    "perPage"  : page_size,
                    "status"   : [2],
                }
            elif orderType == 2:
                payload = {
                    "orderType" : orderType,
                    "page"      : page_num,
                    "perPage"   : page_size,
                    "status"    : [2],
                    "isJitOrder": 2
                }
            response_text = fetch(self.web_page, url, payload)
            spu_list_new = response_text['info']['data']
            skc_list = [item['goods']['skcName'] for item in spu_list_new]
            self.get_activity_label(skc_list)
            spu_list += spu_list_new
            time.sleep(0.3)

        if len(spu_list) == 0:
            log(f'无{["", "急采", "备货"][orderType]}发货单')
            return None

        write_to_excel = [
            # 0          1        2          3          4          5          6     7
            ['店铺名称', 'SKC图片', 'SKU图片', '商品信息', '下单/需求数量', '库存(模式/本地/在途/希音)', '成本价', '核价',
             '近7天SKU销量/SKC销量/SKC曝光', 'SKC点击率/SKC转化率', '自主参与活动', '最晚预约上门取件', '要求实际完成取件',
             'SKC', 'SKU']
        ]
        cache_file2 = f'{self.config.auto_dir}/shein/dict/skc_shelf_{self.store_username}.json'
        DictSkcShelf = read_dict_from_file(cache_file2)
        cache_file3 = f'{self.config.auto_dir}/shein/dict/skc_product_{self.store_username}.json'
        DictSkcProduct = read_dict_from_file(cache_file3)
        cache_file = f'{self.config.auto_dir}/shein/dict/activity_price_{self.store_name}.json'
        dictActivityPrice = read_dict_from_file(cache_file)
        cache_file4 = f'{self.config.auto_dir}/shein/dict/dict_sku_info_{self.store_username}.json'
        DictSkuInfo = read_dict_from_file(cache_file4)
        for spu_item in spu_list:
            skc = spu_item['goods']['skcName']
            skcCode = spu_item['goods']['supplierCode']
            skc_img = str(spu_item['goods']['imgPath'])
            orderNum = spu_item['sellerOrderNo']
            orderTime = spu_item['allocateTime']
            requestTakeParcelTime = spu_item['requestTakeParcelTime']
            suggestedReserveTime = spu_item['suggestedReserveTime']
            good_level = spu_item['goods']['goodsLevelName']

            self.get_skc_week_actual_sales(skc)

            spu = DictSkcProduct[skc]['spu_name']
            log('spu', spu)
            for sku_item in spu_item['detail']:
                needQuantity = sku_item['needQuantity']
                orderQuantity = sku_item['orderQuantity']
                # sku_img = sku_item['skuThumb']
                skuCode = sku_item['supplierSku']
                stock = self.bridge.get_sku_stock(skuCode, 'mb')
                cost_price = self.bridge.get_sku_cost(skuCode, 'mb')
                suffixZh = sku_item['suffixZh']
                sku = sku_item['skuCode']
                supplyPrice = sku_item['supplyPrice']
                sku_img = self.bridge.get_sku_img(skuCode, 'mb')
                sale_model = DictSkuInfo[skuCode][0]
                shein_stock = DictSkuInfo[skuCode][1]
                shelf_days = DictSkuInfo[skuCode][2]
                real_transit = DictSkuInfo[skuCode][3]
                stock_str = f'{sale_model}\n{stock}/{real_transit}/{shein_stock}'

                item = []
                item.append(f'{self.store_name}\n{good_level}')
                item.append(skc_img)
                item.append(sku_img)
                if cost_price == '-':
                    profit = '-'
                else:
                    profit = f'{float(supplyPrice) - float(cost_price):.2f}'
                # item.append(f'订单号: {orderNum}\n下单时间: {orderTime}\n最晚预约上门取件: {suggestedReserveTime}\nSKC: {skc}\nSKC货号: {skcCode}\nSKU货号: {skuCode}\n属性集: {suffixZh}\n上架时间: {DictSkcShelf[skc]}\n上架天数: {shelf_days}\n成本/核价/利润: ¥{cost_price}/¥{supplyPrice}/¥{profit}\n下单/需求数量: {orderQuantity}/{needQuantity}\n库存模式/本地/在途/希音: {sale_model}/{stock}/{real_transit}/{shein_stock}\n')
                item.append(f'订单号: {orderNum}\n下单时间: {orderTime}\n最晚预约上门取件: {suggestedReserveTime}\nSKC: {skc}\nSKC货号: {skcCode}\nSKU货号: {skuCode}\n属性集: {suffixZh}\n上架时间: {DictSkcShelf[skc]}\n上架天数: {shelf_days}\n成本/核价/利润: ¥{cost_price}/¥{supplyPrice}/¥{profit}')
                item.append(f'[{orderQuantity}/{needQuantity}]')
                item.append(stock_str)
                item.append(cost_price)
                item.append(supplyPrice)
                sale_num_list, sale_data_list = self.get_sku_week_sale_list(spu, skc, sku)
                item.append("\n".join(sale_num_list))
                item.append("\n".join(sale_data_list))
                item.append(self.get_skc_activity_label(skc, sku, dictActivityPrice))
                item.append(suggestedReserveTime)
                item.append(requestTakeParcelTime)
                item.append(skc)
                item.append(sku)
                write_to_excel.append(item)

        cache_file = f'{self.config.auto_dir}/shein/cache/jit_{TimeUtils.today_date()}_{orderType}_{TimeUtils.get_period()}.json'
        write_dict_to_file_ex(cache_file, {self.store_username: write_to_excel}, {self.store_username})

        return write_to_excel

    # 获取商品包含sku销量的列表
    def get_dict_sku_stock_detail(self):
        log(f'获取备货信息商品列表 做成字典')
        url = "https://sso.geiwohuo.com/idms/goods-skc/list"
        pageNumber = 1
        pageSize = 100
        dictPayload = {
            "pageNumber"            : pageNumber,
            "pageSize"              : pageSize,
            "supplierCodes"         : "",
            "skcs"                  : "",
            "spu"                   : "",
            "c7dSaleCntBegin"       : "",
            "c7dSaleCntEnd"         : "",
            "goodsLevelIdList"      : [],
            "supplyStatus"          : "",
            "shelfStatus"           : "",
            "categoryIdList"        : [],
            "skcStockBegin"         : "",
            "skcStockEnd"           : "",
            "skuStockBegin"         : "",
            "skuStockEnd"           : "",
            "skcSaleDaysBegin"      : "",
            "skcSaleDaysEnd"        : "",
            "skuSaleDaysBegin"      : "",
            "skuSaleDaysEnd"        : "",
            "planUrgentCountBegin"  : "",
            "planUrgentCountEnd"    : "",
            "skcAvailableOrderBegin": "",
            "skcAvailableOrderEnd"  : "",
            "skuAvailableOrderBegin": "",
            "skuAvailableOrderEnd"  : "",
            "shelfDateBegin"        : "",
            "shelfDateEnd"          : "",
            "stockWarnStatusList"   : [],
            "labelFakeIdList"       : [],
            "sheinSaleByInventory"  : "",
            "tspIdList"             : [],
            "adviceStatus"          : [],
            "sortBy7dSaleCnt"       : 2
        }
        payload = dictPayload
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))

        spu_list = response_text['info']['list']

        total = response_text['info']['count']
        totalPage = math.ceil(total / pageSize)
        for page in range(2, totalPage + 1):
            log(f'获取备货信息商品列表 第{page}/{totalPage}页')
            dictPayload['pageNumber'] = page
            payload = dictPayload
            response_text = fetch(self.web_page, url, payload)
            spu_list_new = response_text['info']['list']
            spu_list += spu_list_new
            time.sleep(0.3)

        DictSkuInfo = {}
        for spu_info in spu_list:
            sale_model = spu_info.get('saleModel', {}).get('name') if spu_info.get('saleModel') else '-'
            shelfDays = spu_info['shelfDays']
            for sku_info in spu_info['skuList']:
                attr = sku_info['attr']
                if attr == '合计':
                    continue
                skuExtCode = str(sku_info['supplierSku'])
                shein_stock = sku_info['stock']

                transit = sku_info['transit']  # 在途
                real_transit = transit + sku_info['stayShelf'] - sku_info['transitSale']

                DictSkuInfo[skuExtCode] = [sale_model, shein_stock, shelfDays, real_transit]

        write_dict_to_file(f'{self.config.auto_dir}/shein/dict/dict_sku_info_{self.store_username}.json', DictSkuInfo)

        return DictSkuInfo

    def get_shop_notify_num(self):
        log(f'正在获取 {self.store_name} 通知数据')
        url = "https://sso.geiwohuo.com/sso/homePage/v4/detail"
        payload = {
            "metaIndexIds": [
                246,  # 急采-待发货
                245  # 备货-待发货
            ],
            "templateType": 0
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        info = response_text.get('info')

        cache_file = f'{self.config.auto_dir}/shein/notify/{self.store_name}_{TimeUtils.get_current_datetime()}.json'
        write_dict_to_file(cache_file, info)

        num245 = 0
        num246 = 0
        for item in info['list']:
            if item['metaIndexId'] == 245:
                num245 = item['count']
            if item['metaIndexId'] == 246:
                num246 = item['count']

        NotifyItem = [self.store_name, num246, num245]

        cache_file = f'{self.config.auto_dir}/shein/cache/jit_notify_{TimeUtils.today_date()}.json'
        write_dict_to_file_ex(cache_file, {self.store_username: NotifyItem}, {self.store_username})

        return info

    def get_activity_list(self):
        url = "https://sso.geiwohuo.com/mrs-api-prefix/mbrs/activity/get_activity_list?page_num=1&page_size=100"
        payload = {}
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        total = response_text.get('info', {}).get('total_count')
        excel_data = [[
            '店铺名称', '活动信息', '已报数量', '可报数量'
        ]]
        if total > 0:
            for item in response_text.get('info', {}).get('activity_detail_list'):
                activity_tag = item.get('text_tag_content')
                activity_name = item['activity_name']
                start_time = item['activity_start_zone_time']
                end_time = item['activity_end_zone_time']
                start_time2 = item['start_zone_time']
                end_time2 = item['end_zone_time']
                allow_goods_num = item.get('allow_goods_num')
                apply_goods_num = item.get('apply_goods_num')
                row_item = [
                    self.store_name,
                    f"活动名称: 【{activity_tag}】{activity_name}\n报名时间: {start_time}~{end_time}\n活动时间: {start_time2}~{end_time2}\n已报数量: {apply_goods_num}/{allow_goods_num}",
                    apply_goods_num,
                    allow_goods_num,
                ]
                excel_data.append(row_item)
                cache_file = f'{self.config.auto_dir}/shein/activity_list/activity_list_{TimeUtils.today_date()}.json'
                write_dict_to_file_ex(cache_file, {self.store_username: excel_data}, [self.store_username])

    def get_product_list(self):
        # self.web_page.goto('https://sso.geiwohuo.com/#/spmp/commdities/list')
        # self.web_page.wait_for_load_state("load")

        cache_file = f'{self.config.auto_dir}/shein/dict/product_list_{self.store_username}.json'
        DictSpuInfo = read_dict_from_file(cache_file, 3600)
        if len(DictSpuInfo) > 0:
            return DictSpuInfo

        page_num = 1
        page_size = 100

        url = f"https://sso.geiwohuo.com/spmp-api-prefix/spmp/product/list?page_num={page_num}&page_size={page_size}"
        payload = {
            "language"              : "zh-cn",
            "only_recommend_resell" : False,
            "only_spmb_copy_product": False,
            "search_abandon_product": False,
            "sort_type"             : 1
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))

        spu_list = response_text['info']['data']
        total = response_text['info']['meta']['count']
        totalPage = math.ceil(total / page_size)

        for page_num in range(2, totalPage + 1):
            log(f'获取商品列表 第{page_num}/{totalPage}页')
            url = f"https://sso.geiwohuo.com/spmp-api-prefix/spmp/product/list?page_num={page_num}&page_size={page_size}"
            response_text = fetch(self.web_page, url, payload)
            spu_list_new = response_text['info']['data']
            spu_list += spu_list_new
            time.sleep(0.3)

        DictSkcShelf = {}
        DictSkcProduct = {}
        DictSpuInfo = {}
        for spu_item in spu_list:
            spu = spu_item['spu_name']
            first_shelf_time = spu_item['first_shelf_time']
            for skc_item in spu_item['skc_info_list']:
                skc_name = skc_item['skc_name']
                DictSkcShelf[skc_name] = first_shelf_time
                DictSkcProduct[skc_name] = spu_item
            DictSpuInfo[spu] = spu_item

        cache_file2 = f'{self.config.auto_dir}/shein/dict/skc_shelf_{self.store_username}.json'
        write_dict_to_file(cache_file2, DictSkcShelf)
        cache_file3 = f'{self.config.auto_dir}/shein/dict/skc_product_{self.store_username}.json'
        write_dict_to_file(cache_file3, DictSkcProduct)

        write_dict_to_file(cache_file, DictSpuInfo)
        return DictSpuInfo

    def query_obm_activity_list(self):
        page_num = 1
        page_size = 100
        date_60_days_ago = TimeUtils.get_past_nth_day(59)
        cache_file = f'{self.config.auto_dir}/shein/cache/obm_activity_{self.store_name}_{date_60_days_ago}_{TimeUtils.today_date()}.json'
        list_item = read_dict_from_file(cache_file, 3600 * 8)
        if len(list_item) > 0:
            return list_item

        url = f"https://sso.geiwohuo.com/mrs-api-prefix/promotion/obm/query_obm_activity_list"
        payload = {
            "insert_end_time"  : f"{TimeUtils.today_date()} 23:59:59",
            "insert_start_time": f"{date_60_days_ago} 00:00:00",
            "page_num"         : page_num,
            "page_size"        : page_size,
            "system"           : "mrs",
            "time_zone"        : "Asia/Shanghai",
            # "state": 3, # 活动开启中 不能用这个条件
            "type_id"          : 31  # 限时折扣
        }

        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))

        list_item = response_text['info']['data']
        total = response_text['info']['meta']['count']
        totalPage = math.ceil(total / page_size)

        for page in range(2, totalPage + 1):
            log(f'获取营销工具列表 第{page}/{totalPage}页')
            payload["page_num"] = page
            response_text = fetch(self.web_page, url, payload)
            list_item += response_text['info']['data']
            time.sleep(0.1)

        write_dict_to_file(cache_file, list_item)
        return list_item

    def query_goods_detail(self, activity_id):
        # web_page.goto(f'https://sso.geiwohuo.com/#/mrs/tools/activity/obm-time-limit-info/{activity_id}')
        # web_page.wait_for_load_state('load')
        log(f'正在获取 {self.store_name} {activity_id} 营销工具商品详情')

        cache_file = f'{self.config.auto_dir}/shein/cache/query_goods_detail_{activity_id}.json'
        list_item = read_dict_from_file(cache_file, 3600 * 8)
        if len(list_item) > 0:
            return list_item

        page_num = 1
        page_size = 100
        url = "https://sso.geiwohuo.com/mrs-api-prefix/promotion/simple_platform/query_goods_detail"
        payload = {
            "activity_id": activity_id,
            "page_num"   : page_num,
            "page_size"  : page_size
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        list_item = response_text['info']['data']
        total = response_text['info']['meta']['count']
        totalPage = math.ceil(total / page_size)

        for page in range(2, totalPage + 1):
            log(f'获取营销工具商品列表 第{page}/{totalPage}页')
            payload["page_num"] = page
            response_text = fetch(self.web_page, url, payload)
            list_item += response_text['info']['data']
            time.sleep(0.1)

        write_dict_to_file(cache_file, list_item)
        return list_item

    def get_partake_activity_goods_list(self):
        # self.web_page.goto(f'https://sso.geiwohuo.com/#/mbrs/marketing/list/1')
        # self.web_page.wait_for_load_state('load')
        log(f'正在获取 {self.store_name} 活动列表')
        page_num = 1
        page_size = 100
        date_60_days_ago = TimeUtils.get_past_nth_day(59)
        cache_file = f'{self.config.auto_dir}/shein/cache/platform_activity_{self.store_name}_{date_60_days_ago}_{TimeUtils.today_date()}.json'
        list_item = read_dict_from_file(cache_file, 3600 * 8)
        if len(list_item) > 0:
            return list_item

        url = f"https://sso.geiwohuo.com/mrs-api-prefix/mbrs/activity/get_partake_activity_goods_list?page_num={page_num}&page_size={page_size}"
        payload = {
            "goods_audit_status"    : 1,
            "insert_zone_time_end"  : f"{TimeUtils.today_date()} 23:59:59",
            "insert_zone_time_start": f"{date_60_days_ago} 00:00:00"
        }

        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        list_item = response_text['info']['data']
        total = response_text['info']['meta']['count']
        totalPage = math.ceil(total / page_size)

        for page in range(2, totalPage + 1):
            log(f'获取活动列表 第{page}/{totalPage}页')
            payload["page_num"] = page
            response_text = fetch(self.web_page, url, payload)
            list_item += response_text['info']['data']
            time.sleep(0.1)

        write_dict_to_file(cache_file, list_item)
        return list_item

    def generate_activity_price_dict(self):
        cache_file = f'{self.config.auto_dir}/shein/dict/activity_price_{self.store_name}.json'
        dict_activity_price = {}
        activity_list = self.query_obm_activity_list()
        for activity in activity_list:
            activity_id = activity['activity_id']
            activity_name = activity['act_name']
            sub_type_id = activity['sub_type_id']  # 1.不限量 2.限量
            dateBegin = TimeUtils.convert_datetime_to_date(activity['start_time'])
            dateEnd = TimeUtils.convert_datetime_to_date(activity['end_time'])
            skc_list = self.query_goods_detail(activity_id)
            for skc_item in skc_list:
                attend_num_sum = skc_item['attend_num_sum']
                product_act_price = skc_item['product_act_price']  # 活动价
                if sub_type_id == 1:
                    attend_num_sum = '不限量'
                for sku_item in skc_item['sku_info_list']:
                    sku = sku_item['sku']  # 平台sku
                    product_act_price = sku_item['product_act_price'] if sku_item[
                        'product_act_price'] else product_act_price  # 活动价
                    key = f'{sku}_{dateBegin}_{dateEnd}_{activity_name}'
                    dict_activity_price[key] = [product_act_price, attend_num_sum]

        platform_activity_list = self.get_partake_activity_goods_list()
        for platform_activity in platform_activity_list:
            activity_name = platform_activity['activity_name']
            text_tag_content = platform_activity['text_tag_content']
            attend_num = platform_activity['attend_num']
            dateBegin = TimeUtils.convert_timestamp_to_date(platform_activity['start_time'])
            dateEnd = TimeUtils.convert_timestamp_to_date(platform_activity['end_time'])
            if text_tag_content != '新品':
                attend_num = '-'
            for sku_item in platform_activity['activity_sku_list']:
                sku = sku_item['sku_code']
                enroll_price = sku_item['enroll_display_str'][:-3]
                key = f'{sku}_{dateBegin}_{dateEnd}_{activity_name}'
                dict_activity_price[key] = [enroll_price, attend_num]

        write_dict_to_file(cache_file, dict_activity_price)

    def get_skc_week_actual_sales(self, skc):
        first_day, last_day = TimeUtils.get_past_7_days_range()
        cache_file = f'{self.config.auto_dir}/shein/cache/{skc}_{first_day}_{last_day}.json'
        if datetime.now().hour >= 9:
            DictSkuSalesDate = read_dict_from_file(cache_file)
        else:
            DictSkuSalesDate = read_dict_from_file(cache_file, 1800)
        if len(DictSkuSalesDate) > 0:
            return DictSkuSalesDate

        url = f"https://sso.geiwohuo.com/idms/sale-trend/detail"
        payload = {
            "skc"      : skc,
            "startDate": first_day,
            "endDate"  : last_day,
            "daysToAdd": 0
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            log(response_text)
            return {}
        list_item = response_text['info']['salesVolumeDateVoList']
        for item in list_item:
            key = item['date']
            DictSkuSalesDate[key] = item['salesVolumeMap']
        list_item2 = response_text['info']['actualSalesVolumeMap']
        for item in list_item2:
            sku = item['skuCode']
            if sku is not None:
                DictSkuSalesDate[sku] = item['actualSalesVolume']

        write_dict_to_file(cache_file, DictSkuSalesDate)
        return DictSkuSalesDate

    def get_preemption_list(self, skc_list):
        url = f"https://sso.geiwohuo.com/idms/goods-skc/preemption-num"
        payload = skc_list
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))

        dict = response_text['info']

        cache_file = f'{self.config.auto_dir}/shein/preemption_num/preemption_num_{self.store_username}.json'
        dict_preemption_num = read_dict_from_file(cache_file)
        dict_preemption_num.update(dict)
        write_dict_to_file(cache_file, dict_preemption_num)

        return dict

    def get_activity_label(self, skc_list):
        url = f"https://sso.geiwohuo.com/idms/goods-skc/activity-label"
        payload = skc_list
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        dict = response_text['info']

        cache_file = f'{self.config.auto_dir}/shein/activity_label/activity_label_{self.store_username}.json'
        dict_label = read_dict_from_file(cache_file)
        dict_label.update(dict)
        write_dict_to_file(cache_file, dict_label)

        return dict

    def get_sku_price_v2(self, skc_list):
        log(f'获取sku价格列表', skc_list)
        url = "https://sso.geiwohuo.com/idms/goods-skc/price"
        response_text = fetch(self.web_page, url, skc_list)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        dict = response_text['info']

        cache_file = f'{self.config.auto_dir}/shein/sku_price/sku_price_{self.store_username}.json'
        dict_sku_price = read_dict_from_file(cache_file)
        dict_sku_price.update(dict)
        write_dict_to_file(cache_file, dict_sku_price)

        return dict

    def get_stock_advice(self, skc_list):
        log(f'获取sku库存建议列表', skc_list)
        url = f"https://sso.geiwohuo.com/idms/goods-skc/get-vmi-spot-advice"
        payload = skc_list
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        dict = response_text['info']

        cache_file = f'{self.config.auto_dir}/shein/vmi_spot_advice/spot_advice_{self.store_username}.json'
        dict_advice = read_dict_from_file(cache_file)
        dict_advice.update(dict)
        write_dict_to_file(cache_file, dict_advice)

        return dict

    def get_dt_time(self):
        if self.dt is not None:
            log(f'字典dt: {self.dt}')
            return self.dt
        log('获取非实时更新时间')
        url = "https://sso.geiwohuo.com/sbn/common/get_update_time"
        payload = {
            "pageCode": "Index",
            "areaCd"  : "cn"
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        self.dt = response_text.get('info').get('dt')
        log(f'dt: {self.dt}')
        return self.dt

    def get_dict_skc_week_trend(self):
        page_num = 1
        page_size = 100

        date_7_days_ago = TimeUtils.get_past_nth_day(7, None, '%Y%m%d')
        log('-7', date_7_days_ago)
        date_1_days_ago = TimeUtils.get_past_nth_day(1, None, '%Y%m%d')
        log('-1', date_1_days_ago)

        url = f"https://sso.geiwohuo.com/sbn/new_goods/get_skc_diagnose_list"
        payload = {
            "areaCd"     : "cn",
            "countrySite": [
                "shein-all"
            ],
            "startDate"  : date_7_days_ago,
            "endDate"    : date_1_days_ago,
            "pageNum"    : page_num,
            "pageSize"   : page_size
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        spu_list = response_text['info']['data']
        total = response_text['info']['meta']['count']
        totalPage = math.ceil(total / page_size)

        for page in range(2, totalPage + 1):
            log(f'获取商品列表 第{page}/{totalPage}页')
            page_num = page
            payload = {
                "areaCd"     : "cn",
                "countrySite": [
                    "shein-all"
                ],
                "startDate"  : date_7_days_ago,
                "endDate"    : date_1_days_ago,
                "pageNum"    : page_num,
                "pageSize"   : page_size
            }
            response_text = fetch(self.web_page, url, payload)
            spu_list_new = response_text['info']['data']
            spu_list += spu_list_new
            time.sleep(0.3)

        DictSkcWeekTrend = {}
        for spu_item in spu_list:
            skc = str(spu_item['skc'])
            DictSkcWeekTrend[skc] = spu_item

        log('len(DictSkcWeekTrend)', len(DictSkcWeekTrend))
        write_dict_to_file(f'{self.config.auto_dir}/shein/dict/dict_skc_week_trend_{self.store_username}.json', DictSkcWeekTrend)
        return DictSkcWeekTrend

    def get_skc_sales(self, skc, start_date, end_date):
        url = "https://sso.geiwohuo.com/idms/stockadvice/saleTrendDetail"
        payload = {
            "skc"      : skc,
            "startDate": start_date,
            "endDate"  : end_date
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        error_msg = response_text.get('msg')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))

        sales_list = response_text['info']['saleTrendDetailList']
        if sales_list:
            for skc_list in sales_list:
                date = skc_list['date']
                if date == '合计':
                    log('无销量skc: ', skc)
                    continue
                skc_sale = skc_list['skcSale']
                skc_order = skc_list['skcOrder']
                for sku_list in skc_list['skuSaleTrendDetailList']:
                    sku = sku_list['skuCode']
                    attr_name = sku_list['attributeName']
                    sku_sale = sku_list['skuSale']
                    sku_order = sku_list['skuOrder']
                    if sku_sale > 0:
                        insert_sales(skc, date, skc_sale, skc_order, sku, attr_name, sku_sale, sku_order)
        return sales_list

    # 获取商品包含sku销量的列表
    def get_product_sku_sales_list(self, source='mb'):
        log(f'获取销量列表')
        url = "https://sso.geiwohuo.com/idms/goods-skc/list"
        pageNumber = 1
        pageSize = 100
        dictPayload = {
            "pageNumber"            : pageNumber,
            "pageSize"              : pageSize,
            "supplierCodes"         : "",
            "skcs"                  : "",
            "spu"                   : "",
            "c7dSaleCntBegin"       : "",
            "c7dSaleCntEnd"         : "",
            "goodsLevelIdList"      : [],
            "supplyStatus"          : "",
            "shelfStatus"           : 1,
            "categoryIdList"        : [],
            "skcStockBegin"         : "",
            "skcStockEnd"           : "",
            "skuStockBegin"         : "",
            "skuStockEnd"           : "",
            "skcSaleDaysBegin"      : "",
            "skcSaleDaysEnd"        : "",
            "skuSaleDaysBegin"      : "",
            "skuSaleDaysEnd"        : "",
            "planUrgentCountBegin"  : "",
            "planUrgentCountEnd"    : "",
            "skcAvailableOrderBegin": "",
            "skcAvailableOrderEnd"  : "",
            "skuAvailableOrderBegin": "",
            "skuAvailableOrderEnd"  : "",
            "shelfDateBegin"        : "",
            "shelfDateEnd"          : "",
            "stockWarnStatusList"   : [],
            "labelFakeIdList"       : [],
            "sheinSaleByInventory"  : "",
            "tspIdList"             : [],
            "adviceStatus"          : [],
            "sortBy7dSaleCnt"       : 2
        }
        payload = dictPayload
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))

        spu_list = response_text['info']['list']

        skc_list = [item['skc'] for item in spu_list]
        self.get_activity_label(skc_list)
        self.get_preemption_list(skc_list)
        self.get_sku_price_v2(skc_list)
        self.get_stock_advice(skc_list)

        total = response_text['info']['count']
        totalPage = math.ceil(total / pageSize)
        for page in range(2, totalPage + 1):
            log(f'获取SKU销量列表 第{page}/{totalPage}页')
            dictPayload['pageNumber'] = page
            payload = dictPayload
            response_text = fetch(self.web_page, url, payload)
            spu_list_new = response_text['info']['list']

            skc_list = [item['skc'] for item in spu_list_new]
            self.get_activity_label(skc_list)
            self.get_preemption_list(skc_list)
            self.get_sku_price_v2(skc_list)
            self.get_stock_advice(skc_list)

            spu_list += spu_list_new
            time.sleep(0.3)

        cache_file = f'{self.config.auto_dir}/shein/sku_price/sku_price_{self.store_username}.json'
        dict_sku_price = read_dict_from_file(cache_file)

        cache_file2 = f'{self.config.auto_dir}/shein/dict/dict_skc_week_trend_{self.store_username}.json'
        DictSkcWeekTrend = read_dict_from_file(cache_file2)

        cache_file3 = f'{self.config.auto_dir}/shein/dict/product_list_{self.store_username}.json'
        DictSpuInfo = read_dict_from_file(cache_file3)

        cache_file = f'{self.config.auto_dir}/shein/dict/activity_price_{self.store_name}.json'
        dictActivityPrice = read_dict_from_file(cache_file)

        product_sku_list = [
            [
                '店铺名称', '商品信息', 'SKC图片', 'SKU图片', 'SKU', 'SKU货号', '在售天数', '库存(模式/本地/在途/希音)',
                '今天销量', '今日订单数',  # 9
                '远7天销量', '远7天订单数', '近7天销量', '近7天订单数', '周销增量', '远30天销量', '远30天订单数',
                '近30天销量', '近30天订单数', '月销增量', '总销量',  # 11
                '申报价', '成本价', '毛利润', '毛利率', '近7天利润', '近30天利润',  # 6
                'SPU', 'SKC', 'SKC货号', '近7天SKU销量/SKC销量/SKC曝光', 'SKC点击率/SKC转化率', '自主参与活动', '商品标题', '叶子类目',  # 5
                'SKC近7天销量', 'SKC近7天曝光人数', 'SKC近7天商详访客', 'SKC近7天点击率', 'SKC近7天支付人数',
                'SKC近7天支付率', 'SKC近7天评论数'
            ]
        ]

        date_60_days_ago = TimeUtils.get_past_nth_day(60, None, '%Y-%m-%d')
        log('-60', date_60_days_ago)
        date_7_days_ago = TimeUtils.get_past_nth_day(7, None, '%Y-%m-%d')
        log('-7', date_7_days_ago)
        date_1_days_ago = TimeUtils.get_past_nth_day(1, None, '%Y-%m-%d')
        log('-1', date_1_days_ago)

        count = 0
        for spu_info in spu_list:
            count += 1
            # if count > 10:
            #     break
            spu = spu_info['spu']
            skc = str(spu_info['skc'])
            # if not shein_db.exists_sales_1_days_ago(skc):
            #     log(f'未查到昨天销量: {skc}')
            self.get_skc_week_actual_sales(skc)
            self.get_skc_sales(skc, date_60_days_ago, date_1_days_ago)
            skcCode = spu_info['supplierCode']
            product_name = DictSpuInfo[spu]['product_name_en']
            category_name = spu_info['categoryName']
            shelfDays = spu_info['shelfDays']
            shelf_status = DictSpuInfo[spu]['shelf_status']
            dictStatus = {
                'WAIT_SHELF': "待上架",
                'ON_SHELF'  : "已上架",
                'SOLD_OUT'  : "已售罄",
                'OUT_SHELF' : "已下架"
            }
            status_cn = dictStatus[shelf_status]
            good_level = spu_info['goodsLevel']['name']
            sale_model = spu_info['saleModel']['name']

            # 过滤已经售罄
            if shelf_status == 'SOLD_OUT':
                log(f'过滤已售罄: {skc} {category_name} {product_name}')
                continue

            for sku_info in spu_info['skuList']:
                sku = sku_info['skuCode']
                skuExtCode = str(sku_info['supplierSku'])
                if sku == '合计':
                    continue

                # 获取基础数据
                stock = self.bridge.get_sku_stock(skuExtCode, source)
                cost_price = self.bridge.get_sku_cost(skuExtCode, source)
                sku_img = self.bridge.get_sku_img(skuExtCode, source)

                # 计算库存相关数据
                shein_stock = sku_info['stock']
                transit = sku_info['transit']  # 在途
                real_transit = transit + sku_info['stayShelf'] - sku_info['transitSale']

                # 获取销量数据
                week_sales = get_last_week_sales(sku)
                week_sales2 = get_near_week_sales(sku)
                month_sales = get_last_month_sales(sku)
                month_sales2 = get_near_month_sales(sku)

                # 获取SKC趋势数据
                key = str(skc)
                skc_trend = DictSkcWeekTrend.get(key, {})

                # 使用append组装数据
                sku_item = []

                # 店铺名称
                sku_item.append(f'{self.store_name}\n({status_cn})\n{good_level}\n{date_7_days_ago}\n{date_1_days_ago}')

                # 商品信息
                product_info = f"SPU: {spu}\nSKC: {skc}\nSKC货号: {skcCode}\n类目: {category_name}\n在售天数: {shelfDays}"
                sku_item.append(product_info)

                # SKC图片
                sku_item.append(spu_info['picUrl'])

                # SKU图片
                sku_item.append(sku_img)

                # SKU基本信息
                sku_item.append(sku)  # SKU
                sku_item.append(f"{sku_info['supplierSku']}")  # SKU货号
                sku_item.append(shelfDays)  # 在售天数

                # 库存信息
                sku_item.append(f'{sale_model}\n{stock}/{real_transit}/{shein_stock}')

                # 今日销量数据
                sku_item.append(sku_info['totalSaleVolume'])  # 今日销量
                sku_item.append(sku_info['orderCnt'])  # 今日订单数

                # 远7天销量数据
                sku_item.append(week_sales[0])  # 远7日销量
                sku_item.append(week_sales[1])  # 远7日订单数

                # 近7天销量数据
                sku_item.append(week_sales2[0])  # 近7日销量
                sku_item.append(week_sales2[1])  # 近7日订单数
                sku_item.append(week_sales2[1] - week_sales2[0])  # 周增销量

                # 远30天销量数据
                sku_item.append(month_sales[0])  # 远30日销量
                sku_item.append(month_sales[1])  # 远30日订单数

                # 近30天销量数据
                sku_item.append(month_sales2[0])  # 近30日销量
                sku_item.append(month_sales2[1])  # 近30日订单数
                sku_item.append(month_sales2[1] - month_sales2[0])  # 月增销量

                # 总销量
                sku_item.append('-')

                # 价格相关
                sku_item.append(dict_sku_price[sku])  # 申报价
                sku_item.append(cost_price)  # 成本价
                sku_item.append('')  # 毛利润
                sku_item.append('')  # 毛利率
                sku_item.append('')  # 近7天利润
                sku_item.append('')  # 近30天利润

                # 商品标识
                sku_item.append(spu)  # SPU
                sku_item.append(skc)  # SKC
                sku_item.append(spu_info['supplierCode'])  # SKC货号

                sale_num_list, sale_data_list = self.get_sku_week_sale_list(spu, skc, sku)
                sku_item.append("\n".join(sale_num_list))
                sku_item.append("\n".join(sale_data_list))
                sku_item.append(self.get_skc_activity_label(skc, sku, dictActivityPrice))

                sku_item.append(product_name)  # 商品标题
                sku_item.append(category_name)  # 叶子类目

                # SKC趋势数据
                sku_item.append(skc_trend.get('saleCnt', 0))  # SKC近7天销量
                sku_item.append(skc_trend.get('epsUvIdx', 0))  # SKC近7天曝光人数
                sku_item.append(skc_trend.get('goodsUv', 0))  # SKC近7天商详访客
                sku_item.append(skc_trend.get('epsGdsCtrIdx', 0))  # SKC近7天点击率
                sku_item.append(skc_trend.get('payUvIdx', 0))  # SKC近7天支付人数
                sku_item.append(skc_trend.get('gdsPayCtrIdx', 0))  # SKC近7天支付率
                sku_item.append(skc_trend.get('totalCommentCnt', 0))  # 评论数

                product_sku_list.append(sku_item)

        cache_file = f'{self.config.auto_dir}/shein/cache/week_sales_{TimeUtils.today_date()}.json'
        write_dict_to_file_ex(cache_file, {self.store_name: product_sku_list}, [self.store_name])

        return product_sku_list

    # 获取一个skc一周内的销售趋势（商品明细中的）
    def get_dict_skc_week_trend_v2(self, spu, skc, start_from=None):
        dt = self.get_dt_time()

        date_7_days_ago, date_1_days_ago = TimeUtils.get_past_7_days_range_format(start_from, '%Y%m%d')
        log(date_7_days_ago, date_1_days_ago, 'dt', dt)

        # 将字符串转换为日期对象
        date1 = datetime.strptime(date_1_days_ago, "%Y%m%d").date()
        date2 = datetime.strptime(dt, "%Y%m%d").date()
        if date1 > date2:
            send_exception(f'get_dict_skc_week_trend_v2: dt:{dt} < date_1_days_ago: {date_1_days_ago}')

        cache_file = f'{self.config.auto_dir}/shein/dict/dict_skc_week_trend_{skc}_{date_7_days_ago}_{date_1_days_ago}.json'
        if datetime.now().hour >= 9:
            DictSkc = read_dict_from_file(cache_file)
        else:
            DictSkc = read_dict_from_file(cache_file, 1800)
        if len(DictSkc) > 0:
            return DictSkc

        url = f"https://sso.geiwohuo.com/sbn/new_goods/get_skc_diagnose_trend"
        payload = {
            "areaCd"     : "cn",
            "countrySite": [
                "shein-all"
            ],
            "dt"         : dt,
            "endDate"    : date_1_days_ago,
            "spu"        : [spu],
            "skc"        : [skc],
            "startDate"  : date_7_days_ago,
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))

        data_list = response_text['info']
        DictSkc = {}
        for date_item in data_list:
            dataDate = date_item['dataDate']
            # epsUvIdx = date_item['epsUvIdx']
            # saleCnt = date_item['saleCnt']
            DictSkc[dataDate] = date_item

        log('len(DictSkc)', len(DictSkc))
        write_dict_to_file(cache_file, DictSkc)
        return DictSkc

    def get_sku_week_sale_list(self, spu, skc, sku):
        dict_skc = self.get_dict_skc_week_trend_v2(spu, skc)
        date_list = TimeUtils.get_past_7_days_list()
        first_day, last_day = TimeUtils.get_past_7_days_range()
        cache_file = f'{self.config.auto_dir}/shein/cache/{skc}_{first_day}_{last_day}.json'
        DictSkuSalesDate = read_dict_from_file(cache_file)
        sales_detail = []
        for date in date_list:
            sales_num = DictSkuSalesDate.get(date, {}).get(sku, {}).get("hisActualValue", 0)
            sales_num = sales_num if sales_num is not None else 0

            saleCnt = get_safe_value(dict_skc.get(date, {}), 'saleCnt', 0)
            epsUvIdx = get_safe_value(dict_skc.get(date, {}), 'epsUvIdx', 0)

            sales_detail.append(f'{date}({TimeUtils.get_weekday_name(date)}): {sales_num}/{saleCnt}/{epsUvIdx}')

        sales_data = []
        for date in date_list:
            goodsUvIdx = get_safe_value(dict_skc.get(date, {}), 'goodsUvIdx', 0)  # 商详访客
            epsGdsCtrIdx = get_safe_value(dict_skc.get(date, {}), 'epsGdsCtrIdx', 0)  # 点击率

            payUvIdx = get_safe_value(dict_skc.get(date, {}), 'payUvIdx', 0)  # 支付人数
            gdsPayCtrIdx = get_safe_value(dict_skc.get(date, {}), 'gdsPayCtrIdx', 0)  # 转化率

            sales_data.append(f'{date}({TimeUtils.get_weekday_name(date)}): {epsGdsCtrIdx:.2%}({goodsUvIdx})/{gdsPayCtrIdx:.2%}({payUvIdx})')

        return sales_detail, sales_data

    def get_activity_price(self, activity_dict, sku, activity_name, dateBegin, dateEnd):
        key = f'{sku}_{dateBegin}_{dateEnd}_{activity_name}'
        price_info = activity_dict.get(key, ['-', '-'])
        return f'活动价:¥{price_info[0]}, 活动库存:{price_info[1]}'

    def get_skc_activity_label(self, skc, sku, dict_activity_price=None):
        cache_file = f'{self.config.auto_dir}/shein/activity_label/activity_label_{self.store_username}.json'
        dict_label = read_dict_from_file(cache_file)
        operateLabelList = dict_label[skc]['operateLabelList']
        activityList = []
        activityList2 = []
        for item in operateLabelList:
            if item['name'] == '活动中':
                activityList.extend(item.get('activityList', []))
            if item['name'] == '即将开始':
                activityList2.extend(item.get('activityList', []))

        if activityList:
            activityLabel = '\n'.join([
                f'  [{act["date"]}]\n【{self.get_activity_price(dict_activity_price, sku, act["name"], act["dateBegin"], act["dateEnd"])}】{act["name"]}\n'
                for act in activityList])
        else:
            activityLabel = '无'
        if activityList2:
            activityLabel2 = '\n'.join([
                f'  [{act["date"]}]\n【{self.get_activity_price(dict_activity_price, sku, act["name"], act["dateBegin"], act["dateEnd"])}】{act["name"]}\n'
                for act in activityList2])
        else:
            activityLabel2 = '无'
        return f'活动中:\n{activityLabel}\n即将开始:\n{activityLabel2}'

    # 获取商品包含sku销量的列表
    # mode = 1.备货建议 2.已上架 3.昨日上架 4.昨日出单
    # 5.采购-缺货要补货      (有现货建议 建议采购为正 有销量)
    # 6.运营采购-滞销清库存   (无现货建议 建议采购为负 30天外 无销量)
    # 7.运营-新品上架需要优化 (无现货建议 建议采购为负 上架15天内)
    # 8.运营-潜在滞销款      (无现货建议 30天外 有销量)
    # 9.运营-潜力热销款      (有现货建议 30天内 有销量)
    # 10.运营-热销款         (有现货建议 30天外 有销量)
    def get_bak_advice(self, mode=1, skcs=None, source='mb'):
        log(f'获取备货信息商品列表 做成字典')
        if skcs == None or len(skcs) == 0:
            # if mode == 3:
            #     skcs = "sh2405133614611175"  # 这是一个不存在的skc
            # else:
            skcs = ""
        else:
            skcs = ",".join(skcs)

        url = "https://sso.geiwohuo.com/idms/goods-skc/list"
        pageNumber = 1
        pageSize = 100
        dictPayload = {
            "pageNumber"            : pageNumber,
            "pageSize"              : pageSize,
            "supplierCodes"         : "",
            "skcs"                  : skcs,
            "spu"                   : "",
            "c7dSaleCntBegin"       : "",
            "c7dSaleCntEnd"         : "",
            "goodsLevelIdList"      : [10, 107, 61, 90, 87, 237, 220, 219, 88, 75, 62, 227, 12, 230, 80, 58, 224, 97],
            "supplyStatus"          : "",
            "shelfStatus"           : "",
            "categoryIdList"        : [],
            "skcStockBegin"         : "",
            "skcStockEnd"           : "",
            "skuStockBegin"         : "",
            "skuStockEnd"           : "",
            "skcSaleDaysBegin"      : "",
            "skcSaleDaysEnd"        : "",
            "skuSaleDaysBegin"      : "",
            "skuSaleDaysEnd"        : "",
            "planUrgentCountBegin"  : "",
            "planUrgentCountEnd"    : "",
            "skcAvailableOrderBegin": "",
            "skcAvailableOrderEnd"  : "",
            "skuAvailableOrderBegin": "",
            "skuAvailableOrderEnd"  : "",
            "shelfDateBegin"        : "",
            "shelfDateEnd"          : "",
            "stockWarnStatusList"   : [],
            "labelFakeIdList"       : [],
            "sheinSaleByInventory"  : "",
            "tspIdList"             : [],
            "adviceStatus"          : [],
            "sortBy7dSaleCnt"       : 2,
            "goodsLevelFakeIdList"  : [1, 2, 3, 8, 14, 15, 4, 11]
        }
        payload = dictPayload
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))

        spu_list = response_text['info']['list']

        skc_list = [item['skc'] for item in spu_list]
        self.get_activity_label(skc_list)
        self.get_preemption_list(skc_list)
        self.get_sku_price_v2(skc_list)
        self.get_stock_advice(skc_list)

        total = response_text['info']['count']
        totalPage = math.ceil(total / pageSize)
        for page in range(2, totalPage + 1):
            log(f'获取备货信息商品列表 第{page}/{totalPage}页')
            dictPayload['pageNumber'] = page
            payload = dictPayload
            response_text = fetch(self.web_page, url, payload)
            spu_list_new = response_text['info']['list']

            skc_list = [item['skc'] for item in spu_list_new]
            self.get_activity_label(skc_list)
            self.get_preemption_list(skc_list)
            self.get_sku_price_v2(skc_list)
            self.get_stock_advice(skc_list)

            spu_list += spu_list_new
            time.sleep(0.3)

        cache_file = f'{self.config.auto_dir}/shein/dict/activity_price_{self.store_name}.json'
        dictActivityPrice = read_dict_from_file(cache_file)
        # cache_file = f'{self.config.auto_dir}/shein/dict/product_list_{self.store_username}.json'
        # DictSpuInfo = read_dict_from_file(cache_file, 5)
        cache_file = f'{self.config.auto_dir}/shein/preemption_num/preemption_num_{self.store_username}.json'
        dict_preemption_num = read_dict_from_file(cache_file)
        cache_file = f'{self.config.auto_dir}/shein/vmi_spot_advice/spot_advice_{self.store_username}.json'
        dict_advice = read_dict_from_file(cache_file)
        cache_file = f'{self.config.auto_dir}/shein/sku_price/sku_price_{self.store_username}.json'
        dict_sku_price = read_dict_from_file(cache_file)
        date_list = TimeUtils.get_past_7_days_list()
        if mode in [2, 5, 6, 7, 8, 9, 10]:
            excel_data = [[
                '店铺名称', 'SKC图片', 'SKU图片', '商品信息', '建议现货数量', '现有库存数量', '已采购数量', '预测日销',
                '本地和采购可售天数', '生产天数', '建议采购', '产品起定量',
                '备货周期(天)', '备货建议', '近7天SKU销量/SKC销量/SKC曝光', 'SKC点击率/SKC转化率', '自主参与活动',
                'SKC',
                "SKU"
            ]]
        else:
            excel_data = [[
                '店铺名称', 'SKC图片', 'SKU图片', '商品信息', '备货建议', '近7天SKU销量/SKC销量/SKC曝光',
                'SKC点击率/SKC转化率', '自主参与活动', 'SKC', "SKU"
            ]]
        for spu_info in spu_list:
            spu = str(spu_info['spu'])
            skc = str(spu_info['skc'])

            status_cn = spu_info['shelfStatus']['name']
            if status_cn != '已上架':
                continue

            # shelf_status = DictSpuInfo.get(spu, {}).get('shelf_status', '')
            # if mode != 1:
            #     if shelf_status != 'ON_SHELF' and shelf_status != 'SOLD_OUT':
            #         log('跳过', skc, shelf_status)
            #         continue

            # if mode in [5, 6, 7, 8, 9, 10] and shelf_status == 'SOLD_OUT':
            #     continue
            #
            # dictStatus = {
            #     'WAIT_SHELF': "待上架",
            #     'ON_SHELF': "已上架",
            #     'SOLD_OUT': "已售罄",
            #     'OUT_SHELF': "已下架"
            # }
            # status_cn = dictStatus.get(shelf_status, '-')

            sale_model = spu_info['saleModel']['name']
            goods_level = spu_info['goodsLevel']['name']
            goods_label = [label["name"] for label in spu_info['goodsLabelList']]
            skc_img = spu_info['picUrl']
            shelfDate = spu_info['shelfDate']
            shelfDays = spu_info['shelfDays']
            categoryName = spu_info['categoryName']

            if mode in [3] and shelfDays != 1:
                continue

            DictSkuSalesDate = self.get_skc_week_actual_sales(skc)

            for sku_info in spu_info['skuList']:
                row_item = []
                attr = sku_info['attr']
                if attr == '合计':
                    continue
                predictDaySales = sku_info['predictDaySales']
                availableOrderCount = sku_info['availableOrderCount']
                if mode == 1:
                    if availableOrderCount is None or availableOrderCount <= 0:
                        log('跳过', skc, availableOrderCount)
                        continue

                row_item.append(f'{self.store_name}\n({status_cn})\n{goods_level}\n{",".join(goods_label)}')
                row_item.append(skc_img)
                sku = sku_info['skuCode']
                skuExtCode = str(sku_info['supplierSku'])
                sku_img = self.bridge.get_sku_img(skuExtCode, source)
                row_item.append(sku_img)

                transit = sku_info['transit']  # 在途

                stock = self.bridge.get_sku_stock(skuExtCode, source)
                cost_price = self.bridge.get_sku_cost(skuExtCode, source)

                supplyPrice = dict_sku_price[sku]
                shein_stock = sku_info['stock']
                if cost_price == '-':
                    profit = '-'
                else:
                    profit = f'{float(supplyPrice) - float(cost_price):.2f}'

                min_spot_advice = dict_advice.get(skc, {}).get(sku, {}).get('minSpotAdvice', 0)
                max_spot_advice = dict_advice.get(skc, {}).get(sku, {}).get('maxSpotAdvice', 0)
                stock_advice = f'{min_spot_advice}~{max_spot_advice}'
                log('stock_advice', stock_advice)
                # 建议现货数量
                advice_stock_number = round((min_spot_advice + max_spot_advice) / 4)

                # 有现货建议
                if mode in [5, 9, 10] and advice_stock_number == 0:
                    continue

                # 无现货建议
                if mode in [6, 7, 8] and advice_stock_number > 0:
                    continue

                stockSaleDays = sku_info['stockSaleDays']

                product_info = (
                    f'SPU: {spu}\n'
                    f'SKC: {skc}\n'
                    f'SKU货号: {skuExtCode}\n'
                    f'属性集: {attr}\n'
                    f'商品分类: {categoryName}\n'
                    f'上架日期: {shelfDate}\n'
                    f'上架天数: {shelfDays}\n'
                    f'库存可售天数/现货建议: {stockSaleDays}/{stock_advice}\n'
                )
                row_item.append(product_info)

                # 建议采购数量逻辑
                try:
                    # 尝试将字符串数字转换为 float，再转为 int（如有必要）
                    current_stock = float(stock)
                    advice_purchase_number = advice_stock_number - int(current_stock)

                    # 建议采购为正
                    if (mode == 5 and advice_purchase_number <= 0):
                        continue

                except (ValueError, TypeError):
                    # 无法转换为数值时
                    advice_purchase_number = '-'

                if mode in [2, 5, 6, 7, 8, 9, 10]:
                    row_item.append(advice_stock_number)
                    row_item.append(stock)

                    row_item.append(0)
                    row_item.append(predictDaySales)
                    row_item.append(0)
                    row_item.append(7)

                    row_item.append(advice_purchase_number)
                    row_item.append(0)  # 产品起定量
                    row_item.append(0)  # 备货周期(天)

                adviceOrderCount = sku_info['adviceOrderCount'] if sku_info['adviceOrderCount'] is not None else '-'
                if sku_info['autoOrderStatus'] is not None:
                    autoOrderStatus = ['-', '是', '否'][sku_info['autoOrderStatus']] if sku_info[
                                                                                            'adviceOrderCount'] is not None else '-'
                else:
                    autoOrderStatus = '-'
                orderCount = sku_info['orderCount']  # 已下单数
                c7dSaleCnt = sku_info['c7dSaleCnt']
                c30dSaleCnt = sku_info['c30dSaleCnt']
                orderCnt = sku_info['orderCnt']
                totalSaleVolume = sku_info['totalSaleVolume']
                planUrgentCount = sku_info['planUrgentCount']
                preemptionCount = dict_preemption_num[skc][sku]
                predictDaySales = sku_info['predictDaySales']
                goodsDate = sku_info['goodsDate']
                stockDays = sku_info['stockDays']

                real_transit = transit + sku_info['stayShelf'] - sku_info['transitSale']

                sales_info = (
                    f'近7天/30天销量: {c7dSaleCnt}/{c30dSaleCnt}\n'
                    f'当天销量/购买单数: {totalSaleVolume}/{orderCnt}\n'
                    f'预测日销/下单参数: {predictDaySales}/{goodsDate}+{stockDays}\n'
                    f'预占数/预计急采数: {preemptionCount}/{planUrgentCount}\n'
                    f'建议下单/已下单数: {adviceOrderCount}/{orderCount}\n'
                    f'拟下单数/自动下单: {availableOrderCount}/{autoOrderStatus}\n'
                    f'模式/本地/在途/希音: {sale_model[:2]}/{stock}/{real_transit}/{shein_stock}\n'
                    f'成本/核价/利润: ¥{cost_price}/¥{supplyPrice}/¥{profit}\n'
                )

                row_item.append(sales_info)

                flag_yesterday = 0
                sales7cn = 0
                for date in date_list:
                    sales_num = DictSkuSalesDate.get(date, {}).get(sku, {}).get("hisActualValue", 0)
                    sales_num = sales_num if sales_num is not None else 0
                    sales7cn += sales_num
                    if TimeUtils.is_yesterday_date(date) and sales_num == 0:
                        flag_yesterday = 1

                if mode == 4 and flag_yesterday:
                    continue

                # 过滤掉未建立马帮信息的
                if mode in [5, 6, 7, 8, 9, 10] and advice_purchase_number == '-':
                    continue

                # 建议采购为正
                if mode in [5] and advice_purchase_number < 0:
                    continue

                # 建议采购为负
                if mode in [6, 7] and advice_purchase_number >= 0:
                    continue

                # 30内
                if mode in [9] and shelfDays > 31:
                    continue

                # 15天内
                if mode in [7] and shelfDays > 15:
                    continue

                # 30外
                if mode in [6, 8, 10] and shelfDays < 31:
                    continue

                # 有销量
                if mode in [5, 8, 9, 10] and sales7cn == 0:
                    continue

                # 无销量
                if mode in [6] and sales7cn > 0:
                    continue

                sale_num_list, sale_data_list = self.get_sku_week_sale_list(spu, skc, sku)
                row_item.append("\n".join(sale_num_list))
                row_item.append("\n".join(sale_data_list))
                row_item.append(self.get_skc_activity_label(skc, sku, dictActivityPrice))
                row_item.append(skc)
                row_item.append(sku)
                excel_data.append(row_item)

        cache_file = f'{self.config.auto_dir}/shein/cache/bak_advice_{mode}_{TimeUtils.today_date()}.json'
        write_dict_to_file_ex(cache_file, {self.store_name: excel_data}, {self.store_name})

        cache_file = f'{self.config.auto_dir}/shein/cache/bak_advice_notify_{mode}_{TimeUtils.today_date()}.json'
        NotifyItem = [self.store_name, len(excel_data[1:])]
        write_dict_to_file_ex(cache_file, {self.store_name: NotifyItem}, {self.store_name})

        return excel_data
