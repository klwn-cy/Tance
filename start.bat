@echo off
chcp 65001 >nul
echo ========================================
echo    碳策通智能体分析服务 - 启动脚本
echo ========================================
echo.

:: 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python环境，请先安装Python
    pause
    exit /b 1
)

:: 检查API Key
if "%DASHSCOPE_API_KEY%"=="" (
    echo [警告] 未设置DASHSCOPE_API_KEY环境变量
    echo 请设置: set DASHSCOPE_API_KEY=your_api_key
    echo.
)

:: 切换到项目目录
cd /d "%~dp0"

echo [启动] 正在启动应用...
echo ========================================
echo.
echo 访问 http://localhost:7899
echo.

python -m uvicorn api_server:app --host 0.0.0.0 --port 7899 --reload

pause
