@echo off
chcp 65001 >nul
echo ========================================
echo    环境配置助手
echo ========================================
echo.

echo 请输入您的通义千问API Key:
echo (可在 https://dashscope.console.aliyun.com/ 获取)
echo.
set /p API_KEY="API Key: "

:: 永久设置用户环境变量
setx DASHSCOPE_API_KEY "%API_KEY%" >nul

echo.
echo [完成] API Key 已保存到系统环境变量
echo 请重新打开命令行窗口使环境变量生效
echo.
pause
