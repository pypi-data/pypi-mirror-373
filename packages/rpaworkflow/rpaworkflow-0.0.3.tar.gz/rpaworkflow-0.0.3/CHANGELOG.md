# 更新日志

所有对 rpaworkflow 包的显著更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.0.1]

### 新增

- 初始版本发布
- 工作流管理器核心功能
- 基本节点系统
- 支持多种自动化工具：
  - Selenium
  - UIAutomator2
  - Undetected ChromeDriver
  - Playwright
  - DrissionPage
- 上下文数据共享机制
- 错误处理和重试机制

- 添加可选依赖功能，支持按需安装特定框架依赖
  - `pip install rpaworkflow[selenium]` - 安装Selenium依赖
  - `pip install rpaworkflow[playwright]` - 安装Playwright依赖
  - `pip install rpaworkflow[uiautomator2]` - 安装UIAutomator2依赖
  - `pip install rpaworkflow[undetected-chromedriver]` - 安装Undetected ChromeDriver依赖
  - `pip install rpaworkflow[drissionpage]` - 安装DrissionPage依赖
  - `pip install rpaworkflow[all]` - 安装所有框架依赖
