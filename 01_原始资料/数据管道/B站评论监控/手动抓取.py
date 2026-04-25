#!/usr/bin/env python3
"""
B站评论监控 - 手动触发版
通过浏览器snapshot获取评论并发送邮件报告

使用方法: python3 手动抓取.py
"""

import json
import os
import re
import subprocess
from datetime import datetime

# 配置
DATA_DIR = "/Users/humiles/OpenClaw项目/莫大韭菜/01_原始资料/B站动态/评论树"
EMAIL_RECIPIENT = "pandaclaw2026@outlook.com"
UID = "525121722"

def parse_snapshot(snapshot_text):
    """解析browser snapshot中的评论数据"""
    comments = []
    
    # 使用正则匹配评论块
    # 匹配模式: 用户名 + 内容 + 时间
    pattern = r'link "([^"]+)"[^u]*uname[^"]*"([^"]+)"[^>]*>[^<]*<[^>]*>[^u]*paragraph "([^"]+)"[^>]*>[^<]*<[^>]*>[^>]*>[^u]*generic "([^"]+)"'
    
    # 简单解析：提取所有评论元素
    lines = snapshot_text.split('\n')
    
    # 从snapshot文本中提取评论数据
    # 格式: 用户名, 内容, 时间
    comment_pattern = re.compile(
        r'link "([^"]+)"[^u]*uname[^"]*"([^"]+)"[^>]*>.*?paragraph "([^"]+)"[^>]*>.*?generic "(\d+小时前|\d+分钟前|\d+天前|\d{4}-\d{2}-\d{2})',
        re.DOTALL
    )
    
    # 更简单的方式：从snapshot中查找评论数据
    # 查找包含用户名和评论内容的块
    blocks = snapshot_text.split('paragraph')
    
    for i, block in enumerate(blocks[1:], 1):  # skip first
        try:
            # 尝试提取用户名
            name_match = re.search(r'link "([^"]+)"[^>]*>[^u]*link "([^"]+)"', block)
            if not name_match:
                continue
            uname = name_match.group(2) if name_match.group(1) != uname else name_match.group(1)
            
            # 提取内容 - 在paragraph标签后
            content_match = re.search(r'paragraph "([^"]+)"', block)
            if not content_match:
                continue
            content = content_match.group(1)
            
            # 提取时间
            time_match = re.search(r'generic "(\d+小时前|\d+分钟前|\d+天前|\d{4}-\d{2}-\d{2})"', block)
            if not time_match:
                continue
            time = time_match.group(1)
            
            if uname and content:
                comments.append({
                    "uname": uname,
                    "content": content,
                    "time": time,
                    "mid": str(i),
                    "like": 0
                })
        except:
            continue
    
    return comments[:50]  # 限制数量

def generate_html(comments, fetch_time):
    """生成HTML报告"""
    UP_UID = UID
    
    total = len(comments)
    total_likes = sum(c.get("like", 0) for c in comments)
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>B站评论监控 - {fetch_time[:10]}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f5f5f5; padding: 20px; line-height: 1.6; }}
        .container {{ max-width: 720px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #00a1d6, #00c8d6); color: white; padding: 24px; border-radius: 12px; margin-bottom: 16px; }}
        .header h1 {{ font-size: 20px; margin-bottom: 6px; }}
        .header p {{ opacity: 0.85; font-size: 13px; }}
        .stats {{ display: flex; gap: 12px; margin-top: 12px; flex-wrap: wrap; }}
        .stat {{ background: rgba(255,255,255,0.25); padding: 8px 16px; border-radius: 8px; }}
        .stat-label {{ font-size: 11px; opacity: 0.9; }}
        .stat-value {{ font-size: 20px; font-weight: bold; }}
        
        .comment {{ background: white; border-radius: 10px; padding: 14px 16px; margin-bottom: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }}
        .comment-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }}
        .name {{ font-weight: 600; font-size: 14px; color: #18191c; }}
        .time {{ color: #9499a0; font-size: 12px; margin-left: auto; }}
        .content {{ color: #18191c; font-size: 14px; }}
        
        .footer {{ text-align: center; padding: 16px; color: #9499a0; font-size: 12px; }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📺 B站评论监控报告</h1>
        <p>莫大韭菜 · 近期更新</p>
        <div class="stats">
            <div class="stat"><div class="stat-label">评论数</div><div class="stat-value">{total}</div></div>
        </div>
    </div>
'''
    
    for c in comments:
        uname = c.get("uname", "未知")
        content = c.get("content", "")
        time = c.get("time", "")
        
        html += f'''    <div class="comment">
        <div class="comment-header">
            <span class="name">{uname}</span>
            <span class="time">{time}</span>
        </div>
        <div class="content">{content}</div>
    </div>
'''
    
    html += f'''    <div class="footer">数据来源: Bilibili | 抓取时间: {fetch_time}</div>
</div>
</body>
</html>'''
    
    return html

def send_email(html, fetch_time):
    """发送邮件"""
    subject = f"【B站监控】莫大韭菜评论 {fetch_time[:10]}"
    
    html_escaped = html.replace('"', '\\"').replace('\n', ' ')
    cmd = f'''bash ~/Library/Application\\ Support/QClaw/openclaw/config/skills/email-skill/scripts/unix/email_gateway.sh send \
  --provider personal \
  --to {EMAIL_RECIPIENT} \
  --subject "{subject}" \
  --html "{html_escaped}"'''
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"📧 邮件发送结果: {result.returncode}")
    if result.returncode != 0:
        print(f"   错误: {result.stderr[:200]}")
    return result.returncode == 0

def main():
    print("=" * 50)
    print("B站评论监控 - 手动抓取")
    print("=" * 50)
    print("请先在浏览器中打开B站动态页面")
    print("然后运行此脚本获取snapshot")
    print()
    print("⚠️ 当前脚本仅支持手动模式")
    print("定时任务将通过cron调用")
    print("=" * 50)

if __name__ == "__main__":
    main()