@echo off
chcp 65001 >nul
echo ========================================
echo    加载知识库到向量数据库
echo ========================================
echo.

cd /d "%~dp0"

echo [执行] 正在加载知识库...
python -c "from rag.vector_store import VectorStoreService; VectorStoreService().load_document(); print('[完成] 知识库加载完成')"

echo.
pause
