#!/usr/bin/env python3
"""
Phase VI 验证校准 - 历史案例回测
验证莫大韭菜投资框架的准确性
"""

import csv
import os
from datetime import datetime

# 持仓股列表
STOCKS = {
    "000762": {"Name": "西藏矿业", "Position": "锂矿"},
    "600343": {"Name": "航天动力", "Position": "商业航天"},
    "002594": {"Name": "比亚迪", "Position": "新能源车"},
    "002169": {"Name": "智光电气", "Position": "储能"},
    "688114": {"Name": "华大智造", "Position": "AI医疗"},
    "601020": {"Name": "华钰矿业", "Position": "锑矿"},
    "002538": {"Name": "司尔特", "Position": "磷矿"},
    "688559": {"Name": "海目星", "Position": "激光设备"},
    "300034": {"Name": "钢研高纳", "Position": "高温合金"},
}

DATA_DIR = "/Users/humiles/莫大韭菜/02_市场数据/历史数据"

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
    """计算移动平均"""
    if len(data) < days:
        return None
    return sum(d['close'] for d in data[-days:]) / days

def check_breakout(data, lookback=20):
    """检查是否突破"""
    if len(data) < lookback:
        return None, None
    
    recent = data[-lookback:]
    highs = [d['high'] for d in recent]
    lows = [d['low'] for d in recent]
    
    resistance = max(highs)
    support = min(lows)
    
    latest = data[-1]['close']
    
    if latest > resistance * 0.98:  # 接近前期高点
        return "突破", resistance
    elif latest < support * 1.02:  # 接近前期低点
        return "破位", support
    else:
        return "盘整", None

def analyze_at_date(data, target_date, lookahead=30):
    """
    模拟在某一天的分析判断
    然后跟踪未来N天的走势
    """
    # 找到目标日期的数据
    target_idx = None
    for i, d in enumerate(data):
        if d['date'] == target_date:
            target_idx = i
            break
    
    if target_idx is None:
        return None
    
    # 获取分析时的数据
    analysis_data = data[:target_idx+1]
    if len(analysis_data) < 60:
        return None
    
    latest = analysis_data[-1]
    ma5 = calc_ma(analysis_data, 5)
    ma20 = calc_ma(analysis_data, 20)
    ma60 = calc_ma(analysis_data, 60)
    
    # 判断走势
    if latest['close'] > ma5:
        trend = "强势"
    elif latest['close'] > ma20:
        trend = "盘整"
    else:
        trend = "弱势"
    
    # 检查突破/破位
    breakout, level = check_breakout(analysis_data)
    
    # 跟踪未来走势
    future_data = data[target_idx+1:target_idx+1+lookahead]
    if future_data:
        entry_price = latest['close']
        max_price = max(d['high'] for d in future_data)
        min_price = min(d['low'] for d in future_data)
        final_price = future_data[-1]['close']
        
        future_return = (final_price / entry_price - 1) * 100
        max_upside = (max_price / entry_price - 1) * 100
        max_downside = (min_price / entry_price - 1) * 100
    else:
        future_return = max_upside = max_downside = 0
    
    return {
        'date': target_date,
        'price': latest['close'],
        'trend': trend,
        'breakout': breakout,
        'ma5': ma5,
        'ma20': ma20,
        'ma60': ma60,
        'future_return': future_return,
        'max_upside': max_upside,
        'max_downside': max_downside,
    }

def run_backtest():
    """运行回测"""
    print("=" * 70)
    print("Phase VI 验证校准 - 莫大韭菜投资框架回测")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    # 定义测试案例
    test_cases = [
        # (股票代码, 日期, 预期判断, 说明)
        ("002594", "2020-01-02", "强势突破", "新能源行情启动"),
        ("002594", "2021-02-10", "高位警戒", "比亚迪创历史新高后"),
        ("601020", "2022-04-27", "困境反转", "ST后低位，锑矿逻辑"),
        ("600343", "2025-01-02", "商业航天启动", "航天板块开始启动"),
        ("000762", "2021-09-01", "锂矿高位", "锂价历史高点附近"),
        ("688559", "2024-01-02", "AI行情启动", "海目星AI激光设备"),
    ]
    
    results = []
    
    for code, date, expected, description in test_cases:
        stock = STOCKS.get(code, {"Name": code})
        data = read_stock_data(code)
        
        if not data:
            print(f"\n⚠️ {stock['Name']}({code}): 无数据")
            continue
        
        result = analyze_at_date(data, date)
        
        if not result:
            print(f"\n⚠️ {stock['Name']}({code}) @ {date}: 日期数据不存在")
            continue
        
        # 判断是否正确
        if "强势" in result['trend'] and "突破" in expected:
            correctness = "✓ 正确"
        elif "弱势" in result['trend'] and "高位" in expected:
            correctness = "✓ 正确"
        elif "突破" in expected and result['breakout'] == "突破":
            correctness = "✓ 正确"
        else:
            correctness = "○ 待验证"
        
        results.append({
            'stock': stock['Name'],
            'date': date,
            'expected': expected,
            'result': result,
            'correctness': correctness,
            'description': description,
        })
        
        print(f"""
{'='*60}
【{stock['Name']} {code}】
日期: {date}
说明: {description}
{'='*60}
当时价格: {result['price']:.2f}
走势判断: {result['trend']}
均线状态:
  MA5:  {result['ma5']:.2f} {'✓' if result['price'] > result['ma5'] else '✗'}
  MA20: {result['ma20']:.2f} {'✓' if result['price'] > result['ma20'] else '✗'}
  MA60: {result['ma60']:.2f} {'✓' if result['price'] > result['ma60'] else '✗'}
突破/破位: {result['breakout']} ({result['ma5']:.2f})

30天后结果:
  最高涨幅: {result['max_upside']:+.1f}%
  最大跌幅: {result['max_downside']:+.1f}%
  最终涨跌: {result['future_return']:+.1f}%

预期判断: {expected}
实际结果: {result['trend']} + {result['breakout']}
验证: {correctness}
""")
    
    # 统计
    print("\n" + "=" * 70)
    print("回测统计")
    print("=" * 70)
    
    correct = sum(1 for r in results if "正确" in r['correctness'])
    total = len(results)
    
    print(f"测试案例: {total}")
    print(f"正确: {correct}")
    print(f"准确率: {correct/total*100:.1f}%" if total > 0 else "N/A")
    
    # 统计各走势的收益
    strong = [r for r in results if "强势" in r['result']['trend']]
    weak = [r for r in results if "弱势" in r['result']['trend']]
    
    if strong:
        avg_return = sum(r['result']['future_return'] for r in strong) / len(strong)
        print(f"\n强势股30天平均收益: {avg_return:+.1f}%")
    
    if weak:
        avg_return = sum(r['result']['future_return'] for r in weak) / len(weak)
        print(f"弱势股30天平均收益: {avg_return:+.1f}%")
    
    return results

if __name__ == "__main__":
    results = run_backtest()
