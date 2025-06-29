@echo off
chcp 65001
echo Discord Bot Manager - 开发环境启动
echo ================================

echo 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误：未找到Python环境
    echo 请先安装Python 3.8+
    pause
    exit /b 1
)

echo.
echo 检查依赖包...
python -c "import PyQt6" 2>nul
if %errorlevel% neq 0 (
    echo 正在安装GUI依赖...
    pip install -r requirements_gui.txt
    if %errorlevel% neq 0 (
        echo 依赖安装失败
        pause
        exit /b 1
    )
)

echo.
echo 启动GUI界面...
python start_gui.py

if %errorlevel% neq 0 (
    echo.
    echo 程序异常退出
    pause
)