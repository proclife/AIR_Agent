#!/usr/bin/env python3
"""
Phase V 数据管道 - 一键更新和分析
"""

import sys
import os
from datetime import datetime

# 确保可以导入同目录的模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 60)
    print("Phase V 数据管道 - 每日更新")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 检查并更新市场数据
    print("\n[1/3] 检查市场数据...")
    try:
        from 市场数据查询 import analyze_all
        analyze_all()
        print("✅ 市场数据检查完成")
    except Exception as e:
        print(f"❌ 数据检查失败: {e}")
    
    # 2. 生成每日简报
    print("\n[2/3] 生成每日简报...")
    try:
        from 每日简报生成 import generate_report
        report_file = generate_report()
        print(f"✅ 简报已生成: {report_file}")
    except Exception as e:
        print(f"❌ 简报生成失败: {e}")
    
    # 3. 输出提示
    print("\n[3/3] 检查需要关注的股票...")
    
    # 简单检查弱势股
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
    }
    
    import csv
    DATA_DIR = "/Users/humiles/莫大韭菜/02_市场数据/历史数据"
    
    def calc_ma(data, days):
        if len(data) < days:
            return None
        return sum(d['close'] for d in data[-days:]) / days
    
    weak_stocks = []
    strong_stocks = []
    
    for code, name in STOCKS.items():
        csv_file = f"{DATA_DIR}/{code}.csv"
        if not os.path.exists(csv_file):
            continue
        
        data = []
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    data.append({
                        'close': float(row['close']),
                        'pctChg': float(row['pctChg']) if row.get('pctChg') else 0,
                    })
                except:
                    continue
        
        if len(data) < 6:
            continue
        
        latest = data[-1]
        ma5 = calc_ma(data, 5)
        pct_5d = (latest['close'] / data[-6]['close'] - 1) * 100
        
        if latest['close'] <= ma5:
            weak_stocks.append((name, pct_5d))
        else:
            strong_stocks.append((name, pct_5d))
    
    if weak_stocks:
        print("\n⚠️ 弱势股 (需关注):")
        for name, pct in sorted(weak_stocks, key=lambda x: x[1]):
            print(f"  - {name}: 5日{pct:+.1f}%")
    
    if strong_stocks:
        print("\n🟢 强势股:")
        for name, pct in sorted(strong_stocks, key=lambda x: x[1], reverse=True):
            print(f"  - {name}: 5日{pct:+.1f}%")
    
    print("\n" + "=" * 60)
    print("✅ Phase V 数据管道更新完成")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
