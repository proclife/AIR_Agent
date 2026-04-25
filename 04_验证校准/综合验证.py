#!/usr/bin/env python3
"""
Phase VI 验证校准 - 莫大框架综合验证
结合行业景气度和技术分析
"""

import csv
import os
from datetime import datetime

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
            except:
                continue
    return data

def calc_ma(data, days):
    if len(data) < days:
        return None
    return sum(d['close'] for d in data[-days:]) / days

def calc_volume_ma(data, days):
    """计算成交量均线"""
    if len(data) < days:
        return None
    return sum(d['volume'] for d in data[-days:]) / days

def moda_analyze(data, date, stock_info):
    """
    莫大韭菜框架分析
    
    核心要素：
    1. 走势判断（五日线）
    2. 位置判断（历史高位/低位）
    3. 量能变化
    4. 行业景气度（外部输入）
    """
    
    # 找到目标日期
    target_idx = None
    for i, d in enumerate(data):
        if d['date'] == date:
            target_idx = i
            break
    if target_idx is None:
        return None
    
    analysis_data = data[:target_idx+1]
    if len(analysis_data) < 60:
        return None
    
    latest = analysis_data[-1]
    ma5 = calc_ma(analysis_data, 5)
    ma20 = calc_ma(analysis_data, 20)
    ma60 = calc_ma(analysis_data, 60)
    
    # 历史位置
    hist_min = min(d['close'] for d in analysis_data)
    hist_max = max(d['close'] for d in analysis_data)
    hist_pct = (latest['close'] - hist_min) / (hist_max - hist_min) * 100 if hist_max != hist_min else 50
    
    # 量能判断
    vol_ma5 = calc_volume_ma(analysis_data, 5)
    vol_ma20 = calc_volume_ma(analysis_data, 20)
    vol_ratio = latest['volume'] / vol_ma20 if vol_ma20 else 1
    
    # 莫大判断
    if latest['close'] > ma5:
        trend = "🟢 五日线上"
        trend_score = 1
    elif latest['close'] > ma20:
        trend = "🟡 盘整"
        trend_score = 0
    else:
        trend = "🔴 五日线下"
        trend_score = -1
    
    # 位置判断
    if hist_pct > 80:
        position = "历史高位"
        pos_score = -1
    elif hist_pct < 20:
        position = "历史低位"
        pos_score = 1
    else:
        position = "中部"
        pos_score = 0
    
    # 量能判断
    if vol_ratio > 1.5:
        volume = "放量"
        vol_score = 1
    elif vol_ratio < 0.7:
        volume = "缩量"
        vol_score = -1
    else:
        volume = "正常"
        vol_score = 0
    
    # 综合评分 (-3 到 +3)
    total_score = trend_score + pos_score + vol_score
    
    # 建议
    if total_score >= 2:
        suggestion = "关注"
        base_confidence = 7
    elif total_score <= -2:
        suggestion = "观望"
        base_confidence = 5
    else:
        suggestion = "中性"
        base_confidence = 5
    
    return {
        'date': date,
        'price': latest['close'],
        'trend': trend,
        'position': position,
        'hist_pct': hist_pct,
        'volume': volume,
        'vol_ratio': vol_ratio,
        'ma5': ma5,
        'ma20': ma20,
        'ma60': ma60,
        'score': total_score,
        'suggestion': suggestion,
        'confidence': base_confidence,
    }

def run_validation():
    """运行验证"""
    print("=" * 70)
    print("Phase VI 验证校准 - 莫大韭菜框架综合验证")
    print("=" * 70)
    
    # 测试案例 (股票代码, 日期, 行业景气度, 预期操作)
    test_cases = [
        # 强势+低位+放量 = 买入信号
        ("002594", "2020-01-02", "高", "买入", "新能源启动"),
        
        # 强势+高位 = 谨慎
        ("002594", "2021-02-10", "高", "持有/减仓", "比亚迪历史高位"),
        
        # 弱势+低位 = 可观察
        ("601020", "2022-04-27", "中", "观察", "ST后低位"),
        ("601020", "2022-04-27", "高", "买入", "锑矿反转逻辑"),
        
        # 商业航天
        ("600343", "2025-01-02", "高", "买入", "航天启动"),
        ("600343", "2025-06-02", "高", "持有", "航天主升"),
        
        # 锂矿
        ("000762", "2021-09-01", "高", "减仓", "锂价高位"),
        ("000762", "2020-03-01", "中", "买入", "锂价启动"),
    ]
    
    results = []
    
    for code, date, industry, expected, description in test_cases:
        stock_names = {
            "002594": "比亚迪",
            "601020": "华钰矿业",
            "600343": "航天动力",
            "000762": "西藏矿业",
        }
        name = stock_names.get(code, code)
        
        data = read_stock_data(code)
        if not data:
            print(f"\n⚠️ {name}: 无数据")
            continue
        
        result = moda_analyze(data, date, {"industry": industry})
        if not result:
            print(f"\n⚠️ {name} @ {date}: 日期不存在")
            continue
        
        # 跟踪未来走势
        target_idx = None
        for i, d in enumerate(data):
            if d['date'] == date:
                target_idx = i
                break
        
        if target_idx:
            future = data[target_idx+1:target_idx+31] if target_idx+31 <= len(data) else data[target_idx+1:]
            if future:
                entry = result['price']
                future_return = (future[-1]['close'] / entry - 1) * 100
                max_up = (max(d['high'] for d in future) / entry - 1) * 100
                max_down = (min(d['low'] for d in future) / entry - 1) * 100
            else:
                future_return = max_up = max_down = 0
        else:
            future_return = max_up = max_down = 0
        
        # 判断是否正确
        if expected == "买入" and result['score'] >= 1 and future_return > 0:
            correct = "✓ 正确"
        elif expected == "观望" and result['score'] <= 0:
            correct = "✓ 正确"
        elif expected == "减仓" and result['hist_pct'] > 70:
            correct = "✓ 正确"
        elif expected == "持有" and result['trend'].startswith("🟢"):
            correct = "✓ 正确"
        else:
            correct = "○ 需调整"
        
        results.append({
            'name': name,
            'date': date,
            'description': description,
            'expected': expected,
            'result': result,
            'future': future_return,
            'correct': correct,
        })
        
        print(f"""
{'='*60}
【{name}】{date}
说明: {description}
{'='*60}

【莫大框架分析】
走势: {result['trend']}
位置: {result['position']} ({result['hist_pct']:.0f}%分位)
量能: {result['volume']} ({result['vol_ratio']:.2f}x)
综合评分: {result['score']} ({result['suggestion']})
置信度: {result['confidence']}/10

均线:
  MA5:  {result['ma5']:.2f}  {'✓' if result['price'] > result['ma5'] else '✗'}
  MA20: {result['ma20']:.2f}  {'✓' if result['price'] > result['ma20'] else '✗'}
  MA60: {result['ma60']:.2f}  {'✓' if result['price'] > result['ma60'] else '✗'}

30天表现:
  最大涨幅: {max_up:+.1f}%
  最大跌幅: {max_down:+.1f}%
  最终涨跌: {future_return:+.1f}%

【判断对比】
预期操作: {expected}
框架建议: {result['suggestion']}
验证结果: {correct}
""")
    
    # 统计
    print("\n" + "=" * 70)
    print("验证统计")
    print("=" * 70)
    
    correct = sum(1 for r in results if "正确" in r['correct'])
    total = len(results)
    
    print(f"测试案例: {total}")
    print(f"正确判断: {correct}")
    print(f"准确率: {correct/total*100:.1f}%" if total > 0 else "N/A")
    
    # 按预期分类统计
    buy_cases = [r for r in results if "买入" in r['expected']]
    hold_cases = [r for r in results if "持有" in r['expected']]
    reduce_cases = [r for r in results if "减仓" in r['expected']]
    
    if buy_cases:
        avg_ret = sum(r['future'] for r in buy_cases) / len(buy_cases)
        print(f"\n买入信号后续30天平均收益: {avg_ret:+.1f}%")
    
    if hold_cases:
        avg_ret = sum(r['future'] for r in hold_cases) / len(hold_cases)
        print(f"持有信号后续30天平均收益: {avg_ret:+.1f}%")
    
    return results

if __name__ == "__main__":
    results = run_validation()
