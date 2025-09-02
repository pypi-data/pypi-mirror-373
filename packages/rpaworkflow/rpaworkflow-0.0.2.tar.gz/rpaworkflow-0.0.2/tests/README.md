# RPA 工作流框架测试套件

本目录包含 RPA 工作流框架的完整测试套件，旨在确保框架的稳定性和可靠性，并提供 100% 的测试覆盖率。

## 测试结构

测试套件按照框架的主要组件进行组织：

- `test_context.py` - 测试上下文管理功能
- `test_node.py` - 测试节点基类和数据存储节点
- `test_condition.py` - 测试条件节点
- `test_loop.py` - 测试循环节点
- `test_error.py` - 测试错误处理节点
- `test_manager.py` - 测试工作流管理器
- `test_exception.py` - 测试异常类

## 运行测试

### 安装测试依赖

首先，确保安装了必要的测试依赖：

```bash
pip install pytest pytest-cov
```

### 运行所有测试

在项目根目录下运行以下命令：

```bash
pytest
```

这将运行所有测试并生成覆盖率报告。

### 运行特定测试文件

```bash
pytest tests/test_node.py
```

### 运行特定测试用例

```bash
pytest tests/test_node.py::test_node_initialization
```

## 测试覆盖率

测试套件配置为生成详细的覆盖率报告，包括：

- 终端输出报告
- HTML 报告（在 `htmlcov` 目录）
- XML 报告（用于 CI 集成）

### 查看 HTML 覆盖率报告

运行测试后，可以打开 `htmlcov/index.html` 文件查看详细的覆盖率报告：

```bash
# 在 Windows 上
start htmlcov/index.html

# 在 macOS 上
open htmlcov/index.html

# 在 Linux 上
xdg-open htmlcov/index.html
```

## 测试覆盖率要求

本测试套件要求 100% 的测试覆盖率。如果测试覆盖率低于 100%，测试将被视为失败。

## 添加新测试

添加新功能时，请确保：

1. 为新功能创建相应的测试用例
2. 测试覆盖所有代码路径，包括正常路径和错误路径
3. 测试边界条件和异常情况
4. 维持 100% 的测试覆盖率

## 测试最佳实践

- 每个测试函数应该只测试一个功能点
- 使用描述性的测试函数名称
- 在测试函数的文档字符串中清晰描述测试目的
- 使用 `assert` 语句验证预期结果
- 避免测试之间的依赖关系