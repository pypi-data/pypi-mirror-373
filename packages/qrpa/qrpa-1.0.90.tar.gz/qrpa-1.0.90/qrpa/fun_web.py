import json
from typing import Optional, Union
from playwright.sync_api import Page

from .fun_base import log, send_exception
from .time_utils import get_current_datetime

import inspect

def fetch(page: Page, url: str, params: Optional[Union[dict, list, str]] = None, headers: Optional[dict] = None, config:
Optional[dict] = None) -> dict:
    """
    发送 HTTP POST 请求，支持自定义 headers。

    :param page: Playwright 的 Page 对象
    :param url: 请求地址
    :param params: 请求参数（dict、list、str 或 None）
    :param headers: 自定义 headers 字典
    :return: 服务器返回的 JSON 响应（dict）
    """
    if params is not None and not isinstance(params, (dict, list, str)):
        raise ValueError("params 参数必须是 dict、list、str 或 None")
    if headers is not None and not isinstance(headers, dict):
        raise ValueError("headers 参数必须是 dict 或 None")

    try:
        page.wait_for_load_state('load')
        response = page.evaluate("""
            async ({ url, params, extraHeaders }) => {
                try {
                    const defaultHeaders = {
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
                        'x-requested-with': 'XMLHttpRequest',
                    };

                    const headers = Object.assign({}, defaultHeaders, extraHeaders || {});
                    const options = {
                        method: 'POST',
                        credentials: 'include',
                        headers: headers
                    };

                    if (params !== null) {
                        if (typeof params === 'string') {
                            options.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8';
                            options.body = params;
                        } else {
                            options.headers['Content-Type'] = 'application/json';
                            options.body = JSON.stringify(params);
                        }
                    }

                    const response = await fetch(url, options);
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status} - ${response.statusText}`);
                    }
                    return await response.json();
                } catch (error) {
                    return { "error": "fetch_failed", "message": error.message };
                }
            }
        """, {"url": url, "params": params, "extraHeaders": headers})

        return response
    except Exception as e:
        raise send_exception()
        # return {"error": "fetch error", "message": str(e)}

def fetch_via_iframe(page: Page, target_domain: str, url: str, params: Optional[Union[dict, list, str]] = None, config:
Optional[dict] = None) -> dict:
    """
    方案 2：在 iframe 内部执行 fetch 请求，绕过 CORS 限制

    :param page: Playwright 的 Page 对象
    :param url: 目标请求的 URL
    :param target_domain: 目标 iframe 所在的域名（用于匹配 iframe）
    :param params: 请求参数（dict、list、str 或 None）
    :return: 服务器返回的 JSON 响应（dict）
    """
    if params is not None and not isinstance(params, (dict, list, str)):
        raise ValueError("params 参数必须是 dict、list、str 或 None")
    response = None
    try:
        # 获取所有 iframe，查找目标域名的 iframe
        frames = page.frames
        target_frame = None
        for frame in frames:
            if target_domain in frame.url:
                target_frame = frame
                break

        if not target_frame:
            return {"error": "iframe_not_found", "message": f"未找到包含 {target_domain} 的 iframe"}

        response = target_frame.evaluate("""
            async ({ url, params }) => {
                try {
                    const options = {
                        method: 'POST',
                        credentials: 'include',
                        headers: {
                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
                            'x-requested-with': 'XMLHttpRequest',
                        }
                    };

                    if (params !== null) {
                        if (typeof params === 'string') {
                            options.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8';
                            options.body = params;
                        } else {
                            options.headers['Content-Type'] = 'application/json';
                            options.body = JSON.stringify(params);
                        }
                    }

                    const response = await fetch(url, options);
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status} - ${response.statusText}`);
                    }
                    return await response.json();
                } catch (error) {
                    return { "error": "iframe_fetch_failed", "message": error.message };
                }
            }
        """, {"url": url, "params": params})

        return response
    except Exception as e:
        raise send_exception()
        # return {"error": "iframe_exception", "message": str(e)}

# 找到一个页面里面所有的iframe
def find_all_iframe(page: Page):
    frames = page.frames
    for frame in frames:
        log("找到 iframe:", frame.url)
    return [frame.url for frame in frames]

# 全屏幕截图
def full_screen_shot(web_page: Page, config):
    # 设置页面的视口大小为一个较大的值，确保截图高清
    web_page.set_viewport_size({"width": 1920, "height": 1080})
    # 截取全页面的高清截图
    full_screenshot_image_path = f'{config.auto_dir}/screenshot/{get_current_datetime()}.png'
    web_page.screenshot(path=full_screenshot_image_path, full_page=True)
    return full_screenshot_image_path

def fetch_get(page: Page, url: str, headers: Optional[dict] = None, config: Optional[dict] = None) -> dict:
    """
    发送 HTTP GET 请求，支持自定义 headers 和配置。
    
    :param page: Playwright 的 Page 对象
    :param url: 请求地址
    :param headers: 自定义 headers 字典
    :param config: 请求配置字典，可包含 credentials, mode, referrer, referrerPolicy 等
    :return: 服务器返回的 JSON 响应（dict）
    """
    if headers is not None and not isinstance(headers, dict):
        raise ValueError("headers 参数必须是 dict 或 None")
    if config is not None and not isinstance(config, dict):
        raise ValueError("config 参数必须是 dict 或 None")

    try:
        page.wait_for_load_state('load')
        response = page.evaluate("""
            async ({ url, extraHeaders, config }) => {
                try {
                    const defaultHeaders = {
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
                    };

                    const defaultConfig = {
                        method: 'GET',
                        credentials: 'include',
                        mode: 'cors'
                    };

                    const headers = Object.assign({}, defaultHeaders, extraHeaders || {});
                    const options = Object.assign({}, defaultConfig, config || {}, { headers: headers });

                    const response = await fetch(url, options);
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status} - ${response.statusText}`);
                    }
                    return await response.json();
                } catch (error) {
                    return { "error": "fetch_failed", "message": error.message };
                }
            }
        """, {"url": url, "extraHeaders": headers, "config": config})

        return response
    except Exception as e:
        raise send_exception()

def safe_goto(page, url, **kwargs):
    caller = inspect.stack()[1]
    log(f"[DEBUG] goto called from {caller.filename}:{caller.lineno} url={url}")
    return page.goto(url, **kwargs)
