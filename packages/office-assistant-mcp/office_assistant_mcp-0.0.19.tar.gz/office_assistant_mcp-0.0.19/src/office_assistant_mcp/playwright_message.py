import asyncio
from playwright.async_api import Page
from shared.log_util import log_debug, log_info, log_error
from shared.browser_manager import get_playwright, create_new_tab, is_browser_available

# 导入必要的函数
from office_assistant_mcp.playwright_util import login_sso


async def open_create_message_plan_page(page=None):
    """打开创建短信计划页面，以便创建短信计划
    
    Args:
        page: 可选的页面实例，如果不提供则使用全局页面
    """
    if page is None:
        _, _, page = await get_playwright()
        log_debug("open_create_message_plan_page: 使用全局页面实例")
    else:
        log_debug("open_create_message_plan_page: 使用指定页面实例")
        
    log_debug(f"open_create_message_plan_page:{page}")
    open_url = "https://portrait.yunjiglobal.com/customersystem/plan"
    # 打开短信计划列表页面
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

    return "已进入短信计划列表页面"


async def open_create_message_plan_page_in_new_tab():
    """在新标签页中打开短信计划页面
    
    Returns:
        tuple: (page, result) - 页面实例和操作结果
    """
    # 创建新标签页
    new_page = await create_new_tab()
    log_info("已创建新标签页，准备打开短信计划页面")
    
    # 在新标签页中打开页面
    result = await open_create_message_plan_page(new_page)
    return new_page, result


async def smart_open_create_message_plan_page():
    """智能打开短信计划页面
    
    自动判断浏览器状态：
    - 如果浏览器已打开，在新标签页中执行任务
    - 如果浏览器未打开，先打开浏览器再执行任务
    
    Returns:
        str: 操作结果信息
    """
    try:
        log_info("智能打开短信计划页面...")
        
        # 检查浏览器是否已经启动
        if is_browser_available():
            log_info("检测到浏览器已启动，在新标签页中执行任务")
            
            # 在新标签页中打开页面
            page, result = await open_create_message_plan_page_in_new_tab()
            
            # 如果打开页面失败（比如需要登录），返回结果
            if "登录失败" in result:
                log_error(f"新标签页打开失败: {result}")
                return result
            
            log_info(f"新标签页任务完成: {result}")
            return f"[新标签页] {result}"
            
        else:
            log_info("浏览器未启动，使用传统方式处理")
            
            # 使用传统方式打开页面
            result = await open_create_message_plan_page()
            
            return f"[首次启动] {result}"
            
    except Exception as e:
        error_msg = f"智能打开短信计划页面失败: {str(e)}"
        log_error(error_msg)
        return error_msg


async def fill_message_group_id(group_id):
    """创建短信计划，填写和选择指定的客群
    
    Args:
        group_id: 客群ID，格式为数字字符串，例如："1050792"
    """
    _, _, page = await get_playwright()
    
    # 搜索客群ID
    await page.get_by_placeholder("请输入人群ID搜索").click()
    await page.get_by_placeholder("请输入人群ID搜索").fill(group_id)
    # 点击搜索按钮
    await page.locator("i.el-icon-search").first.click()
    
    # 检查是否存在"人群ID"文本，这表示结果列表显示了

    id_input = page.get_by_text("人群ID")
    await id_input.wait_for(state="visible", timeout=3000)
    id_input_count = await id_input.count()
    log_debug(f"人群ID count:{id_input_count}")
    if id_input_count == 0:
        return f"提醒用户，未搜到{group_id}客群"

    return f"已搜索并选择客群ID: {group_id}"


async def fill_message_plan_info(plan_name, send_date, send_time):
    """填写短信计划的标题、发送日期和时间
    
    Args:
        plan_name: 计划名称，格式为字符串，例如："0412高质量用户圣牧纯牛奶"
        send_date: 发送日期，格式为"YYYY-MM-DD"，例如："2025-04-12"
        send_time: 发送时间，格式为"HH:MM:SS"，例如："18:00:00"
    """
    _, _, page = await get_playwright()
    form = page.locator("form").first
    # 填写计划名称
    name_input = form.get_by_role("textbox").first
    log_debug(f"name_input:{name_input}, count:{await name_input.count()}")
    log_debug(f"name_input.is_visible():{await name_input.is_visible()}, is_editable:{await name_input.is_editable()}")
    await name_input.click()
    await name_input.fill(plan_name)
    
    # 设置发送日期和时间
    await page.get_by_role("textbox", name="选择日期").click()
    await page.get_by_role("textbox", name="选择日期").nth(1).click()
    await page.get_by_role("textbox", name="选择日期").nth(1).fill(send_date)
    
    await page.get_by_role("textbox", name="选择时间").click()
    await page.get_by_role("textbox", name="选择时间").press("ControlOrMeta+a")
    await page.get_by_role("textbox", name="选择时间").fill(send_time)
    
    # 点击确定按钮
    await page.get_by_role("button", name="确定").nth(1).click()
    
    # 选择无AB测
    await page.get_by_role("radio", name="无AB测").click()
    
    return f"已填写短信计划基本信息：计划名称={plan_name}，发送时间={send_date} {send_time}"


async def fill_message_content(content, product_id):
    """设置发送短信的文本内容，通过商品id生成并插入商品链接
    
    Args:
        content: 短信内容，格式为字符串，例如："哪吒联名款纯牛奶！单提装送礼优选~圣牧有机纯牛奶10包仅需28.9元＞"
        product_id: 商品ID，格式为数字字符串，例如："962956"
    """
    _, _, page = await get_playwright()
    # 取消App推送勾选
    await page.locator("span.el-checkbox__label:has-text('App推送')").nth(0).click() # 外层有button，只有使用css定位
    await page.get_by_role("button", name="App推送").click()
    await page.locator("span.el-checkbox__label:has-text('短信发送')").nth(0).click()
    
    # 选择短信发送方式
    await page.get_by_role("button", name="短信发送").click()
    await page.get_by_role("radio", name="人工营销短信").click()
    
    # 填写短信内容
    await page.get_by_role("textbox", name="请输入短信内容").click()
    await page.get_by_role("textbox", name="请输入短信内容").fill(content)
    
    # 插入商品链接
    await page.get_by_role("button", name="插入链接").click()
    await page.get_by_role("radio", name="商品详情(唤醒小程序)").click()
    await page.get_by_role("textbox", name="请输入商品id").click()
    await page.get_by_role("textbox", name="请输入商品id").fill(product_id)
    await page.get_by_role("button", name="转换").click()
    await asyncio.sleep(1)
    
    await page.get_by_role("button", name="确 定").click()
    
    return f'已设置短信内容和商品链接：短信内容={content}，商品ID={product_id}。'


async def set_department_info():
    """设置费用归属部门和执行后时间"""
    _, _, page = await get_playwright()
    # 选择费用归属部门
    await page.get_by_role("textbox", name="请选择费用归属部门").click()
    await page.get_by_role("menuitem", name="云集").first.click()
    await page.get_by_text("前台").click()
    await page.get_by_text("云集事业部").click()  # 云集 / 前台 / 云集事业部 / 渠道中心 / 销售组 / 营销策划
    await page.get_by_text("渠道中心").click()
    await page.get_by_text("销售组").click()
    await page.get_by_role("menuitem", name="营销策划").get_by_role("radio").click()
    
    # 空白地方点击一下
    await page.get_by_role("heading", name="效果追踪").click()
    
    return '已设置默认费用归属部门。请用户人工检查填写的表单，再点击"提交"执行计划！'


def judge_category_or_brand_type(keyword: str) -> str:
    """判断关键词属于哪个类目层级、是否是品牌、或者是商品名
    
    Args:
        keyword: 用户输入的关键词，如"面膜"、"素野"等
    
    Returns:
        判断结果，格式为：
        - 如果是类目："{类目级别}：{类目名称}"，如"类目：后台一级类目"
        - 如果是品牌："品牌：{品牌名称}"，如"品牌：素野"
        - 如果以上都不是："商品名：{关键词}"，如"商品：熊猫抱抱卷"
    """
    import json
    import os
    import re
    
    # 将输入关键词转为小写
    keyword_lower = keyword.lower()
    
    # 读取品牌列表文件
    try:
        # 获取brand_list_lower.txt的路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        brand_file_path = os.path.join(current_dir, "brand_list_lower.txt")
        
        # 检查是否是品牌
        if os.path.exists(brand_file_path):
            with open(brand_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 处理包含/的情况，表示多个名称
                    if '/' in line:
                        brand_names = line.split('/')
                        for brand_name in brand_names:
                            if brand_name.strip().lower() == keyword_lower:
                                return f"品牌：{keyword}"
                    else:
                        if line.lower() == keyword_lower:
                            return f"品牌：{keyword}"
        
        # 读取类目json文件
        category_file_path = os.path.join(current_dir, "category.json")
        
        with open(category_file_path, 'r', encoding='utf-8') as f:
            category_data = json.load(f)
        
        # 遍历所有类目数据
        if category_data.get("success") and category_data.get("data"):
            for item in category_data["data"]:
                category_level = item.get("showName")
                enum_value = item.get("enumValue", "")
                
                if not enum_value:
                    continue
                
                # 解析类目值
                category_items = enum_value.split(',')
                for category_item in category_items:
                    parts = category_item.split('-')
                    if len(parts) >= 1:
                        category_name = parts[0].strip()
                        if category_name.lower() == keyword_lower:
                            return f"类目：{category_level}"
                
        # 如果没有找到匹配的类目和品牌，则认为是商品名
        return f"商品：{keyword}"
    
    except Exception as e:
        log_error(f"判断类目品牌类型时发生错误: {str(e)}")
        return f"判断失败，发生错误: {str(e)}"

