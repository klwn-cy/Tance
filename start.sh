#!/bin/bash
echo "========================================"
echo "   碳策通智能体分析服务 - 启动脚本"
echo "========================================"
echo ""
# 切换到脚本所在目录
cd "$(dirname "$0")"

# ------------------ 新增：仅读取 .env 文件 ------------------
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi
# -------------------------------------------------------------

# 检查Python环境（已修正为 python3）
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python环境，请先安装Python"
    exit 1
fi
# 检查API Key
if [ -z "$DASHSCOPE_API_KEY" ]; then
    echo "[警告] 未设置DASHSCOPE_API_KEY环境变量"
    echo "请设置: export DASHSCOPE_API_KEY=your_api_key"
    echo ""
fi
# 检查依赖（已修正为 pip3）
echo "[检查] 正在检查依赖..."
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "[安装] 正在安装依赖..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败"
        exit 1
    fi
fi
echo "[完成] 依赖检查通过"
echo ""
echo "[启动] 正在启动应用..."
echo "========================================"
echo ""
echo "访问 http://localhost:7899"
echo ""
python3 -m uvicorn api_server:app --host 0.0.0.0 --port 7899 --reload