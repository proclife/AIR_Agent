#!/usr/bin/env python3
"""
yfinance 港股数据获取脚本
自动获取港股K线数据，更新本地CSV
"""

import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 配置
HIST_DATA_DIR = "/Users/humiles/OpenClaw项目/莫大韭菜/02_市场数据/K线数据/港股"

# ============ 港股: (yfinance代码, 本地代码, 名称) ============
HK_STOCKS = [
    # 科技巨头
    ("9988.HK", "09988", "阿里巴巴"),
    ("0700.HK", "00700", "腾讯"),
    ("3690.HK", "03690", "美团"),
    ("9618.HK", "09618", "京东"),
    ("9888.HK", "09888", "百度"),
    ("9961.HK", "09961", "携程"),
    ("9999.HK", "09999", "网易"),
    # 新能源车
    ("9868.HK", "09868", "小鹏汽车"),
    ("9866.HK", "09866", "蔚来"),
    ("2015.HK", "02015", "理想汽车"),
    # 消费
    ("2319.HK", "02319", "蒙牛乳业"),
    ("0291.HK", "00291", "华润啤酒"),
    ("1880.HK", "01880", "泡泡玛特"),
    # 金融
    ("0939.HK", "00939", "建设银行"),
    ("3988.HK", "03988", "中国银行"),
    ("2628.HK", "02628", "中国人寿"),
    ("2318.HK", "02318", "平安保险"),
    # 地产/物业
    ("1918.HK", "01918", "融创中国"),
    ("6098.HK", "06098", "碧桂园服务"),
    # 其他
    ("1810.HK", "01810", "小米集团"),
    ("2688.HK", "02688", "新奥能源"),
]


def fetch(code, start="2025-01-01", end=None):
    """获取K线"""
    if end is None:
        end = datetime.now()
    
    try:
        ticker = yf.Ticker(code)
        df = ticker.history(start=start, end=end)
        
        if df.empty or 'Close' not in df.columns:
            return None
        
        # 标准化输出格式
        result = pd.DataFrame({
            'date': df.index.strftime('%Y-%m-%d'),
            'open': df['Open'].values,
            'high': df['High'].values,
            'low': df['Low'].values,
            'close': df['Close'].values,
            'volume': df['Volume'].values,
        })
        
        # 计算涨跌幅
        result['pct_change'] = result['close'].pct_change() * 100
        
        return result
        
    except Exception as e:
        print(f"  获取错误: {e}")
        return None


def update_one(yf_code, local_code, name):
    """更新单个标的"""
    # 确保目录存在
    os.makedirs(HIST_DATA_DIR, exist_ok=True)
    
    filepath = f"{HIST_DATA_DIR}/{local_code}.csv"
    print(f"{local_code} {name}", end=" ", flush=True)
    
    try:
        df_new = fetch(yf_code, "2025-01-01")
        if df_new is None or df_new.empty:
            print("无数据")
            return False
        
        if os.path.exists(filepath):
            df_old = pd.read_csv(filepath)
            old_date = pd.to_datetime(df_old['date']).max()
            new_date = pd.to_datetime(df_new['date']).max()
            
            if new_date > old_date:
                # 追加新数据
                df_new = df_new[pd.to_datetime(df_new['date']) > old_date]
                df = pd.concat([df_old, df_new], ignore_index=True)
                print(f"{old_date.date()}→{new_date.date()}")
            else:
                print(f"无新数据")
                return False
        else:
            df = df_new
            print("新建")
        
        df.to_csv(filepath, index=False, encoding='utf-8')
        return True
        
    except Exception as e:
        print(f"错误: {e}")
        return False


def main():
    print(f"\n=== yfinance 港股数据获取 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    count = 0
    
    print(f"\n--- 港股 ({len(HK_STOCKS)}) ---")
    for yf_code, local_code, name in HK_STOCKS:
        if update_one(yf_code, local_code, name):
            count += 1
    
    print(f"\n=== 完成: 更新 {count} 个 ===\n")


if __name__ == "__main__":
    main()