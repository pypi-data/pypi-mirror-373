# 发布指南

本文档提供了如何构建和发布 rpaworkflow 包到 PyPI 的步骤。

## 准备工作

1. 确保你已经安装了必要的工具：

```bash
uv pip install build twine
```

2. 确保你有 PyPI 账号，并且已经在 PyPI 上注册了项目名称。

## 构建包

在项目根目录下运行以下命令构建包：

```bash
python -m build
```

这将在 `dist/` 目录下创建源代码分发包（.tar.gz）和轮子分发包（.whl）。

## 测试发布到 TestPyPI

在正式发布前，建议先发布到 TestPyPI 进行测试：

```bash
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

然后可以通过以下命令安装测试版本：

```bash
uv pip install --index-url https://test.pypi.org/simple/ rpaworkflow
```

## 正式发布到 PyPI

确认测试无误后，可以正式发布到 PyPI：

```bash
twine upload dist/*
```

## 版本更新

1. 在 `pyproject.toml` 文件中更新版本号
2. 更新 CHANGELOG.md（如果有）
3. 提交更改到版本控制系统
4. 创建版本标签
5. 按照上述步骤重新构建和发布

## 自动化发布（可选）

你可以使用 GitHub Actions 自动化发布流程。创建 `.github/workflows/publish.yml` 文件，配置在标签推送时自动构建和发布包。

## 可选依赖管理

rpaworkflow 包使用了可选依赖功能，允许用户根据需要安装特定框架的依赖。这些配置在 `pyproject.toml` 文件的 `[project.optional-dependencies]` 部分：

```toml
[project.optional-dependencies]
selenium = [
    "selenium>=4.0.0",
]
playwright = [
    "playwright>=1.20.0",
]
# 其他框架...
all = [
    # 包含所有框架的依赖
]
```

当更新依赖版本或添加新的框架支持时，请确保：

1. 更新对应框架的依赖版本要求
2. 同时更新 `all` 选项中的依赖列表
3. 在 README.md 中更新安装说明

## 注意事项

- 发布前确保所有测试通过
- 确保文档已更新
- 检查依赖项是否正确声明，包括可选依赖
- 确保许可证信息正确
- 测试各个可选依赖的安装和功能