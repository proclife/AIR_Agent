#!/usr/bin/env python3
"""
财报数据获取脚本 - 修复版
每周自动更新K线数据中所有股票的财报信息
"""
import baostock as bs
import pandas as pd
import os
import sys

# 配置路径
FINANCIAL_DATA_DIR = "/Users/humiles/OpenClaw项目/莫大韭菜/02_市场数据/财报数据"
KLINE_DIR = "/Users/humiles/OpenClaw项目/莫大韭菜/02_市场数据/K线数据/A股"

# 获取A股股票代码列表
def get_stock_codes():
    codes = []
    for f in os.listdir(KLINE_DIR):
        if f.endswith('.csv') and not f.startswith('ETF_') and not f.startswith(('15', '39')):
            code = f.replace('.csv', '')
            # 跳过纯数字代码（已处理）
            if code.isdigit():
                codes.append(code)
    return sorted(codes)

# 获取股票名称
def get_stock_name(code):
    if len(code) == 6 and code.isdigit():
        if code.startswith('688'):
            bs_code = 'sh.' + code
        else:
            bs_code = 'sz.' + code
        
        rs = bs.query_stock_basic(code=bs_code)
        if rs.next():
            return rs.get_row_data()[1] or code
    return code

def main():
    print(f"=== 财报数据获取 ===")
    
    codes = get_stock_codes()
    print(f"共 {len(codes)} 只股票")
    
    # 登录一次
    lg = bs.login()
    if lg.error_code != '0':
        print(f"登录失败: {lg.error_msg}")
        sys.exit(1)
    
    success = 0
    skip = 0
    
    for i, code in enumerate(codes):
        # 检查是否已有
        existing = [f for f in os.listdir(FINANCIAL_DATA_DIR) if f.startswith(code + '_')]
        if existing:
            skip += 1
            continue
        
        # 获取利润表 - 正确格式
        if code.startswith('688'):
            bs_code = 'sh.' + code
        else:
            bs_code = 'sz.' + code
        
        data_list = []
        for year in range(2021, 2026):
            rs = bs.query_profit_data(bs_code, str(year))
            if rs.error_code == '0':
                while rs.next():
                    data_list.append(rs.get_row_data())
        
        if data_list:
            df = pd.DataFrame(data_list, columns=rs.fields)
            name = get_stock_name(code)
            filepath = os.path.join(FINANCIAL_DATA_DIR, f"{code}_{name}.csv")
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            success += 1
            print(f"[{i+1}/{len(codes)}] {code} {name} ✓ ({len(df)}条)")
        else:
            print(f"[{i+1}/{len(codes)}] {code} 无数据")
    
    bs.logout()
    print(f"\n完成: 新增 {success}, 跳过 {skip}")

if __name__ == "__main__":
    main()