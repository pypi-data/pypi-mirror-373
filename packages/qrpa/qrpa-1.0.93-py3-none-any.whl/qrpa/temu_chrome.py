from playwright.sync_api import sync_playwright, Page
from qrpa import get_progress_json_ex, done_progress_json_ex, send_exception
from qrpa import TemuLib, get_chrome_page_v3, log

from typing import Literal, Optional, Callable, List, Dict, Any

"""不要test开头命名文件 否则会用pytest运行这个程序"""

def temu_chrome_excute(settings, run_prepare: Optional[Callable] = None, run: Optional[Callable] = None, run_summary: Optional[Callable] = None, run_notify: Optional[Callable] = None, key_id: Optional[str] = None, just_usernames: Optional[List] = None, just_mall_ids: Optional[List] = None):
    run_prepare()
    with sync_playwright() as p:
        count = 0
        while True:
            try:
                count += 1
                with get_chrome_page_v3(p) as (browser, context, web_page):
                    web_page: Page  # 显式注解

                    for account in settings.temu_account_list:
                        username = account[0]
                        password = account[1]

                        if just_usernames and username not in just_usernames:
                            continue

                        if get_progress_json_ex(settings, key_id, username):
                            continue

                        temu_client = TemuLib(settings, username, password, web_page)
                        shop_list = temu_client.get_shop_list()
                        # 增加每个店铺的处理进度
                        for shop in shop_list:
                            mall_id = shop[0]
                            mall_name = shop[1]
                            if just_mall_ids and mall_id not in just_mall_ids:
                                continue

                            store_name = f'{mall_id}_{mall_name}'
                            if not get_progress_json_ex(settings, key_id, store_name):
                                log(f"正在处理店铺: {mall_name},{mall_id},{username}")
                                run(temu_client, web_page, mall_id, mall_name)
                                done_progress_json_ex(settings, key_id, store_name)

                        done_progress_json_ex(settings, key_id, username)

                    if not get_progress_json_ex(settings, key_id, 'run_summary'):
                        run_summary()
                        done_progress_json_ex(settings, key_id, 'run_summary')
                    if not get_progress_json_ex(settings, key_id, 'run_notify'):
                        run_notify()
                        done_progress_json_ex(settings, key_id, 'run_notify')
                    break
            except:
                send_exception()
                if count > 1:
                    break
