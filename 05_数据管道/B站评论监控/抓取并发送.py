#!/usr/bin/env python3
"""
B站评论监控 - 通过浏览器snapshot获取评论并发送邮件报告
定时: 9:30, 12:30, 14:30, 22:00
"""

import json
import os
import sys
import subprocess
from datetime import datetime

# 配置
DATA_DIR = "/Users/humiles/OpenClaw项目/莫大韭菜/01_原始资料/B站动态/评论树"
EMAIL_RECIPIENT = "pandaclaw2026@outlook.com"
UID = "525121722"  # 莫大韭菜的UID
BROWSER_TAB_ID = "293CEB9FBF8BDFA316D53F5746E93A86"

def generate_html(comments, fetch_time):
    """生成HTML报告"""
    UP_UID = UID
    
    # 统计
    total = len(comments)
    up_comments = [c for c in comments if str(c.get("mid")) == UP_UID]
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
        .avatar {{ width: 32px; height: 32px; border-radius: 50%; }}
        .name {{ font-weight: 600; font-size: 14px; color: #18191c; }}
        .time {{ color: #9499a0; font-size: 12px; margin-left: auto; }}
        .content {{ color: #18191c; font-size: 14px; }}
        .up-comment {{ background: #fff5f5; border-left: 3px solid #fe2c55; }}
        
        .footer {{ text-align: center; padding: 16px; color: #9499a0; font-size: 12px; }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📺 B站评论监控报告</h1>
        <p>莫大韭菜 · 近4小时更新</p>
        <div class="stats">
            <div class="stat"><div class="stat-label">新评论</div><div class="stat-value">{total}</div></div>
            <div class="stat"><div class="stat-label">UP主评论</div><div class="stat-value">{len(up_comments)}</div></div>
            <div class="stat"><div class="stat-label">总点赞</div><div class="stat-value">{total_likes}</div></div>
        </div>
    </div>
'''
    
    # 只显示前20条评论
    for c in comments[:20]:
        mid = str(c.get("mid", ""))
        is_up = mid == UP_UID
        uname = c.get("uname", "未知")
        content = c.get("content", "")
        like = c.get("like", 0)
        ctime = c.get("time", "")
        
        html += f'''    <div class="comment {'up-comment' if is_up else ''}">
        <div class="comment-header">
            <span class="name">{uname}{' 🎬' if is_up else ''}</span>
            <span class="time">{ctime}</span>
        </div>
        <div class="content">{content}</div>
    </div>
'''
    
    if total > 20:
        html += f'    <div style="text-align:center;color:#9499a0;padding:12px">... 还有 {total-20} 条评论</div>\n'
    
    html += f'''    <div class="footer">数据来源: Bilibili | 抓取时间: {fetch_time}</div>
</div>
</body>
</html>'''
    
    return html

def save_html(html, fetch_time):
    """保存HTML文件"""
    os.makedirs(DATA_DIR, exist_ok=True)
    date_str = fetch_time[:10]
    path = os.path.join(DATA_DIR, f"{date_str}_评论监控.html")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    return path

def send_email(html, fetch_time):
    """发送邮件"""
    subject = f"【B站监控】莫大韭菜评论 {fetch_time[:10]}"
    
    # 使用email skill发送
    html_escaped = html.replace('"', '\\"').replace('\n', ' ')
    cmd = f'''bash ~/Library/Application\\ Support/QClaw/openclaw/config/skills/email-skill/scripts/unix/email_gateway.sh send \
  --provider personal \
  --to {EMAIL_RECIPIENT} \
  --subject "{subject}" \
  --html "{html_escaped}"'''
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0

# 模拟数据 - 实际使用时从snapshot解析
def main():
    fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🕐 检查更新: {fetch_time}")
    
    # 检查是否有新评论（比较上次保存的时间）
    date_str = fetch_time[:10]
    last_file = os.path.join(DATA_DIR, f"{date_str}_评论监控.html")
    
    if os.path.exists(last_file):
        print(f"📄 今日已发送: {last_file}")
        print("⏭️ 跳过")
        return
    
    print("⚠️ 需要手动抓取评论数据")
    print("请使用browser工具获取snapshot后手动生成报告")

if __name__ == "__main__":
    main()