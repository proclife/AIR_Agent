#!/usr/bin/env python3
"""
每日市场简报生成器
基于莫大韭菜投资框架，分析持仓股和关注板块
"""

import csv
import os
from datetime import datetime

# 持仓股列表
STOCKS = {
    "000762": {"Name": "西藏矿业", "Position": "锂矿", "Weight": 16.4},
    "600343": {"Name": "航天动力", "Position": "商业航天", "Weight": 15.8},
    "002594": {"Name": "比亚迪", "Position": "新能源车", "Weight": 15.5},
    "002169": {"Name": "智光电气", "Position": "储能", "Weight": 14.0},
    "688114": {"Name": "华大智造", "Position": "AI医疗", "Weight": 12.6},
    "601020": {"Name": "华钰矿业", "Position": "锑矿", "Weight": 6.7},
    "002538": {"Name": "司尔特", "Position": "磷矿", "Weight": 6.4},
    "688559": {"Name": "海目星", "Position": "激光设备", "Weight": 0},
    "300034": {"Name": "钢研高纳", "Position": "高温合金", "Weight": 0},
}

DATA_DIR = "/Users/humiles/莫大韭菜/02_市场数据/历史数据"
REPORT_DIR = "/Users/humiles/莫大韭菜/05_数据管道/每日简报"

os.makedirs(REPORT_DIR, exist_ok=True)

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

def analyze_stock(code):
    """分析单只股票"""
    stock = STOCKS.get(code, {"Name": code, "Position": "", "Weight": 0})
    
    data = read_stock_data(code)
    if not data:
        return None
    
    latest = data[-1]
    ma5 = calc_ma(data, 5)
    ma10 = calc_ma(data, 10)
    ma20 = calc_ma(data, 20)
    
    # 判断走势
    if latest['close'] > ma5:
        trend = "强势"
        signal = "🟢"
    elif latest['close'] > ma10:
        trend = "盘整"
        signal = "🟡"
    else:
        trend = "弱势"
        signal = "🔴"
    
    # 5日涨跌
    pct_5d = (latest['close'] / data[-6]['close'] - 1) * 100 if len(data) >= 6 else 0
    
    return {
        'code': code,
        'name': stock['Name'],
        'position': stock['Position'],
        'weight': stock['Weight'],
        'date': latest['date'],
        'close': latest['close'],
        'pct': latest['pctChg'],
        'high': latest['high'],
        'low': latest['low'],
        'ma5': ma5,
        'ma10': ma10,
        'ma20': ma20,
        'trend': trend,
        'signal': signal,
        'pct_5d': pct_5d,
    }

def generate_report():
    """生成每日简报"""
    today = datetime.now().strftime('%Y-%m-%d')
    report_file = f"{REPORT_DIR}/简报_{today}.md"
    
    # 分析所有持仓股
    results = []
    for code in STOCKS:
        result = analyze_stock(code)
        if result:
            results.append(result)
    
    # 分类
    strong = [r for r in results if r['trend'] == '强势']
    weak = [r for r in results if r['trend'] == '弱势']
    others = [r for r in results if r['trend'] == '盘整']
    
    # 计算整体表现
    total_pct = sum(r['pct'] * r['weight'] / 100 for r in results if r['weight'] > 0)
    
    # 生成报告
    report = f"""# 【每日市场简报】{today}

> 生成时间: {datetime.now().strftime('%H:%M')}

---

## 📊 持仓股表现

### 强势股 ({len(strong)}只) 🟢

| 股票 | 现价 | 涨跌 | 5日涨跌 | MA5 | 走势 |
|------|------|------|---------|-----|------|
"""
    for r in strong:
        ma5_status = "✓" if r['close'] > r['ma5'] else "✗"
        report += f"| {r['name']} | {r['close']:.2f} | {r['pct']:+.2f}% | {r['pct_5d']:+.1f}% | {r['ma5']:.2f}{ma5_status} | {r['signal']}{r['trend']} |\n"

    report += f"""
### 弱势股 ({len(weak)}只) 🔴

| 股票 | 现价 | 涨跌 | 5日涨跌 | MA5 | 走势 |
|------|------|------|---------|-----|------|
"""
    for r in weak:
        ma5_status = "✓" if r['close'] > r['ma5'] else "✗"
        report += f"| {r['name']} | {r['close']:.2f} | {r['pct']:+.2f}% | {r['pct_5d']:+.1f}% | {r['ma5']:.2f}{ma5_status} | {r['signal']}{r['trend']} |\n"

    if others:
        report += f"""
### 盘整股 ({len(others)}只) 🟡

| 股票 | 现价 | 涨跌 | 5日涨跌 | MA5 | 走势 |
|------|------|------|---------|-----|------|
"""
        for r in others:
            ma5_status = "✓" if r['close'] > r['ma5'] else "✗"
            report += f"| {r['name']} | {r['close']:.2f} | {r['pct']:+.2f}% | {r['pct_5d']:+.1f}% | {r['ma5']:.2f}{ma5_status} | {r['signal']}{r['trend']} |\n"

    report += f"""
---

## 📈 整体评估

**持仓加权涨跌: {total_pct:+.2f}%**

### 走势分布
- 🟢 强势: {len(strong)}只
- 🟡 盘整: {len(others)}只
- 🔴 弱势: {len(weak)}只

---

## 🎯 操作建议

"""

    # 弱势股分析
    if weak:
        report += "### 需要关注 🔴\n\n"
        for r in weak:
            if r['pct_5d'] < -5:
                report += f"- **{r['name']}**: 5日跌{r['pct_5d']:.1f}%，注意是否破位\n"
            else:
                report += f"- **{r['name']}**: 走势偏弱，持续关注\n"
        report += "\n"

    # 强势股分析
    if strong:
        report += "### 强势延续 🟢\n\n"
        for r in strong:
            if r['pct_5d'] > 5:
                report += f"- **{r['name']}**: 5日涨{r['pct_5d']:.1f}%，走势强劲\n"
            else:
                report += f"- **{r['name']}**: 维持在五日线上\n"
        report += "\n"

    report += f"""---

## 📋 明日关注

1. 弱势股能否收复五日线？
2. 强势股是否持续放量？
3. 大盘整体环境变化？

---

## ⚠️ 风险提示

- 数据截至 {results[0]['date'] if results else 'N/A'}
- 走势判断基于技术分析，仅供参考
- 投资有风险，决策需谨慎

"""

    # 保存报告
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 简报已生成: {report_file}")
    return report_file

if __name__ == "__main__":
    generate_report()
