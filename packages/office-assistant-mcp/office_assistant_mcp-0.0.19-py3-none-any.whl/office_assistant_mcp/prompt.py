"""
提示词模块，用于存放各种提示词模板
"""

def get_planning_customer_group_prompt(user_query: str) -> str:
    """
    获取创建客群规划的提示词模板
    
    Args:
        user_query: 用户输入的创建客群的原样指令
    
    Returns:
        填充后的提示词
    """
    return f"""## 任务：新建客群参数检查与规划

## 指令：
分析 用户的输入的指令，检查创建客群所需信息：
1. 客群名称
2. 业务类型（活动运营、用户运营等）
3. 客群定义 (用户行为描述 或 用户身份类型，至少一项)

- 如果缺少信息，根据用户语义自动为其补充，客群名称可以使用用户提到的产品名，业务类型默认"活动运营"。
- 如果信息完整，直接返回下方创建客群规划的操作步骤。

## 创建客群规划的操作步骤：

1. 调用 `open_create_customer_group_page`打开客群新建页面。
2. 调用 `fill_customer_group_info` (含客群名称, 业务类型默认为"活动运营")。
3. 如指定了用户身份，调用 `fill_customer_group_user_tag_set_basic_info`。
4. 处理用户行为标签前，对维度相关的名词描述，用户如果没有明确指定属于哪一级类目或品牌、或商品名，则调用`judge_category_brand_or_product`工具先去判断指令里的专业名词是类目、品牌、还是商品，再创建行为标签，比如用户提到牛奶，也需要调用工具去判断是类目还是商品名。
5. 处理用户行为标签时，按以下规则进行：
    a. 点击添加按钮：
    - 使用 `fill_customer_click_add_behavior_tag_button(tag_position)` 点击添加按钮，增加一个行为标签：
        - `"left"`：当前标签与前一个标签为并列关系（无嵌套）。
        - `"right"`：当前标签是前一个标签的子标签，仅在逻辑结构中**明确存在括号嵌套时使用**，会把前一个标签从一级标签变为二级标签，然后两个标签变成同一级标签。

    **根据”且“、”或“关系拆分多个标签。嵌套的唯一判定标准是逻辑结构中是否有括号嵌套**
    
    b. 填写标签内容：
    - 先点击完全部添加按钮，再依次调用 `fill_customer_fill_behavior_tag_form` 填写标签内容。
    - 假设有3个标签，则先调用3次 `fill_customer_click_add_behavior_tag_button`，再依次调用3次 `fill_customer_fill_behavior_tag_form`。
    
    c. 根据需要，把“且”关系改为“或”关系：
    - 所有标签之间默认逻辑为“且”。仅当用户输入中某组标签应为“或”时，才调用 `fill_customer_toggle_behavior_tag_relation_to_or(relation_position)`

    relation_position 编号规则如下：
    - 编号从 `0` 开始，从最外层到内层，从上到下依次编号。
    - 同一个层级嵌套的一组条件只有1个编号。

    判断标准总结：
    -  默认关系就是“且”，不需要改，**不调用 toggle**
    -  结构中出现了应为“或”的组合，**才调用 toggle**
    -  多个“或”块编号顺序是：外层“或” → 第一个嵌套“或” → 第二个嵌套“或”，不是按出现顺序统一编号。
    -  relation_position编号示例,[]中的数字为编号:
        - `A 或 B 或 C`：有1个共用编号：0
        - `(A 或 B) 且 (C 或 D)`：有3个编号：(A [1] B) [0] (C [2] D)
        - `A 或 (B 且 C 且 D)`：有2个编号：A [0] (B [1] C [1] D)

    d. 行为标签调用示例：
    - `A 或 B 或 C`：
        - 添加三次 `"left"`
        - 调用一次 `fill_customer_toggle_behavior_tag_relation_to_or(0)`，用于 A、B、C 的“且”变”或“

    - `(A 或 B) 且 (C 或 D)`：
        - A（left）、B（right）、C（left）、D（right），(A 或 B)变成二级标签，(C 或 D)变成二级标签，最外侧层的“且”relation_position编号为0，是一级标签。
        - 调用 `fill_customer_toggle_behavior_tag_relation_to_or(1)` 修改 A 与 B 为“或”，下标relation_position=0是第一层级最外层的(A 或 B)与(C 或 D)的“且”。
        - 调用 `fill_customer_toggle_behavior_tag_relation_to_or(2)` 修改 C 与 D 为“或”。
    
    - `A 或 (B 且 C)`：
        - A（left）、B（left）、C（right）
        - B 与 C 之间默认是“且”，不需要 toggle
        - 调用一次 `fill_customer_toggle_behavior_tag_relation_to_or(0)`，用于 A 与 (B 且 C) 的“且”变”或“，即第一层级最外层的那个“且”。
    
6. 成功填写全部表单后，调用 `estimate_customer_group_size` 预估客群人数，填写表单失败则不执行客群人数预估。
7. 如果页面如需登录，调用 `login_sso`去登录。
8. 完成客群创建后，提醒用户："已完成客群创建表单填写，请人工检查客群信息，再点击\"提交\"执行计划！"。
9. 注意：使用中文回复，步骤需按顺序一步一步执行，不能并发执行；有多个标签需要创建时，先执行完所有的添加按钮点击事件，再依次填写标签表单，否则会造成UI异常。（该提示也作为结果返回）

## 用户的输入
{user_query}

## 返回结果：
"""


def get_planning_message_plan_prompt(user_query: str) -> str:
    """
    获取创建短信计划规划的提示词模板
    
    Args:
        user_query: 用户输入的创建短信计划的原样指令
    
    Returns:
        填充后的提示词
    """
    return f"""## 任务：新建短信发送计划参数检查与规划

## 指令：
分析用户输入的指令，检查创建短信计划所需的以下必要信息是否齐全：
1. 客群ID
2. 发送时间
3. 商品ID，或者指定的日期二选一（包括今天、明天等表示日期的字符串）（如果指令中提到了日期，则用户指令中可以不提供商品ID，根据日期调用`read_item_id_by_date`等飞书表格工具，从飞书表格中查询具体的商品ID）

- 如果缺少必填信息，直接返回缺少的信息点。
- 如果信息完整，直接返回下方创建短信计划规划的操作步骤。

## 规划的操作步骤：
1. 如果没有`商品ID`，但有指定日期，则根据日期调用`read_item_id_by_date`、`read_item_name_by_date`、`read_item_price_by_date`等飞书表格工具，从飞书表格中查询具体的商品ID等商品信息。
2. 如果用户没有提供具体的`短信内容`，则调用 `generate_item_sms_content`工具根据商品信息生成短信内容。
3. 调用 `open_create_customer_group_page` 打开短信计划页面。
4. 调用 `fill_message_group_id` 搜索并选择指定客群。
5. 调用 `fill_message_plan_info` 设置计划名称和发送时间。
6. 调用 `fill_message_content` 设置短信内容和商品链接。
7. 调用 `set_department_info` 设置默认的费用归属部门。
8. 如页面需要登录，调用 `login_sso` 去登录。
9. 注意：使用中文回复，步骤需按顺序一步一步执行，不能并发执行。（该提示也作为结果返回）

## 用户的输入指令
{user_query}

## 返回结果：
""" 