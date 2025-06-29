@echo off
chcp 65001
echo Discord Bot Manager 自动构建脚本
echo ================================

echo 正在检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误：未找到Python环境，请先安装Python 3.8+
    pause
    exit /b 1
)

echo.
echo 正在安装构建工具...
pip install pyinstaller

echo.
echo 开始构建可执行文件...
python build_exe.py

if %errorlevel% equ 0 (
    echo.
    echo ================================
    echo 构建成功完成！
    echo 可执行文件位置: dist\DiscordBotManager\
    echo ================================
    echo.
    echo 按任意键打开输出目录...
    pause >nul
    explorer dist
) else (
    echo.
    echo 构建失败，请检查错误信息
    pause
)