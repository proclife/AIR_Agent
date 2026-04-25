#!/usr/bin/env python3
"""
市场数据查询工具
基于莫大韭菜持仓股，快速获取和分析市场数据
"""

import csv
import os
from datetime import datetime, timedelta

# 持仓股列表
STOCKS = {
    "000762": {"name": "西藏矿业", "market": "sz", "position": "锂矿"},
    "600343": {"name": "航天动力", "market": "sh", "position": "商业航天"},
    "002594": {"name": "比亚迪", "market": "sz", "position": "新能源车"},
    "002169": {"name": "智光电气", "market": "sz", "position": "储能"},
    "688114": {"name": "华大智造", "market": "sh", "position": "AI医疗"},
    "601020": {"name": "华钰矿业", "market": "sh", "position": "锑矿"},
    "002538": {"name": "司尔特", "market": "sz", "position": "磷矿"},
    "688559": {"name": "海目星", "market": "sh", "position": "激光设备"},
    "300034": {"name": "钢研高纳", "market": "sz", "position": "高温合金"},
    "688533": {"name": "上大股份", "market": "sh", "position": "高温合金"},
}

DATA_DIR = "/Users/humiles/莫大韭菜/02_市场数据/K线数据/A股"

def read_stock_data(code):
    """读取股票历史数据"""
    csv_file = f"{DATA_DIR}/{code}.csv"
    if not os.path.exists(csv_file):
        return None
    
    data = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                data.append({
                    'date': row['date'],
                    'close': float(row['close']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'volume': float(row['volume']),
                    'pctChg': float(row['pctChg']) if row.get('pctChg') else 0,
                })
            except (ValueError, KeyError):
                continue
    return data

def calc_ma(data, days):
    """计算简单移动平均线"""
    if len(data) < days:
        return None
    return sum(d['close'] for d in data[-days:]) / days

def analyze_stock(code):
    """分析单只股票"""
    stock_info = STOCKS.get(code, {"name": code, "position": ""})
    name = stock_info["name"]
    position = stock_info["position"]
    
    data = read_stock_data(code)
    if not data:
        return f"❌ {name}({code}): 无数据"
    
    # 最新数据
    latest = data[-1]
    prev = data[-2] if len(data) > 1 else latest
    
    # 计算均线
    ma5 = calc_ma(data, 5)
    ma10 = calc_ma(data, 10)
    ma20 = calc_ma(data, 20)
    ma60 = calc_ma(data, 60)
    
    # 判断走势
    if latest['close'] > ma5:
        trend = "🟢 五日线上"
    elif latest['close'] > ma10:
        trend = "🟡 十日线附近"
    else:
        trend = "🔴 五日线下"
    
    # 计算近期涨跌
    pct_5d = (latest['close'] / data[-6]['close'] - 1) * 100 if len(data) >= 6 else 0
    
    result = f"""
【{name} {code}】
板块: {position}
日期: {latest['date']}
现价: {latest['close']:.2f}
涨跌幅: {latest['pctChg']:+.2f}%
今日: 高{latest['high']:.2f} 低{latest['low']:.2f}
5日涨跌: {pct_5d:+.2f}%

均线:
  MA5:  {ma5:.2f} {'✓' if latest['close'] > ma5 else '✗'}
  MA10: {ma10:.2f} {'✓' if latest['close'] > ma10 else '✗'}
  MA20: {ma20:.2f} {'✓' if latest['close'] > ma20 else '✗'}
  MA60: {ma60:.2f} {'✓' if latest['close'] > ma60 else '✗'}

走势: {trend}
"""
    return result

def analyze_all():
    """分析所有持仓股"""
    print("=" * 60)
    print(f"持仓股分析 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    for code in STOCKS:
        print(analyze_stock(code))
    
    print("=" * 60)
    print("说明: ✓=价格在均线上  ✗=价格在均线下方")
    print("      🟢强势 🟡盘整 🔴弱势")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 分析指定股票
        code = sys.argv[1]
        print(analyze_stock(code))
    else:
        # 分析所有持仓股
        analyze_all()
