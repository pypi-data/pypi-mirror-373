import os
import tempfile
from typing import Tuple, Optional, List
from playwright.async_api import async_playwright, Playwright, BrowserContext, Page
from shared.log_util import log_debug, log_info, log_error

# 浏览器路径配置 - 从环境变量读取
CHROME_PATH = os.getenv("chrome_path")  # 如果环境变量中有chrome_path，则使用Chrome，否则使用Chromium
# CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CHROME_USER_DATA_DIR = None

# 全局变量用于缓存playwright实例
_playwright_instance: Optional[Playwright] = None
_browser_instance: Optional[BrowserContext] = None
_page_instance: Optional[Page] = None

# 管理所有创建的页面实例
_all_pages: List[Page] = []


def reset_playwright_cache():
    """重置playwright缓存，以便创建新的浏览器和页面实例"""
    log_info("reset playwright cache")
    global _playwright_instance, _browser_instance, _page_instance
    _playwright_instance = None
    _browser_instance = None
    _page_instance = None


async def remove_lock_files():
    """删除浏览器用户数据目录下的锁文件，防止浏览器打不开"""
    if not CHROME_USER_DATA_DIR:
        log_info("使用默认chromium浏览器，无需清理缓存")
        return
        
    lock_files_to_remove = ["SingletonLock", "SingletonCookie", "SingletonSocket"]
    if os.path.exists(CHROME_USER_DATA_DIR):
        for file_name in lock_files_to_remove:
            file_path = os.path.join(CHROME_USER_DATA_DIR, file_name)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    log_info(f"Successfully removed lock file: {file_path}")
                except OSError as e:
                    log_info(f"Error removing lock file {file_path}: {e}")
    else:
        log_info(f"User data directory not found, skipping lock file cleanup: {CHROME_USER_DATA_DIR}")


async def create_playwright(user_data_dir_name: str = "office_assistant_mcp_chrome_user_data") -> Tuple[Playwright, BrowserContext]:
    """创建playwright实例
    
    Args:
        user_data_dir_name: 用户数据目录名称，不同业务可以使用不同的目录
    """
    global CHROME_USER_DATA_DIR
    
    # 如果CHROME_USER_DATA_DIR为空，则在临时目录下创建一个固定的用户数据目录
    if CHROME_USER_DATA_DIR is None:
        temp_dir = os.path.join(tempfile.gettempdir(), user_data_dir_name)
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        CHROME_USER_DATA_DIR = temp_dir
        log_info(f"使用Chrome临时用户数据目录: {CHROME_USER_DATA_DIR}")
        
    await remove_lock_files()
    p = await async_playwright().start()
    
    # 浏览器启动参数
    launch_options = {
        'user_data_dir': CHROME_USER_DATA_DIR,
        'headless': False,  # 显示浏览器界面
        'args': ['--window-size=1920,900', '--ignore-certificate-errors']  # 设置窗口大小为1920x1000
    }
    
    # 如果CHROME_PATH不为空，则使用指定的浏览器路径
    if CHROME_PATH:
        launch_options['executable_path'] = CHROME_PATH
        log_info(f"使用Chrome浏览器，路径: {CHROME_PATH}")
    else:
        log_info("使用默认Chromium浏览器")
    log_info(f"launch_options: {launch_options}")
    browser = await p.chromium.launch_persistent_context(**launch_options)
    return p, browser


async def get_playwright() -> Tuple[Playwright, BrowserContext, Page]:
    """获取playwright对象,如果没有则新建，有则返回全局缓存的对象"""
    global _playwright_instance, _browser_instance, _page_instance

    if _playwright_instance is None or _browser_instance is None or _page_instance is None:
        log_debug(f"获取playwright，创建新实例")
        _playwright_instance, _browser_instance = await create_playwright()
        _page_instance = await _browser_instance.new_page()
        _page_instance.set_default_timeout(5000)
        _all_pages.append(_page_instance)
    else:
        log_debug(f"获取playwright，使用缓存")
    
    # 确保所有实例都不为None
    assert _playwright_instance is not None
    assert _browser_instance is not None
    assert _page_instance is not None
    
    return _playwright_instance, _browser_instance, _page_instance


async def create_new_tab() -> Page:
    """创建新的标签页
    
    Returns:
        Page: 新创建的页面实例
    """
    global _browser_instance
    
    # 确保browser实例存在
    if _browser_instance is None:
        _, _browser_instance, _ = await get_playwright()
    
    # 创建新页面
    new_page = await _browser_instance.new_page()
    new_page.set_default_timeout(5000)
    _all_pages.append(new_page)
    
    log_info(f"创建新标签页，当前总标签页数量: {len(_all_pages)}")
    return new_page


async def close_tab(page: Page):
    """关闭指定的标签页
    
    Args:
        page: 要关闭的页面实例
    """
    global _all_pages
    
    try:
        await page.close()
        if page in _all_pages:
            _all_pages.remove(page)
        log_info(f"已关闭标签页，剩余标签页数量: {len(_all_pages)}")
    except Exception as e:
        log_error(f"关闭标签页失败: {e}")


async def close_all_tabs():
    """关闭所有标签页"""
    global _all_pages
    
    for page in _all_pages.copy():
        try:
            await page.close()
        except Exception as e:
            log_error(f"关闭标签页失败: {e}")
    
    _all_pages.clear()
    log_info("已关闭所有标签页")


async def close_playwright():
    """关闭并清除缓存的playwright和browser实例"""
    log_debug(f"close playwright")
    global _playwright_instance, _browser_instance, _page_instance, _all_pages

    # 先关闭所有标签页
    await close_all_tabs()

    if _browser_instance:
        await _browser_instance.close()
        _browser_instance = None

    if _playwright_instance:
        await _playwright_instance.stop()
        _playwright_instance = None

    _page_instance = None
    _all_pages = []


def update_global_page(page: Page):
    """更新全局页面实例
    
    Args:
        page: 新的页面实例
    """
    global _page_instance
    _page_instance = page
    log_info(f"已更新全局页面实例")


def is_browser_available() -> bool:
    """检查浏览器是否已经启动并可用
    
    Returns:
        bool: 浏览器可用返回True，否则返回False
    """
    global _browser_instance, _playwright_instance
    
    # 检查浏览器实例和playwright实例是否都存在
    if _browser_instance is not None and _playwright_instance is not None:
        try:
            # 尝试获取浏览器上下文的页面，检查是否真的可用
            # 如果浏览器上下文被关闭，这个调用会抛出异常
            pages = _browser_instance.pages
            
            # 检查是否有页面存在
            if len(pages) > 0:
                # 尝试访问第一个页面的 URL 来确认页面是否可用
                # 这个调用会在浏览器上下文被关闭时抛出异常
                _ = pages[0].url
                return True
            else:
                # 没有页面，认为浏览器不可用，需要重新启动
                log_info("没有页面，认为浏览器不可用，重置缓存")
                reset_playwright_cache()
                return False
                
        except Exception as e:
            log_info(f"浏览器实例检查失败: {e}")
            # 如果是浏览器上下文被关闭的异常，重置缓存
            if "Target page, context or browser has been closed" in str(e):
                log_info("检测到浏览器上下文已关闭，重置缓存")
                reset_playwright_cache()
            return False
    
    return False