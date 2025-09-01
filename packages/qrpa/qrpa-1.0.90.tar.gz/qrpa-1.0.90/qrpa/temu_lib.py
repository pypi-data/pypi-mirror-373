from .fun_file import read_dict_from_file, write_dict_to_file, read_dict_from_file_ex, write_dict_to_file_ex
from .fun_base import log, send_exception, md5_string, get_safe_value
from .time_utils import TimeUtils

import json, requests, time, math

class TemuLib:
    def __init__(self, config, mobile, password, web_page):
        self.config = config
        self.web_page = web_page
        self.mobile = mobile

        self.dict_mall = {}
        self.cookie = self.doLoginToTemu(mobile, password)

    # 主账户登录 返回Cookie
    def doLoginToTemu(self, username, password):
        cache_cookie = f'{self.config.auto_dir}/temu/cookie/cookie_{username}.json'
        dict_cookie = read_dict_from_file(cache_cookie, 1)
        if len(dict_cookie) > 0:
            self.cookie = dict_cookie.get('cookie')
            return

        log(f'登录Temu账号: {username}')

        """使用 XPath 登录网站"""
        # 导航到登录页面
        self.web_page.goto("https://seller.kuajingmaihuo.com/login")
        # 输入用户名
        self.web_page.locator('//input[@id="usernameId"]').fill("")
        self.web_page.locator('//input[@id="usernameId"]').fill(username)
        # 输入密码
        self.web_page.locator('//input[@id="passwordId"]').fill("")
        self.web_page.locator('//input[@id="passwordId"]').fill(password)
        # 勾选隐私政策（checkbox）
        self.web_page.locator('//input[@type="checkbox"]/following-sibling::div').click()  # 直接check不了 换成点击
        # 点击登录按钮
        self.web_page.locator('//button[span[text()="登录"]]').click()
        # 等待登录完成（根据页面加载情况调整等待策略）
        self.web_page.wait_for_load_state("load")

        while True:
            log('等待卖家中心出现')
            try:
                if self.web_page.locator('//div[text()="Temu商家中心"]').count() == 1:
                    log('卖家中心已出现')
                    break
                if self.web_page.locator('//div[text()="Seller Central"]').count() == 1:
                    log('卖家中心已出现')
                    break
            except Exception as e:
                log(f"❌{e}")
            time.sleep(1.5)

        log("✅ 登录成功")

        self.web_page.wait_for_load_state("load")
        self.web_page.wait_for_timeout(3000)
        cookies = self.web_page.context.cookies()
        cookies_list = [cookie for cookie in cookies if '.kuajingmaihuo.com' in cookie['domain']]
        self.cookie = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies_list])
        log(f'已获取self.cookie:', self.cookie)
        write_dict_to_file(cache_cookie, {'cookie': self.cookie})
        return self.cookie

    def post_json(self, str_url, payload, mall_id=None):
        global response
        try:
            headers = {
                'content-type': 'application/json',
                'priority'    : 'u=1, i',
                'referer'     : 'https://seller.kuajingmaihuo.com/settle/site-main',
                'user-agent'  : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
                'Cookie'      : self.cookie,
            }
            if mall_id:
                headers.update({'mallid': f"{mall_id}"})
            response = requests.post(str_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # 如果响应不正常，会抛出异常

            response_text = response.json()
            error_code = response_text.get('error_code') or response_text.get('errorCode')
            if error_code != 1000000:
                raise send_exception(response_text)
            return response.json()  # 直接返回 JSON 格式的数据
        except:
            raise send_exception()

    def get_shop_list(self):
        log(f'获取店铺列表')
        global DictMall
        url = "https://seller.kuajingmaihuo.com/bg/quiet/api/mms/userInfo"
        response_text = self.post_json(url, {})

        company_list = response_text['result']['companyList']
        mall_list = []
        for company in company_list:
            mallList = company['malInfoList']
            # shop_list = [['店铺ID', '店铺名称', '主账号', '店铺类型']]
            for mall in mallList:
                mall_id = str(mall['mallId'])
                mall_name = str(mall['mallName'])
                shop_info = [mall_id, mall_name, self.mobile, '半托管' if mall['isSemiManagedMall'] else '全托管']
                write_dict_to_file_ex(self.config.temu_store_info, {mall_id: shop_info}, [mall_id])

                self.dict_mall[str(mall['mallId'])] = mall['mallName']

                if not mall['isSemiManagedMall']:
                    mall_list.append([str(mall['mallId']), mall['mallName'], '', self.mobile])

        return mall_list

    def get_funds_info(self, mall_id):
        log(f'获取 {self.dict_mall[mall_id]} 资金信息')
        url = "https://seller.kuajingmaihuo.com/api/merchant/payment/account/amount/info"
        response_text = self.post_json(url, {}, mall_id)
        total_amount = response_text.get('result').get('totalAmount')
        available_amount = response_text.get('result').get('availableBalance')

        NotifyItem = [self.dict_mall[mall_id], total_amount, available_amount, '', TimeUtils.current_datetime()]

        cache_file = f'{self.config.auto_dir}/temu/cache/funds_{TimeUtils.today_date()}.json'
        write_dict_to_file_ex(cache_file, {mall_id: NotifyItem}, [mall_id])

        return NotifyItem

    def list_warehouse(self, mall_id, mall_name):
        log(f'获取店铺 {mall_name} 销售商品列表 第1页')
        url = "https://seller.kuajingmaihuo.com/marvel-mms/cn/api/kiana/venom/sales/management/listWarehouse"
        payload = {
            "pageNo"               : 1,
            "pageSize"             : 40,
            "isLack"               : 0,
            "selectStatusList"     : [12],  # 12 是已加入站点
            "priceAdjustRecentDays": 30  # 近30日价格调整
        }
        response_text = self.post_json(url, payload, mall_id)

        total = response_text['result']['total']
        subOrderListCount = len(response_text['result']['subOrderList'])
        totalPage = math.ceil(total / subOrderListCount) if subOrderListCount else 0
        subOrderList = response_text['result']['subOrderList']

        for page in range(2, totalPage + 1):
            log(f'获取店铺{mall_name}销售商品列表 第{page}/{totalPage}页')
            payload['pageNo'] = page
            response_text = self.post_json(url, payload, mall_id)
            subOrderList += response_text['result']['subOrderList']
            time.sleep(0.3)

        cache_file = f'{self.config.auto_dir}/temu/cache/warehouse_list_{TimeUtils.today_date()}.json'
        write_dict_to_file_ex(cache_file, {mall_id: subOrderList}, [mall_id])

        return subOrderList
