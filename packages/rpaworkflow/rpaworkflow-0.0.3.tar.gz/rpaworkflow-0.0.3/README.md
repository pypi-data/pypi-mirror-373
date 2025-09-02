# RPA Workflow

一个灵活、可扩展的RPA（机器人流程自动化）工作流框架，支持多种自动化工具的工作流管理和节点执行。

## 特性

- 统一的工作流管理接口
- 支持多种自动化工具：
  - Selenium
  - UIAutomator2 (Android)
  - Undetected ChromeDriver
  - Playwright
  - DrissionPage
- 可扩展的节点系统
- 内置错误处理和重试机制
- 上下文数据共享

## 安装

### 基本安装

```bash
pip install rpaworkflow
```

### 安装特定框架依赖

rpaworkflow支持多种自动化框架，您可以根据需要安装特定框架的依赖：

```bash
# 安装Selenium依赖
pip install rpaworkflow[selenium]

# 安装Playwright依赖
pip install rpaworkflow[playwright]

# 安装UIAutomator2依赖
pip install rpaworkflow[uiautomator2]

# 安装Undetected ChromeDriver依赖
pip install rpaworkflow[undetected-chromedriver]

# 安装DrissionPage依赖
pip install rpaworkflow[drissionpage]

# 安装所有框架依赖
pip install rpaworkflow[all]
```

使用uv安装：

```bash
# 安装Selenium依赖
uv pip install rpaworkflow[selenium]

# 安装所有框架依赖
uv pip install rpaworkflow[all]
```

## 快速开始

### Selenium Web 自动化示例

```python
from rpaworkflow.selenium import ConnectBrowserNode, NavigateNode, CloseBrowserNode
from rpaworkflow.manager import WorkflowManager, WorkflowStatus
from rpaworkflow.nodes import WaitTimeNode

# 创建工作流管理器
workflow = WorkflowManager(name="简单Web自动化")

# 添加节点
workflow.add_node(ConnectBrowserNode(name="连接浏览器"))
workflow.add_node(NavigateNode(name="打开网页", url="https://www.example.com"))
workflow.add_node(WaitTimeNode(name="等待加载", min_time=2))

workflow.set_finally_node(CloseBrowserNode(name='关闭浏览器'))

# 执行工作流
result = workflow.run()
print(f"工作流执行状态: {result.status}")

assert result.status == WorkflowStatus.SUCCESS
```

### Android 自动化示例

```python
from rpaworkflow.uiautomator2 import ConnectDeviceNode, ClickNode, LaunchAppNode, StopAppNode
from rpaworkflow.manager import WorkflowManager, WorkflowStatus

# 创建工作流管理器
workflow = WorkflowManager(name="Android自动化")

package_name = '...'  # 例如 'com.example.app'

# 添加节点
workflow.add_node(ConnectDeviceNode(name="连接设备"))
workflow.add_node(LaunchAppNode(name="启动APP", package_name=package_name))
workflow.add_node(ClickNode(name="点击按钮", selector={"resourceId": "com.example.app:id/button1"}))

workflow.set_finally_node(StopAppNode(name="停止APP", package_name=package_name))

# 执行工作流
result = workflow.run()

assert result.status == WorkflowStatus.SUCCESS
```

### Playwright 现代 Web 自动化示例

```python
from rpaworkflow.playwright import ConnectBrowserNode, NavigateNode, ClickNode, InputTextNode, ScreenshotNode, CloseBrowserNode
from rpaworkflow.manager import WorkflowManager, WorkflowStatus

# 创建工作流管理器
workflow = WorkflowManager(name="Playwright自动化")

# 添加节点
workflow.add_node(ConnectBrowserNode(name="连接浏览器", browser_type="chromium"))
workflow.add_node(NavigateNode(name="打开网页", url="https://www.example.com"))
workflow.add_node(ClickNode(name="点击登录按钮", selector="#login-button"))
workflow.add_node(InputTextNode(name="输入用户名", selector="#username", text="user"))
workflow.add_node(ScreenshotNode(name="截图", file_path="result.png"))

workflow.set_finally_node(CloseBrowserNode(name="关闭浏览器"))

# 执行工作流
result = workflow.run()

assert result.status == WorkflowStatus.SUCCESS
```

### DrissionPage 多功能 Web 自动化示例

```python
from rpaworkflow.drissionpage import ConnectPageNode, NavigateNode, ClickNode, InputTextNode, ScreenshotNode, QuitBrowserNode
from rpaworkflow.manager import WorkflowManager, WorkflowStatus

# 创建工作流管理器
workflow = WorkflowManager(name="DrissionPage自动化")

# 添加节点
workflow.add_node(ConnectPageNode(name="连接页面", page_type="web"))
workflow.add_node(NavigateNode(name="打开网页", url="https://www.example.com"))
workflow.add_node(ClickNode(name="点击按钮", locator="#login-button"))
workflow.add_node(InputTextNode(name="输入文本", locator="#username", text="user"))
workflow.add_node(ScreenshotNode(name="截图", filename="screenshot.png", save_path='./'))

workflow.set_finally_node(QuitBrowserNode(name="退出浏览器"))

# 执行工作流
result = workflow.run()

assert result.status == WorkflowStatus.SUCCESS
```

### Undetected ChromeDriver 反检测 Web 自动化示例

```python
import undetected_chromedriver as uc
from rpaworkflow.undetected_chromedriver import ConnectBrowserNode, NavigateNode, ClickNode, InputTextNode, CloseBrowserNode
from rpaworkflow.manager import WorkflowManager, WorkflowStatus

# 创建工作流管理器
workflow = WorkflowManager(name="Undetected Chrome自动化")

# 添加节点
workflow.add_node(ConnectBrowserNode(name="连接浏览器", headless=False, suppress_welcome=True))
workflow.add_node(NavigateNode(name="打开网页", url="https://bot.sannysoft.com"))  # 指纹检测网站
workflow.add_node(ClickNode(name="点击按钮", by=uc.By.CSS_SELECTOR, value="#some-button"))
workflow.add_node(InputTextNode(name="输入文本", by=uc.By.CSS_SELECTOR, value="#some-input", text="测试文本"))

workflow.set_finally_node(CloseBrowserNode(name="关闭浏览器"))

# 执行工作流
result = workflow.run()

assert result.status == WorkflowStatus.SUCCESS
```

## 高级用法

### 条件分支

```python
from rpaworkflow.nodes import ConditionNode

# 创建条件节点
condition_node = ConditionNode(
    name="条件判断",
    condition=lambda ctx: ctx.get("some_value") > 10,
    true_node=SomeNode(name="条件为真时执行"),
    false_node=SomeNode(name="条件为假时执行")
)

# 添加到工作流
workflow.add_node(condition_node)
```

### 逻辑组合函数

`and_` 和 `or_` 函数可以组合多个节点的条件，用于创建复杂的条件逻辑。

```python
from rpaworkflow.func import or_, and_
from rpaworkflow.nodes import CheckElementNode

# 创建检查元素节点
check_button1 = CheckElementNode(name="检查按钮1", selector="#button1")
check_button2 = CheckElementNode(name="检查按钮2", selector="#button2")
check_button3 = CheckElementNode(name="检查按钮3", selector="#button3")

# 使用 or_ 函数：前面节点若正常运行, 则不执行下一个节点, 否则执行下一个节点
or_node = or_(check_button1, check_button2)
workflow.add_node(or_node)

# 使用 and_ 函数：前一个节点异常, 不执行下一个节点, 否则执行下一个节点
and_node = and_(check_button1, check_button2, check_button3)
workflow.add_node(and_node)

# 组合使用
complex_condition = or_(check_button1, and_(check_button2, check_button3))
workflow.add_node(complex_condition)
```

### 循环节点

```python
from rpaworkflow.nodes import LoopNode, LambdaActionNode

# 创建一个计数器节点
increment_counter = LambdaActionNode(
    name="增加计数器",
    action=lambda ctx: ctx.set("counter", ctx.get("counter", 0) + 1)
)

# 创建循环节点
loop_node = LoopNode(
    name="循环执行",
    loop_condition=lambda ctx: ctx.get("counter", 0) < 5,  # 循环条件：计数器小于5
    loop_node=increment_counter  # 循环执行的节点
)

# 初始化计数器
workflow.add_node(LambdaActionNode(
    name="初始化计数器",
    action=lambda ctx: ctx.set("counter", 0)
))

# 添加循环节点
workflow.add_node(loop_node)
```

### 空节点和错误节点

```python
from rpaworkflow.nodes import EmptyNode, ErrorNode, ErrorStorageNode

# 空节点 - 不执行任何操作，可用作占位符
workflow.add_node(EmptyNode(name="空操作"))

# 错误节点 - 抛出异常
workflow.add_node(ErrorNode(
    name="抛出错误",
    error="自定义错误信息"  # 也可以传入Exception对象
))

# 错误存储节点 - 抛出异常并存储到上下文
workflow.add_node(ErrorStorageNode(
    name="存储错误",
    error="自定义错误信息",
    output_key="error_info"  # 错误信息将存储在上下文的这个键下
))
```

## 贡献

欢迎贡献代码、报告问题或提出改进建议！

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。
