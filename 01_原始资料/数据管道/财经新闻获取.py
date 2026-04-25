#!/usr/bin/env python3
"""
财经新闻获取脚本 - 支持多频道
获取东方财富财经新闻，按频道自动保存
"""
import akshare as ak
import json
from datetime import datetime
from pathlib import Path
import os

# 配置
OUTPUT_DIR = Path('/Users/humiles/OpenClaw项目/莫大韭菜/02_市场数据/重大新闻')
CATEGORIES = ['A股', '板块', '期货', '港股', '基金', '外汇', '美股']

def fetch_news(category: str) -> dict:
    """获取指定分类的新闻"""
    try:
        news = ak.stock_news_em(symbol=category)
        return news.to_dict(orient='records')
    except Exception as e:
        print(f"获取{category}新闻失败: {e}")
        return []

def main():
    today = datetime.now().strftime('%Y-%m-%d')
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    all_news = {
        'fetch_time': f"{today} {datetime.now().strftime('%H:%M:%S')}",
        'categories': {},
        'total': 0
    }
    
    for cat in CATEGORIES:
        news_list = fetch_news(cat)
        if news_list:
            all_news['categories'][cat] = {
                'count': len(news_list),
                'news': news_list
            }
            all_news['total'] += len(news_list)
            print(f"✅ {cat}: {len(news_list)}条")
        else:
            print(f"❌ {cat}: 0条")
    
    # 保存
    output_file = OUTPUT_DIR / f'财经新闻_{today}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    
    print(f"\n已保存到: {output_file}")
    print(f"总计: {all_news['total']}条新闻")

if __name__ == '__main__':
    main()