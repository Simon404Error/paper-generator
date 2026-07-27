@echo off
chcp 65001 >nul
title 试卷生成器

echo.
echo   ╔══════════════════════════╗
echo   ║   试 卷 生 成 器       ║
echo   ║   智能题库 · Python版  ║
echo   ╚══════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Install Flask if needed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装 Flask...
    pip install flask -q
    if errorlevel 1 (
        echo [错误] Flask 安装失败，请手动执行: pip install flask
        pause
        exit /b 1
    )
)

:: Start server
echo [启动] 正在启动服务器...
echo [地址] http://localhost:5000
echo.
echo 按 Ctrl+C 停止服务器
echo.

start "" http://localhost:5000
python app.py
pause
