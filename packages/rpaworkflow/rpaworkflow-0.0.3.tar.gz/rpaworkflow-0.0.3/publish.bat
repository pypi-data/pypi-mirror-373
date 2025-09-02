@echo off
echo 正在构建 rpaworkflow 包...

:: 清理旧的构建文件
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist rpaworkflow.egg-info rmdir /s /q rpaworkflow.egg-info

:: 构建包
python -m build

echo.
echo 构建完成！生成的文件在 dist 目录下。
echo.

set /p CHOICE=是否要上传到 PyPI？(y/n): 

if /i "%CHOICE%"=="y" (
    echo.
    echo 正在上传到 PyPI...
    twine upload dist/*
    echo.
    echo 上传完成！
) else (
    echo.
    echo 已取消上传。
)

echo.
echo 按任意键退出...
pause > nul