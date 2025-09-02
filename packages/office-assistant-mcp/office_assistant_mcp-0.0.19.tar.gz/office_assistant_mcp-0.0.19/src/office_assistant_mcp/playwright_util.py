import os
import tempfile
# os.environ['PWDEBUG'] = '1'  # 运行程序马上就进入Playwright调试模式
from playwright.async_api import async_playwright, Locator, Frame, Page, expect
import re
import asyncio
from shared.log_util import log_debug, log_info, log_error
import importlib.metadata
from dotenv import load_dotenv
import httpx
    
load_dotenv()

# 浏览器路径 - 从环境变量读取
# 示例配置：
# CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# 浏览器用户数据目录，指定目录，避免重复登录
# CHROME_USER_DATA_DIR = "/Users/kamous/Library/Application Support/Google/Chrome/playwright1"
CHROME_PATH = os.getenv("chrome_path")  # 如果环境变量中有chrome_path，则使用Chrome，否则使用Chromium
# CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CHROME_USER_DATA_DIR = None

from shared.browser_manager import get_playwright, reset_playwright_cache, create_new_tab, is_browser_available, update_global_page

"""
用户行为标签层级：
- 一级标签：.sql-item .sql-row(不包含右侧添加按钮)
    - 二级标签：.sql-row
"""

def get_current_version():
    """获取当前版本号"""
    return importlib.metadata.version("office_assistant_mcp")

# get_playwright 从 shared.browser_manager 导入



async def login_sso(page=None):
    """处理飞书SSO登录流程
    
    Args:
        page: 可选的页面实例，如果不提供则使用全局页面
    """
    if page is None:
        _, _, page = await get_playwright()

    # 检查页面是否包含"飞书登录"文本
    # 打印当前页面url
    log_info(f"当前页面url:{page.url}")
    if "sso.yunjiglobal.com/?backUrl=" in page.url:
        # 点击飞书登录按钮
        await page.get_by_text("飞书登录").click()
        log_info(f"等待飞书授权登录")
        # 等待"授权"按钮出现
        try:
            await page.wait_for_selector('button:has-text("授权")', timeout=30000)
            # 点击授权按钮
            log_debug("点击授权")
            await page.get_by_role("button", name="授权", exact=True).click()
            log_debug("登录成功")
            return "登录成功"
        except Exception as e:
            log_error(f"等待授权按钮出现时发生错误: {e}")
            return "登录失败"
    elif "accounts.feishu.cn" in page.url:
        # 等待"授权"按钮出现
        try:
            await page.wait_for_selector('button:has-text("授权")', timeout=30000)
            # 点击授权按钮
            log_debug("点击授权")
            await page.get_by_role("button", name="授权", exact=True).click()
            log_debug("登录成功")
            return "登录成功"
        except Exception as e:
            log_info(f"扫描登录")
            return "请用户扫码登录"
    else:
        # 页面不包含"飞书登录"文本，无需登录
        log_info(f"无需登录")
        return "无需登录"


async def open_create_customer_group_page(page=None):
    """打开客群列表页面并点击新建客群按钮
    
    Args:
        page: 可选的页面实例，如果不提供则使用全局页面
    """
    if page is None:
        _, _, page = await get_playwright()
        log_debug("open_create_customer_group_page: 使用全局页面实例")
    else:
        log_debug("open_create_customer_group_page: 使用指定页面实例")

    open_url = "https://portrait.yunjiglobal.com/customersystem/customerList?identify=cgs-cgm-customerList"
    # 打开客群列表页面
    await page.goto(open_url)

    login_result = await login_sso(page)
    log_debug(f"判断登录结果:{login_result}")
    if login_result == "登录成功":
        # 等待两秒
        await asyncio.sleep(2)
        log_debug(f"重新打开页面")
        await page.goto(open_url)
    elif login_result == "登录失败":
        return "登录失败，请提示用户使用飞书扫码登录"

    log_debug(f"开始新建客群")
    content = page.frame_locator("iframe")
    await content.get_by_role("button", name="新建客群").click()

    return "已进入新建客群页面"


async def open_create_customer_group_page_in_new_tab():
    """在新标签页中打开客群列表页面并点击新建客群按钮
    
    Returns:
        tuple: (page, result) - 页面实例和操作结果
    """
    # 创建新标签页
    new_page = await create_new_tab()
    log_info("已创建新标签页，准备打开客群创建页面")
    
    # 在新标签页中打开页面
    result = await open_create_customer_group_page(new_page)
    return new_page, result


async def smart_open_create_customer_group_page():
    """智能打开客群创建页面
    
    自动判断浏览器状态：
    - 如果浏览器已打开，在新标签页中执行任务
    - 如果浏览器未打开，先打开浏览器再执行任务
    
    Returns:
        tuple: (page, result) - 页面实例和操作结果信息
    """
    try:
        log_info("智能打开客群创建页面...")
        
        # 检查浏览器是否已经启动
        if is_browser_available():
            log_info("检测到浏览器已启动，在新标签页中执行任务")
            
            # 在新标签页中打开页面
            page, result = await open_create_customer_group_page_in_new_tab()
            
            # 如果打开页面失败（比如需要登录），返回结果
            if "登录失败" in result:
                log_error(f"新标签页打开失败: {result}")
                return None, result
            
            # 更新全局页面实例为新标签页
            update_global_page(page)
            
            log_info(f"新标签页任务完成: {result}")
            return page, f"[新标签页] {result}"
            
        else:
            log_info("浏览器未启动，使用传统方式处理")
            
            # 使用传统方式打开页面
            result = await open_create_customer_group_page()
            _, _, page = await get_playwright()
            
            return page, f"[首次启动] {result}"
            
    except Exception as e:
        error_msg = f"智能打开客群创建页面失败: {str(e)}"
        log_error(error_msg)
        return None, error_msg


async def fill_customer_group_info(group_name: str, business_type: str):
    """填写客群基本信息

    Args:
        group_name: 客群名称
        business_type: 业务类型
    """
    _, _, page = await get_playwright()
    content = page.frame_locator("iframe")

    # 填写客群名称
    await content.get_by_role("textbox", name="请输入字母、数字、下划线和汉字格式的客群名称，最多20字").click()
    await content.get_by_role("textbox", name="请输入字母、数字、下划线和汉字格式的客群名称，最多20字").fill(group_name)

    # 选择业务类型
    await content.get_by_role("textbox", name="请选择").click()
    await content.get_by_text(business_type).click()

    # 选择动态客群
    await content.get_by_role("radio", name="动态客群（每日0点重新按照筛选条件更新客群用户）").click()

    # 点击预估客群人数
    # await content.get_by_role("button", name="点我预估客群人数").click()

    return f"已填写客群基本信息：名称={group_name}，业务类型={business_type}"


async def print_iframe_snapshot(page):
    iframe = page.frame_locator("iframe")
    body = iframe.locator('body')
    snapshot = await body.aria_snapshot()
    log_debug(f"snapshot:{snapshot}")

    # log_debug(f"page accessibility:{await page.accessibility.snapshot()}")


async def fill_customer_group_user_tag_set_basic_info(
    identity_types: list[str] = None,
    v2_unregistered: str = None
):
    """
    新增客群的用户标签，填写用户身份及是否推客用户。
    
    Args:
        identity_types: 新制度用户身份，可多选，例如 ["P1", "V3"]
                       可选值包括: "P1", "P2", "P3", "P4", "V1", "V2", "V3", "VIP"
                       不区分大小写，如"p1"也会被识别为"P1"
        v2_unregistered: V2以上未注册推客用户，可选值: "是", "否"
    
    :return: 操作结果描述
    """
    _, _, page = await get_playwright()
    content = page.frame_locator("iframe")
    log_debug(f"start set basic info")
    # await print_iframe_snapshot(page)

    # 切换到基础信息和云集属性标签页
    await content.get_by_role("tab", name="基础信息").click()
    await content.get_by_role("tab", name="云集属性").click()
    
    # 处理新制度用户身份选项
    if identity_types and isinstance(identity_types, list):
        valid_identity_types = ["P1", "P2", "P3", "P4", "V1", "V2", "V3", "VIP"]
        # 创建大小写匹配字典
        identity_map = {item.upper(): item for item in valid_identity_types}
        
        for identity in identity_types:
            # 将用户输入转为大写进行匹配
            upper_identity = identity.upper() if isinstance(identity, str) else ""
            if upper_identity in identity_map:
                # 获取正确大小写的身份值
                actual_identity = identity_map[upper_identity]
                if actual_identity == "VIP":
                    # VIP选项有多个，需要使用nth(1)
                    await content.get_by_text(actual_identity, exact=True).nth(1).click()
                else:
                    await content.get_by_text(actual_identity, exact=True).click()
    
    # 处理V2以上未注册推客用户选项
    if v2_unregistered in ["是", "否"]:
        # 获取云集属性标签下的"是"或"否"选项
        await content.get_by_label("云集属性").get_by_text(v2_unregistered, exact=True).nth(4).click()

    return "已完成用户标签基础信息填写"


async def click_add_behavior_tag_button(tag_position: str = "left", page=None) -> str:
    """点击添加行为标签按钮
    
    Args:
        tag_position: 标签添加按钮位置，可选值：
                    - "left"：点击左侧添加按钮，添加一级标签（默认）
                      用于添加所有同级标签（无论是否用"且"或"或"连接）
                    - "right"：点击右侧添加按钮，添加子标签
                      仅用于添加某个标签组内的子标签（有嵌套关系时）
                    
                    例如：
                    - "A且B且C"结构：三个都是一级标签，都使用"left"
                    - "A或(B且C)"结构：A和B使用"left"，C使用"right"
        page: 可选的页面实例，如果不提供则使用全局页面
    
    Returns:
        str: 操作结果描述
    """
    if page is None:
        _, _, page = await get_playwright()
    content = page.frame_locator("iframe")
    if tag_position == "left":
        # 点击左侧的添加按钮，添加一级标签
        # add_button = content.get_by_role("button", name=" 添加")
        # 正则匹配添加按钮
        add_button = content.locator("button").filter(has_text=re.compile(r"^\s*添加\s*$"))
        await add_button.is_enabled()
        await add_button.click()
        return "已点击左侧添加按钮，添加一级标签"
    elif tag_position == "right":
        # 点击最后一行右侧的添加按钮，添加子标签
        # 获取所有行
        item = content.locator(".sql-item").last
        icon_count = await item.locator(".add-icon").count()
        log_debug(f"当前有{icon_count}个添加按钮")
        await item.locator(".add-icon").nth(icon_count - 2).click() # 倒数第2个按钮
        return f"已点击右侧添加按钮，添加子标签"
    else:
        return f"错误：标签位置参数无效，只支持'left'或'right'"


async def fill_behavior_tag_form(
    row_index: int,
    time_range_type: str = "最近",
    time_range_value: str = None,
    action_type: str = "做过",
    theme: str = "购买", 
    dimension: str = None, 
    dimension_condition: str = None,
    dimension_value: str = None,
    metric: str = None,
    metric_condition: str = None,
    metric_value: str = None,
    metric_value_end: str = None 
):
    """填写指定行的行为标签表单
    
    Args:
        row_index: 要填写的标签行索引，从0开始
        time_range_type: 时间范围类型："最近"或"任意时间"
        time_range_value: 时间范围值，天数，如："7"
        action_type: 行为类型："做过"或"没做过"
        theme: 主题："购买"或"搜索"等
        dimension: 维度选项
        dimension_condition: 维度条件
        dimension_value: 维度值
        metric: 指标名称
        metric_condition: 指标条件
        metric_value: 指标值
        metric_value_end: 指标范围结束值，仅当metric_condition="介于"时使用
    
    Returns:
        str: 操作结果描述
    """
    _, _, page = await get_playwright()
    # await page.pause()
    content = page.frame_locator("iframe")
    
    # 获取所有行
    rows = content.locator(".sql-row")
    row_count = await rows.count()
    
    if row_index < 0 or row_index >= row_count:
        return f"错误：标签行索引{row_index}超出范围，当前共有{row_count}行"
    
    # 获取指定的行
    item = rows.nth(row_index)
    
    # 选择时间范围类型
    await item.locator(".el-select__caret").first.click()
    await content.get_by_role("listitem").filter(has_text=time_range_type).click()

    # 填写时间范围值
    if time_range_value:
        await item.get_by_role("textbox", name="天数").last.fill(time_range_value)

    # 选择行为类型（做过/没做过）
    await item.get_by_role("textbox", name="请选择").nth(0).click()
    await content.get_by_role("listitem").filter(has_text=re.compile(f"^{action_type}$")).click()

    # 选择主题
    await item.get_by_role("textbox", name="选择主题").last.click()
    await content.get_by_role("listitem").filter(has_text=theme).click()

    # 根据是否有维度来确定指标的位置
    textbox_index = 1  # 初始值，用于追踪当前到了第几个"请选择"框
    input_index = 0    # 初始值，用于追踪当前到了第几个"请输入"框

    # 设置维度（如果有）
    if dimension:
        # 选择维度
        await item.get_by_role("textbox", name="选择维度").last.click()
        await content.get_by_role("listitem").filter(has_text=re.compile(f"^{dimension}$")).click()

        # 设置维度条件
        if dimension_condition:
            await item.get_by_role("textbox", name="请选择").nth(textbox_index).click()
            await content.get_by_role("listitem").filter(has_text=re.compile(f"^{dimension_condition}$")).click()
            textbox_index += 1
            # 填写维度值
            if dimension_value:
                # 检查是否是需要从下拉列表中选择的类目
                need_dropdown_selection = dimension in ["后台一级类目", "后台二级类目", "后台三级类目", "后台四级类目", "商品品牌"]
                
                # 处理多个维度值，支持中英文逗号分隔
                dimension_values = []
                if ',' in dimension_value or '，' in dimension_value:
                    for sep in [',', '，']:
                        if sep in dimension_value:
                            dimension_values.extend([v.strip() for v in dimension_value.split(sep) if v.strip()])
                else:
                    dimension_values = [dimension_value]

                
                log_debug(f"处理维度值: {dimension_values}")
                
                for value in dimension_values:
                    if not value:
                        continue
                        
                    if need_dropdown_selection:
                        dimension_input = rows.nth(row_index).locator(".el-select__input").nth(input_index)
                    else:
                        dimension_input = item.get_by_role("textbox", name="请输入").nth(input_index)
                    
                    await dimension_input.click()
                    await dimension_input.fill(value) 
                    await asyncio.sleep(0.5)
                    
                    if need_dropdown_selection:
                        # 获取所有列表项
                        list_items = content.get_by_role("listitem")
                        count = await list_items.count()
                        log_debug(f"找到 {count} 个下拉选项")
                        
                        # 修改：只有当dimension=="商品品牌"时才勾选所有下拉列表，其他情况只勾选第一个选项
                        if dimension == "商品品牌":
                            # 勾选所有选项
                            for i in range(count):
                                # 给UI一些响应时间
                                await asyncio.sleep(0.2)
                                item = list_items.nth(i)
                                # 获取文本内容（可选）
                                text = await item.text_content()
                                log_debug(f"点击下拉选项: {text}")
                                # 点击选项
                                await item.click()
                        else:
                            # 其他维度只勾选第一个选项
                            if count > 0:
                                await asyncio.sleep(0.2)
                                item = list_items.nth(0)
                                text = await item.text_content()
                                log_debug(f"点击第一个下拉选项: {text}")
                                await item.click()
                    
                    # 点击空白区域
                    await content.locator(".custom-editer > div").first.click()
                    await asyncio.sleep(0.2)

                
                input_index += 1

    # 设置指标
    if metric:
        # 如果没有选择维度，则从维度选项框里选择指标
        metric_title = "选择指标"
        metric_input_index = -1
        if not dimension:
            metric_title = "选择维度"
            metric_input_index = row_index
        metric_inputs = content.get_by_placeholder(metric_title)
        
        log_debug(f"{metric_title}数量：{await metric_inputs.count()}，指标输入框索引：{metric_input_index}")
        metric_input = metric_inputs.nth(metric_input_index)
        await metric_input.wait_for(state="visible", timeout=5000)
        await metric_input.click()
        await content.get_by_role("listitem").filter(has_text=re.compile(f"^{metric}$")).click()

        # 设置指标条件
        if metric_condition:
            # await item.get_by_role("textbox", name="请选择").last.click()  # item 上不一定能找到”请选择“框
            select_count = await content.get_by_role("textbox", name="请选择").count()
            metric_condition_index = select_count - (row_count - 1 - row_index) * 2 - 1
            log_debug(f"请选择框个数: {select_count}, 指标条件索引: {metric_condition_index}")
            await content.get_by_role("textbox", name="请选择").nth(metric_condition_index).click()
            await content.get_by_role("listitem").filter(has_text=re.compile(f"^{metric_condition}$")).click()

            # 填写指标值
            if metric_value:
                metric_input = content.get_by_role("textbox", name="请输入")
                metric_input_count = await metric_input.count() - (row_count - 1 - row_index)
                if metric_condition == "介于" and metric_value_end:
                    await metric_input.nth(metric_input_count - 2).click()
                    await metric_input.nth(metric_input_count - 2).fill(metric_value)
                    await metric_input.nth(metric_input_count - 1).click()
                    await metric_input.nth(metric_input_count - 1).fill(metric_value_end)
                else:
                    await metric_input.nth(metric_input_count - 1).click()
                    await metric_input.nth(metric_input_count - 1).fill(metric_value)
                
    return f"已填写第{row_index+1}行{theme}用户行为标签"


async def toggle_relation_to_or(relation_position: int = 0):
    """将指定的且关系切换为或关系
    
    Args:
        relation_position: 关系位置，表示要修改的第几个"且"关系，从0开始计数
                         - 0: 第一个"且"关系（通常是一级标签之间的关系）
                         - 1: 第二个"且"关系（通常是同一级标签下的二级标签之间的关系）
                         依此类推
    
    Returns:
        str: 操作结果描述
    """
    _, _, page = await get_playwright()
    content = page.frame_locator("iframe")
    # 获取所有"且"按钮
    and_buttons = content.locator(".logicBar")
    count = await and_buttons.count()
    print(f"当前有{count}个且关系")
    if relation_position < 0 or relation_position >= count:
        return f"错误：关系位置{relation_position}超出范围，当前共有{count}个且关系"
    
    # 点击指定的"且"按钮
    await and_buttons.nth(relation_position + 1).click() # 有一个隐藏的且
    
    return f"已将第{relation_position+1}个关系从「且」切换为「或」"


# 保留原有的add_user_behavior_common_tags函数，以保持向后兼容性
async def add_user_behavior_search_tags_test():
    """添加一个搜索主题的用户行为标签"""
    return await add_user_behavior_common_tags(
        time_range_type="最近",
        time_range_value="10",
        action_type="没做过",
        theme="搜索",
        dimension="搜索词",
        dimension_condition="包含",
        dimension_value="轻姿养",
        metric="搜索次数",
        metric_condition=">=",
        metric_value="1"
    )


async def add_user_behavior_common_tags(
    time_range_type: str = "最近",
    time_range_value: str = None,
    action_type: str = "做过",
    theme: str = "购买", 
    dimension: str = None, 
    dimension_condition: str = None,
    dimension_value: str = None,
    metric: str = None,
    metric_condition: str = None,
    metric_value: str = None,
    metric_value_end: str = None 
):
    """添加一个通用的用户行为标签

    Args:
        time_range_type: 时间范围类型："最近"或"任意时间"
        time_range_value: 时间范围值，天数，如："7"
        action_type: 行为类型："做过"或"没做过"
        theme: 主题："购买"或"搜索"等
        dimension: 维度选项。当theme="购买"时可用：
            - 类目相关：["后台一级类目", "后台二级类目", "后台三级类目", "后台四级类目"]
              (条件均为=或!=，值为字符串，支持下拉列表多选)
            - 商品相关：["商品品牌", "商品名称", "商品id"] 
              (条件均为=或!=，品牌需从下拉列表选择，其他为字符串)
        dimension_condition: 维度条件：通常为=或!=
        dimension_value: 维度值：根据dimension类型提供相应字符串，多个值可用逗号(,或，)分隔
        metric: 指标名称。当theme="购买"时可用：
            ["购买金额", "购买件数", "购买净金额", "购买订单数"]
            (所有指标条件均支持=, >=, <=, <, >，值均为数字)
        metric_condition: 指标条件：=, >=, <=, <, >, 介于
        metric_value: 指标值：数字类型，当metric_condition="介于"时为范围开始值
        metric_value_end: 指标范围结束值：仅当metric_condition="介于"时使用
    """
    # 点击添加按钮
    await click_add_behavior_tag_button(tag_position="left")
    
    # 获取当前所有行数
    _, _, page = await get_playwright()
    content = page.frame_locator("iframe")
    rows = content.locator(".sql-row")
    row_count = await rows.count()
    log_debug(f"标签当前有{row_count}行")
    # 填写最后一行的表单
    return await fill_behavior_tag_form(
        row_index=row_count-1,
        time_range_type=time_range_type,
        time_range_value=time_range_value,
        action_type=action_type,
        theme=theme,
        dimension=dimension,
        dimension_condition=dimension_condition,
        dimension_value=dimension_value,
        metric=metric,
        metric_condition=metric_condition,
        metric_value=metric_value,
        metric_value_end=metric_value_end
    )


async def toggle_behavior_tag_relation_to_or():
    """将用户行为标签之间的关系从"且"切换为"或"

    用户行为标签之间默认是"且"关系，即用户需要同时满足所有标签条件。
    本函数用于将这种关系切换为"或"关系，即用户只需满足任一标签条件。
    此函数默认修改第一个"且"关系（一级标签之间的关系）。

    Returns:
        str: 操作结果描述
    """
    return await toggle_relation_to_or(relation_position=0)


def is_within_expected_range(actual: int, expected: int, tolerance: float = 0.2) -> bool:
    """检查实际人数是否在期望人数的容差范围内
    
    Args:
        actual: 实际客群人数
        expected: 期望客群人数
        tolerance: 容差百分比，默认为0.2（20%）
    
    Returns:
        bool: 是否在容差范围内
    """
    if expected == 0:
        return True
    
    difference = abs(actual - expected)
    return difference <= expected * tolerance


async def estimate_customer_group_size(get_estimate: bool = False, expected_size: int = 0):
    """预估客群人数
    Args:
        get_estimate: 是否获取预估人数，默认为False
        expected_size: 期望客群人数，默认为0（不进行比较）
    Returns:
        str: 操作结果描述
    """
    _, _, page = await get_playwright()
    content = page.frame_locator("iframe")
    # 设置API拦截器
    # await setup_api_mock()

    # 等待预估结果出现
    try:
        # await page.pause()
        # 等待按钮变为可点击状态，最多等待60秒
        button = content.get_by_role("button", name="点我预估客群人数")
        log_info(f"等待预估按钮变为可点击状态，最长等待60秒")
        await button.wait_for(state="visible", timeout=60000)
        # 等待按钮可见并启用，最多等待60秒
        for i in range(60):  # 每秒检查一次，最多60次
            try:
                if await button.is_visible() and await button.is_enabled():
                    # 检查按钮是否还有loading样式
                    button_class = await button.get_attribute("class")
                    if "is-loading" not in (button_class or ""):
                        log_info(f"预估按钮已变为可点击状态")
                        break
                    else:
                        log_debug(f"按钮仍在loading状态，继续等待... ({i+1}/60)")
                else:
                    log_debug(f"按钮尚未准备就绪，继续等待... ({i+1}/60)")
                await asyncio.sleep(1)
            except Exception as check_error:
                log_debug(f"检查按钮状态时出错: {check_error}，继续等待...")
                await asyncio.sleep(1)
        else:
            log_info(f"等待60秒后，按钮状态: 可见={await button.is_visible()}, 可用={await button.is_enabled()}")
        
        # 点击预估客群人数按钮
        await button.click()
        # await asyncio.sleep(2)  # 等待2秒，给系统一些响应时间
        
        if get_estimate:
            # 等待预估结果出现，最长等待120秒
            try:
                log_info(f"等待预估结果出现，最长等待120秒")
                import re
                estimate_element = content.get_by_text(re.compile(r"当前条件下.*客群人数预估为.*人"))
                await estimate_element.wait_for(timeout=30000)  # 120秒超时
                
                # 获取元素文本并提取数字
                element_text = await estimate_element.text_content()
                log_debug(f"预估结果文本: {element_text}")
                if element_text:
                    # 使用正则表达式提取数字，更灵活的匹配
                    number_match = re.search(r'预估为\s*(\d+)\s*人', element_text)
                    if number_match:
                        estimated_count = int(number_match.group(1))
                        
                        # 如果设置了期望人数，进行比较
                        if expected_size > 0:
                            if is_within_expected_range(estimated_count, expected_size):
                                return f"已点击客群人数预估，客群人数预估{estimated_count}人，与期望人数{expected_size}相差在20%以内，创建任务结束"
                            else:
                                difference_percentage = abs(estimated_count - expected_size) / expected_size * 100
                                return f"已点击客群人数预估，客群人数预估{estimated_count}人，与期望人数{expected_size}相差{difference_percentage:.1f}%，相差较大，请继续优化筛选条件"
                        else:
                            return f"已点击客群人数预估，客群人数预估{estimated_count}人"
                
                return "已点击客群人数预估，未获取到预估人数"
            except Exception as wait_error:
                log_error(f"等待预估结果时出错: {wait_error}")
                return "已点击客群人数预估，未获取到预估人数"
        else:
            # await page.pause()
            return "已点击客群人数预估"
    except Exception as e:
        log_error(f"预估客群人数时出错: {e}")
        return f"预估客群人数时出错: {str(e)}"


async def send_llm_request(content: str) -> str:
    """
    发送LLM请求
    
    Args:
        content: 请求内容
        
    Returns:
        str: 响应内容
    """
    # 从环境变量中读取llm_key
    llm_key = os.environ.get("llm_key")
    if not llm_key:
        log_error("环境变量llm_key未设置")
        raise ValueError("环境变量llm_key not found，请联系管理员设置llm_key")
    url = "https://talentshot.yunjiglobal.com/digitalhuman/api/llm/completions"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {llm_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "content": content,
        "model": "deepseek",
        "history_message": [],
        "temperature": 0.3,
        "timeout": 60,
        "trace_tags": [],
        "trace_session_id": "",
        "trace_user_id": ""
    }
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(url, headers=headers, json=payload, timeout=120)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0 and "data" in result and "content" in result["data"]:
                    return result["data"]["content"]
                else:
                    log_error(f"LLM响应格式异常: {result}")
                    return f"LLM响应格式异常: {result}"
            else:
                log_error(f"LLM请求失败，状态码: {response.status_code}")
                return f"LLM请求失败，状态码: {response.status_code}"
    except Exception as e:
        log_error(f"发送LLM请求时出错: {str(e)}")
        return f"发送LLM请求时出错: {str(e)}"


async def setup_api_mock():
    """设置API拦截器，拦截客群人数预估接口并返回来自JSON文件的响应"""
    import json
    import os
    
    _, _, page = await get_playwright()
    
    # 获取JSON文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, "predictPersonCount.json")
    
    async def handle_route(route):
        url = route.request.url
        if "usergroupadmin/v1/api/customGroup/predictPersonCount" in url:
            log_info(f"拦截到客群人数预估接口: {url}")
            
            try:
                # 读取JSON文件内容
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    response_data = json.load(f)
                
                # 转换为JSON字符串
                response_body = json.dumps(response_data, ensure_ascii=False)
                log_info(f"从文件读取响应数据: {response_body}")
                
                # 返回文件中的响应数据
                await route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=response_body
                )
            except Exception as e:
                log_error(f"读取预设响应文件时发生错误: {e}")
                # 使用默认响应
                await route.fulfill(
                    status=200,
                    content_type="application/json",
                    body='{"errorCode":"1","errorMsg":"读取预设响应文件失败","data":"0"}'
                )
        else:
            # 其他请求正常通过
            await route.continue_()
    
    # 设置路由拦截
    await page.route("**/*", handle_route)
    log_info(f"已设置API拦截器，将拦截客群人数预估接口，响应数据来源: {json_file_path}")
    return "已设置API拦截器"
