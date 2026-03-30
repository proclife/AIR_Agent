# 莫大韭菜雪球监控系统

**账户链接：** https://xueqiu.com/u/2632831661  
**监控内容：**
- ✅ 发言（原创帖子）
- ✅ 评论（前30最热评论）
- ✅ 回复（对评论的回复）
- ❌ 点赞记录（不需要）

---

## 📋 项目状态

### 当前阶段
- ⏳ **开发中** - 雪球反爬虫机制复杂，需要特殊处理

### 技术挑战
1. **JavaScript 动态加载** — 雪球使用 React，内容动态渲染
2. **反爬虫机制** — 需要真实浏览器环境
3. **登录要求** — 某些内容需要登录才能查看

### 解决方案

#### 方案 A：使用 Camoufox（推荐）
```bash
# Camoufox 是反爬虫浏览器，可绕过大多数反爬机制
# 需要安装：brew install camoufox
```

#### 方案 B：使用 OpenClaw 浏览器自动化
```bash
# 通过 Gateway API 调用浏览器工具
# 脚本：xueqiu_monitor_v2.py
```

#### 方案 C：手动导出
```
1. 访问 https://xueqiu.com/u/2632831661
2. 手动复制发言、评论、回复内容
3. 保存为 JSON 文件
```

---

## 🚀 快速开始

### 安装依赖
```bash
cd ~/.qclaw/workspace/skills/xueqiu-monitor
source .venv/bin/activate
# 依赖已安装：requests, beautifulsoup4
```

### 运行脚本
```bash
# v1：API 方式（已失效）
python3 xueqiu_monitor.py

# v2：浏览器自动化方式（开发中）
python3 xueqiu_monitor_v2.py
```

---

## 📊 数据格式

### 发言数据
```json
{
  "fetch_date": "2026-03-29",
  "total": 10,
  "posts": [
    {
      "id": "123456",
      "text": "发言内容",
      "created_at": "2026-03-29 10:00:00",
      "likes": 100,
      "comments": 50,
      "reposts": 10,
      "url": "https://xueqiu.com/status/123456"
    }
  ]
}
```

### 评论数据
```json
{
  "fetch_date": "2026-03-29",
  "total": 30,
  "comments": [
    {
      "id": "789012",
      "text": "评论内容",
      "created_at": "2026-03-29 10:05:00",
      "likes": 20,
      "target_id": "123456",
      "target_text": "被评论的帖子内容"
    }
  ]
}
```

### 回复数据
```json
{
  "fetch_date": "2026-03-29",
  "total": 50,
  "replies": [
    {
      "id": "345678",
      "text": "回复内容",
      "created_at": "2026-03-29 10:10:00",
      "likes": 5,
      "target_id": "789012",
      "target_text": "被回复的评论内容"
    }
  ]
}
```

---

## ⏰ 定时监控

### 配置定时任务
```bash
# 每天 10:00 自动检查新发言
cron add --schedule "0 10 * * *" --task "python3 ~/.qclaw/workspace/skills/xueqiu-monitor/xueqiu_monitor.py"
```

### 实时通知
- 当检测到新发言时，自动发送通知
- 包含发言内容、发布时间、互动数据

---

## 🔐 数据安全

- ✅ 仅抓取公开数据
- ✅ 本地存储（无云端上传）
- ✅ 完整的日志审计
- ✅ 遵守雪球 ToS

---

## 📝 文件清单

| 文件 | 说明 |
|------|------|
| `xueqiu_monitor.py` | v1 - API 方式（已失效） |
| `xueqiu_monitor_v2.py` | v2 - 浏览器自动化方式 |
| `抓取日志.txt` | 执行日志 |
| `last_run.json` | 最后运行记录 |
| `README.md` | 本文件 |

---

## 🎯 下一步

1. **测试浏览器自动化** — 验证 Camoufox 或 OpenClaw 浏览器是否可用
2. **完善数据提取** — 实现页面解析逻辑
3. **配置定时任务** — 设置每日自动检查
4. **实现实时通知** — 新发言时自动告知

---

**项目状态：** 🟡 **开发中**  
**最后更新：** 2026-03-29 21:35 GMT+8

