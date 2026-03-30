# Phase V 数据管道

## 概述

基于莫大韭菜投资框架的市场数据管道，用于自动获取、分析和报告持仓股走势。

## 目录结构

```
05_数据管道/
├── README.md              # 本说明文件
├── 一键更新.py             # 一键执行所有操作
├── 市场数据查询.py          # 查询持仓股技术分析
├── 每日简报生成.py         # 生成每日市场简报
├── 每日简报/              # 生成的简报存放目录
│   └── 简报_YYYY-MM-DD.md
└── logs/                  # 日志目录
```

## 使用方法

### 快速开始

```bash
cd ~/莫大韭菜/05_数据管道
python3 一键更新.py
```

### 单独使用

```bash
# 查询所有持仓股
python3 市场数据查询.py

# 查询指定股票
python3 市场数据查询.py 000762

# 生成每日简报
python3 每日简报生成.py
```

## 持仓股列表

| 代码 | 名称 | 板块 | 仓位 | 状态 |
|------|------|------|------|------|
| 000762 | 西藏矿业 | 锂矿 | 16.4% | ✅ |
| 600343 | 航天动力 | 商业航天 | 15.8% | ✅ |
| 002594 | 比亚迪 | 新能源车 | 15.5% | ✅ |
| 002169 | 智光电气 | 储能 | 14.0% | ✅ |
| 688114 | 华大智造 | AI医疗 | 12.6% | ✅ |
| 601020 | 华钰矿业 | 锑矿 | 6.7% | ✅ |
| 002538 | 司尔特 | 磷矿 | 6.4% | ✅ |
| 688559 | 海目星 | 激光设备 | - | ✅ |
| 300034 | 钢研高纳 | 高温合金 | - | ✅ |
| 688533 | 上大股份 | 高温合金 | - | ❌ 需补充 |

## 技术指标

### 均线系统

- **MA5**: 5日均线，短期趋势
- **MA10**: 10日均线
- **MA20**: 20日均线，中期趋势
- **MA60**: 60日均线，长期趋势

### 走势判断

| 状态 | 标准 | 信号 |
|------|------|------|
| 🟢 强势 | 价格 > MA5 | 五日线上，可格局 |
| 🟡 盘整 | MA5 < 价格 < MA10 | 观望 |
| 🔴 弱势 | 价格 < MA5 | 减仓/止损 |

## 输出内容

### 每日简报

- 持仓股涨跌汇总
- 强势/弱势分类
- 走势分布统计
- 操作建议
- 明日关注

## 定时任务设置

### macOS (launchd)

创建 `~/Library/LaunchAgents/com.modaocai.marketdata.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.modaocai.marketdata</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/humiles/莫大韭菜/05_数据管道/一键更新.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</key>
        <key>Minute</key>
        <integer>15</integer>
    </dict>
</dict>
</plist>
```

### 手动加载

```bash
launchctl load ~/Library/LaunchAgents/com.modaocai.marketdata.plist
launchctl start com.modaocai.marketdata
```

## 数据来源

- **历史数据**: 本地 CSV 文件
- **实时数据**: akshare (需联网)
- **更新频率**: 每日开盘前

## 注意事项

1. 数据截止到上一个交易日
2. 需要 Python 3.6+
3. 如需实时数据，需安装 akshare: `pip3 install akshare`

## 更新日志

### 2026-03-26
- 初始版本
- 支持持仓股技术分析
- 支持每日简报生成
