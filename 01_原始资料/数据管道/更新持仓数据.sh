#!/bin/bash
# market_data_update.sh
# 更新持仓股市场数据

DATA_DIR="/Users/humiles/莫大韭菜/02_市场数据/历史数据"
LOG_DIR="/Users/humiles/莫大韭菜/05_数据管道/logs"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

mkdir -p "$LOG_DIR"

echo "=== 市场数据更新 ===" 
echo "时间: $TIMESTAMP"
echo ""

# 持仓股列表
STOCKS=(
    "000762:西藏矿业"
    "600343:航天动力"
    "002594:比亚迪"
    "002169:智光电气"
    "688114:华大智造"
    "601020:华钰矿业"
    "002538:司尔特"
    "688559:海目星"
    "300034:钢研高纳"
    "688533:上大股份"
)

# 检查是否有python3
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要 python3 来运行数据更新"
    echo "使用 Homebrew 安装: brew install python3"
    exit 1
fi

# 检查 akshare
if ! python3 -c "import akshare" &> /dev/null; then
    echo "安装 akshare..."
    pip3 install akshare --quiet
fi

# 尝试更新数据
echo "尝试更新数据..."

python3 << 'PYTHON_SCRIPT'
import akshare
import os
from datetime import datetime

DATA_DIR = "/Users/humiles/莫大韭菜/02_市场数据/历史数据"
LOG_FILE = f"/Users/humiles/莫大韭菜/05_数据管道/logs/update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

STOCKS = {
    "000762": "西藏矿业",
    "600343": "航天动力", 
    "002594": "比亚迪",
    "002169": "智光电气",
    "688114": "华大智造",
    "601020": "华钰矿业",
    "002538": "司尔特",
    "688559": "海目星",
    "300034": "钢研高纳",
    "688533":上大股份",
}

def update_stock(code, name):
    try:
        # 判断市场
        if code.startswith("6"):
            symbol = f"sh{code}"
        else:
            symbol = f"sz{code}"
        
        # 获取今日数据
        today = datetime.now().strftime('%Y%m%d')
        
        df = akshare.stock_zh_a_hist(symbol=symbol, period="daily", start_date=today, end_date=today, adjust="qfq")
        
        if df is not None and len(df) > 0:
            # 追加到CSV
            csv_file = f"{DATA_DIR}/{code}.csv"
            df.tail(1).to_csv(csv_file, mode='a', header=False, index=False)
            print(f"✅ {name}({code}): {df.iloc[-1]['收盘']}")
            return True
        else:
            print(f"⏸️ {name}({code}): 今日无新数据")
            return False
            
    except Exception as e:
        print(f"❌ {name}({code}): {str(e)[:50]}")
        return False

print("开始更新持仓股数据...")
print("-" * 40)

success = 0
failed = 0

for code, name in STOCKS.items():
    if update_stock(code, name):
        success += 1
    else:
        failed += 1

print("-" * 40)
print(f"完成: ✅ {success} ⏸️ {failed}")

PYTHON_SCRIPT

echo ""
echo "=== 更新完成 ==="
