"""
# 适用环境python3
# 紫鸟浏览器自动化操作 - 面向对象重构版本
"""
import os
import platform
import shutil
import time, datetime
import traceback
import uuid
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Literal, Optional, Callable, List, Dict, Any

import requests
import subprocess
from playwright import sync_api
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# 使用 partial 或 lambda 固定部分参数
from functools import partial

from .fun_win import find_software_install_path
from .fun_base import log, hostname, send_exception, NetWorkIdleTimeout
from .fun_file import check_progress_json_ex, get_progress_json_ex, done_progress_json_ex, write_dict_to_file_ex

class ZiniaoClient:
    """紫鸟客户端管理类"""

    def __init__(self, config):
        self.config = config
        self.version = "v5"
        self.socket_port = 16851
        self.is_windows = platform.system() == 'Windows'
        self.is_mac = platform.system() == 'Darwin'
        self.client_path = self._get_client_path()
        self.user_info = self._get_user_info()

        if not self.is_windows and not self.is_mac:
            raise RuntimeError("webdriver/cdp只支持windows和mac操作系统")

    def _get_client_path(self) -> str:
        """获取客户端路径"""
        if self.is_windows:
            ziniao = find_software_install_path('SuperBrowser')
            if ziniao is None:
                raise RuntimeError('未找到SuperBrowser安装路径')
            return ziniao
        else:
            return 'ziniao'

    def _get_user_info(self) -> Dict[str, str]:
        """获取用户登录信息"""
        return {
            "company" : self.config.ziniao.company,
            "username": self.config.ziniao.username,
            "password": self.config.ziniao.password
        }

    def kill_process(self):
        """杀紫鸟客户端进程"""
        if self.version == "v5":
            process_name = 'SuperBrowser.exe'
        else:
            process_name = 'ziniao.exe'

        if self.is_windows:
            os.system('taskkill /f /t /im ' + process_name)
        elif self.is_mac:
            os.system('killall ziniao')
            time.sleep(3)

    def start_browser(self):
        """启动客户端"""
        try:
            if self.is_windows:
                cmd = [self.client_path, '--run_type=web_driver', '--show_sidb=true', '--ipc_type=http', '--port=' + str(self.socket_port)]
            elif self.is_mac:
                cmd = ['open', '-a', self.client_path, '--args', '--run_type=web_driver', '--ipc_type=http',
                       '--port=' + str(self.socket_port)]
            else:
                raise RuntimeError("不支持的操作系统")

            subprocess.Popen(cmd)
            time.sleep(5)
        except Exception:
            raise RuntimeError('start browser process failed')

    def update_core(self):
        """下载所有内核，打开店铺前调用，需客户端版本5.285.7以上"""
        data = {
            "action"   : "updateCore",
            "requestId": str(uuid.uuid4()),
        }
        data.update(self.user_info)

        while True:
            result = self.send_http(data)
            print(result)
            if result is None:
                print("等待客户端启动...")
                time.sleep(2)
                continue
            if result.get("statusCode") is None or result.get("statusCode") == -10003:
                print("当前版本不支持此接口，请升级客户端")
                return
            elif result.get("statusCode") == 0:
                print("更新内核完成")
                return
            else:
                print(f"等待更新内核: {json.dumps(result)}")
                time.sleep(2)

    def send_http(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """HTTP通讯方式"""
        try:
            url = f'http://127.0.0.1:{self.socket_port}'
            response = requests.post(url, json.dumps(data).encode('utf-8'), timeout=120)
            return json.loads(response.text)
        except Exception as err:
            print(err)
            return None

    def delete_all_cache(self):
        """删除所有店铺缓存"""
        if not self.is_windows:
            return
        local_appdata = os.getenv('LOCALAPPDATA')
        cache_path = os.path.join(local_appdata, 'SuperBrowser')
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path)

    def delete_all_cache_with_path(self, path: str):
        """删除指定路径的店铺缓存"""
        if not self.is_windows:
            return
        cache_path = os.path.join(path, 'SuperBrowser')
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path)

    def exit(self):
        """关闭客户端"""
        data = {"action": "exit", "requestId": str(uuid.uuid4())}
        data.update(self.user_info)
        print('@@ get_exit...' + json.dumps(data))
        self.send_http(data)

class ZiniaoBrowser:
    """紫鸟浏览器操作类"""

    def __init__(self, client: ZiniaoClient, config):
        self.client = client
        self.config = config

    def open_store(self, store_info: str, isWebDriverReadOnlyMode: int = 0,
            isprivacy: int = 0, isHeadless: int = 0,
            cookieTypeSave: int = 0, jsInfo: str = "") -> Dict[str, Any]:
        """打开店铺"""
        request_id = str(uuid.uuid4())
        data = {
            "action"                 : "startBrowser",
            "isWaitPluginUpdate"     : 0,
            "isHeadless"             : isHeadless,
            "requestId"              : request_id,
            "isWebDriverReadOnlyMode": isWebDriverReadOnlyMode,
            "cookieTypeLoad"         : 0,
            "cookieTypeSave"         : cookieTypeSave,
            "runMode"                : "1",
            "isLoadUserPlugin"       : False,
            "pluginIdType"           : 1,
            "privacyMode"            : isprivacy
        }
        data.update(self.client.user_info)

        if store_info.isdigit():
            data["browserId"] = store_info
        else:
            data["browserOauth"] = store_info

        if len(str(jsInfo)) > 2:
            data["injectJsInfo"] = json.dumps(jsInfo)

        r = self.client.send_http(data)
        if str(r.get("statusCode")) == "0":
            return r
        elif str(r.get("statusCode")) == "-10003":
            print(f"login Err {json.dumps(r, ensure_ascii=False)}")
            raise RuntimeError("登录错误")
        else:
            print(f"Fail {json.dumps(r, ensure_ascii=False)} ")
            raise RuntimeError("打开店铺失败")

    def close_store(self, browser_oauth: str):
        """关闭店铺"""
        request_id = str(uuid.uuid4())
        data = {
            "action"      : "stopBrowser",
            "requestId"   : request_id,
            "duplicate"   : 0,
            "browserOauth": browser_oauth
        }
        data.update(self.client.user_info)

        r = self.client.send_http(data)
        if str(r.get("statusCode")) == "0":
            return r
        elif str(r.get("statusCode")) == "-10003":
            print(f"login Err {json.dumps(r, ensure_ascii=False)}")
            raise RuntimeError("登录错误")
        else:
            print(f"Fail {json.dumps(r, ensure_ascii=False)} ")
            raise RuntimeError("关闭店铺失败")

    def get_browser_list(self, platform_name="SHEIN-全球") -> List[Dict[str, Any]]:
        """获取浏览器列表"""
        request_id = str(uuid.uuid4())
        data = {
            "action"   : "getBrowserList",
            "requestId": request_id
        }
        data.update(self.client.user_info)

        r = self.client.send_http(data)
        if str(r.get("statusCode")) == "0":
            print(r)
            # return r.get("browserList", [])
            return [site for site in r.get("browserList", []) if site.get("platform_name") == platform_name]
        elif str(r.get("statusCode")) == "-10003":
            print(f"login Err {json.dumps(r, ensure_ascii=False)}")
            raise RuntimeError("登录错误")
        else:
            print(f"Fail {json.dumps(r, ensure_ascii=False)} ")
            raise RuntimeError("获取浏览器列表失败")

    def get_browser_context(self, playwright, port: int):
        """获取playwright浏览器会话"""
        browser = playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        context = browser.contexts[0]
        return context

    def open_ip_check(self, browser_context, ip_check_url: str) -> bool:
        """打开ip检测页检测ip是否正常"""
        try:
            page = browser_context.pages[0]
            page.goto(ip_check_url)
            success_button = page.locator('//button[contains(@class, "styles_btn--success")]')
            success_button.wait_for(timeout=60000)  # 等待查找元素60秒
            print("ip检测成功")
            return True
        except PlaywrightTimeoutError:
            print("ip检测超时")
            return False
        except Exception as e:
            print("ip检测异常:" + traceback.format_exc())
            return False

    def open_launcher_page(self, browser_context, launcher_page: str, store_username: str, store_name: str, run_func: Callable, task_key: str):
        """打开启动页面并执行业务逻辑"""
        page = browser_context.pages[0]
        page.goto(launcher_page)
        page.wait_for_timeout(3000)

        run_func(page, store_username, store_name, task_key)

        # 标记完成
        done_progress_json_ex(self.config, task_key, store_name)

class ZiniaoTaskManager:
    """紫鸟任务管理类"""

    def __init__(self, browser: ZiniaoBrowser, config):
        self.browser = browser
        self.config = config

    def daily_cleanup_superbrowser(self, browser_id):
        """
        每天删除一次SuperBrowser缓存文件夹

        Args:
            browser_id (str): 浏览器ID，如 '26986387919128'
        """

        # 获取本地AppData路径
        local_appdata = os.getenv('LOCALAPPDATA')
        if not local_appdata:
            log("错误: 无法获取LOCALAPPDATA路径")
            return False

        # 构建路径
        cache_path = os.path.join(local_appdata, 'SuperBrowser')
        target_folder = os.path.join(cache_path, f'User Data\\Chromium_{browser_id}')
        flag_file = os.path.join(cache_path, f'User Data\\cleanup_flag_{browser_id}.txt')

        # 检查目标文件夹是否存在
        if not os.path.exists(target_folder):
            log(f"目标文件夹不存在: {target_folder}")
            return False

        # 获取当前日期
        today = datetime.date.today()
        today_str = today.strftime('%Y-%m-%d')

        # 检查标志文件
        need_cleanup = True

        if os.path.exists(flag_file):
            try:
                # 读取标志文件中的日期
                with open(flag_file, 'r', encoding='utf-8') as f:
                    last_cleanup_date = f.read().strip()

                # 如果是今天已经清理过，则跳过
                if last_cleanup_date == today_str:
                    log(f"今天({today_str})已经清理过，跳过删除操作")
                    need_cleanup = False

            except Exception as e:
                log(f"读取标志文件时出错: {e}")
                # 如果读取出错，继续执行清理

        if need_cleanup:
            try:
                # 删除目标文件夹
                log(f"正在删除文件夹: {target_folder}")
                shutil.rmtree(target_folder)
                log("删除成功!")

                # 创建/更新标志文件
                os.makedirs(os.path.dirname(flag_file), exist_ok=True)
                with open(flag_file, 'w', encoding='utf-8') as f:
                    f.write(today_str)

                log(f"已创建标志文件: {flag_file}")
                return True

            except Exception as e:
                log(f"删除文件夹时出错: {e}")
                return False

        return True

    def run_single_store_task(self, browser_info: Dict[str, Any],
            run_func: Callable, task_key: str,
            just_store_username: Optional[List[str]] = None,
            is_skip_store: Optional[Callable] = None
    ):
        """运行单个店铺的任务"""
        store_id = browser_info.get('browserOauth')
        store_name = browser_info.get("browserName")
        store_username = browser_info.get("store_username")

        # 删除浏览器缓存,一天一删
        browser_id = browser_info.get("browserId")
        self.daily_cleanup_superbrowser(browser_id)

        retry_count = 0
        while True:
            try:
                retry_count += 1
                # 记录店铺账号与店铺别名对应关系
                cache_file = f'{self.config.auto_dir}/shein_store_alias.json'
                write_dict_to_file_ex(cache_file, {store_username: store_name}, [store_username])

                if is_skip_store and is_skip_store(store_username, store_name):
                    return

                if just_store_username is not None:
                    if store_username not in just_store_username:
                        log(f'=================================跳过 just_store_username: {store_name},{store_username}, {just_store_username}======================================')
                        return
                    else:
                        log(f'---------------------------------命中 just_store_username: {store_name},{store_username}, {just_store_username}-------------------------------------')

                if get_progress_json_ex(self.config, task_key, store_name):
                    log(f'=================================跳过 进度已完成: {task_key},{store_name},{store_username}=================================')
                    return

                # 打开店铺
                print(f"=====打开店铺：{store_name}=====")
                ret_json = self.browser.open_store(store_id)
                print(ret_json)
                store_id = ret_json.get("browserOauth") or ret_json.get("browserId")

                # 获取playwright浏览器会话
                with sync_api.sync_playwright() as playwright:
                    try:
                        browser_context = self.browser.get_browser_context(playwright, ret_json.get('debuggingPort'))
                        if browser_context is None:
                            print(f"=====关闭店铺：{store_name}=====")
                            self.browser.close_store(store_id)
                            return

                        # 获取ip检测页地址
                        ip_check_url = ret_json.get("ipDetectionPage")
                        if not ip_check_url:
                            print("ip检测页地址为空，请升级紫鸟浏览器到最新版")
                            print(f"=====关闭店铺：{store_name}=====")
                            self.browser.close_store(store_id)
                            raise RuntimeError("ip检测页地址为空")

                        ip_usable = self.browser.open_ip_check(browser_context, ip_check_url)
                        if ip_usable:
                            print("ip检测通过，打开店铺平台主页")
                            # 业务逻辑
                            try:
                                self.browser.open_launcher_page(browser_context, ret_json.get("launcherPage"), store_username, store_name, run_func, task_key)
                            except NetWorkIdleTimeout:
                                log('捕获到自定义错误: NetWorkIdleTimeout')
                                self.browser.close_store(store_id)
                                pass

                        else:
                            print("ip检测不通过，请检查")
                    except:
                        print("脚本运行异常:" + traceback.format_exc())
                        raise
                    finally:
                        print(f"=====关闭店铺：{store_name}=====")
                        self.browser.close_store(store_id)
                    break
            except:
                send_exception(f'第{retry_count}次运行失败，准备重新打开店铺: {store_username},{store_name},{store_id}')
                if retry_count > 5:
                    break

    def run_all_stores_task(self, browser_list: List[Dict[str, Any]],
            run_func: Callable, task_key: str,
            just_store_username: Optional[List[str]] = None,
            is_skip_store: Optional[Callable] = None
    ):
        """循环运行所有店铺的任务"""
        for browser_info in browser_list:
            self.run_single_store_task(browser_info, run_func, task_key, just_store_username, is_skip_store)

    def run_with_thread_pool(self, browser_list: List[Dict[str, Any]],
            max_threads: int = 3, run_func: Callable = None,
            task_key: str = None,
            just_store_username: Optional[List[str]] = None,
            is_skip_store: Optional[Callable] = None
    ):
        """使用线程池控制最大并发线程数运行任务"""
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            task = partial(self.run_single_store_task,
                           run_func=run_func, task_key=task_key,
                           just_store_username=just_store_username,
                           is_skip_store=is_skip_store)
            log(f'店铺总数: {len(browser_list)}')
            executor.map(task, browser_list)

class ZiniaoRunner:
    """紫鸟主运行器类"""

    def __init__(self, config):
        self.config = config
        os.environ['auto_dir'] = self.config.auto_dir
        os.environ['wxwork_bot_exception'] = self.config.wxwork_bot_exception

        self.client = ZiniaoClient(config)
        self.browser = ZiniaoBrowser(self.client, config)
        self.task_manager = ZiniaoTaskManager(self.browser, config)

    def execute(self, run_prepare: Optional[Callable] = None,
            run: Optional[Callable] = None,
            run_summary: Optional[Callable] = None,
            run_notify: Optional[Callable] = None,
            task_key: Optional[str] = None,
            just_store_username: Optional[List[str]] = None,
            is_skip_store: Optional[Callable] = None,
            platform_name: Optional[str] = "SHEIN-全球",
    ):
        """主执行入口"""
        # 前置执行 if run_prepare:
        run_prepare()

        # 终止紫鸟客户端已启动的进程
        self.client.kill_process()

        print("=====启动客户端=====")
        self.client.start_browser()
        print("=====更新内核=====")
        self.client.update_core()

        # 获取店铺列表
        print("=====获取店铺列表=====")
        browser_list = self.browser.get_browser_list(platform_name=platform_name)
        if not browser_list:
            print("browser list is empty")
            raise RuntimeError("店铺列表为空")

        # 多线程并发执行任务
        max_threads = 1 if (hostname().lower() == 'krrpa') else 3
        log(f'当前启用线程数: {max_threads}')
        self.task_manager.run_with_thread_pool(browser_list, max_threads, run, task_key, just_store_username, is_skip_store)

        # 任务重试逻辑
        try_times = 0
        while not check_progress_json_ex(self.config, task_key, just_store_username):
            try_times += 1
            send_exception(f'检测到任务未全部完成,再次执行: {try_times}')
            self.task_manager.run_with_thread_pool(browser_list, max_threads, run, task_key, just_store_username, is_skip_store)
            if try_times >= 4:
                send_exception(f'检测到任务未全部完成,再次执行: {try_times}')
                break

        # 数据汇总
        if not get_progress_json_ex(self.config, task_key, 'run_summary'):
            if run_summary:
                run_summary()
            done_progress_json_ex(self.config, task_key, 'run_summary')
        log('run_summary 完成')

        # 发送通知
        if not get_progress_json_ex(self.config, task_key, 'run_notify'):
            if run_notify:
                run_notify()
            done_progress_json_ex(self.config, task_key, 'run_notify')
        log('run_notify 完成')

        # 关闭客户端
        self.client.exit()

if __name__ == "__main__":
    pass
