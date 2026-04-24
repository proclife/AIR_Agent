#!/usr/bin/env python3
"""
B站视频处理管道 — 一键：抓取元数据 → 下载音频 → 转写文字 → 更新索引

用法:
  # 处理单个视频
  python3 bilibili_pipeline.py BV13qdfBtEhF

  # 处理最新N个视频（自动检测未处理的）
  python3 bilibili_pipeline.py --latest 5

  # 只下载音频（不转写）
  python3 bilibili_pipeline.py BV13qdfBtEhF --skip-transcribe

  # 强制重新转写
  python3 bilibili_pipeline.py BV13qdfBtEhF --force

环境依赖:
  - yt-dlp (brew install yt-dlp)
  - ffmpeg (brew install ffmpeg)
  - openai-whisper (pip3.14 install openai-whisper --break-system-packages)
  - ~/.bili_cookies_netscape.txt (Netscape格式Cookie，用于充电视频)
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# ============ 配置 ============

PROJECT_PATH = Path("/Users/humiles/OpenClaw项目/莫大韭菜")
AUDIO_DIR = PROJECT_PATH / "01_原始资料" / "B站音频"
TRANSCRIPT_DIR = PROJECT_PATH / "01_原始资料" / "B站转写"
VIDEO_DATA_DIR = PROJECT_PATH / "01_原始资料" / "B站动态" / "视频数据"
INDEX_DIR = PROJECT_PATH / "04_索引文件"

COOKIE_FILE = Path(os.path.expanduser("~/.bili_cookies_netscape.txt"))

# Whisper 配置
WHISPER_MODEL = "base"
WHISPER_LANGUAGE = "zh"
WHISPER_DEVICE = "cpu"
KMP_DUPLICATE_LIB_OK = "TRUE"

# Bilibili API
BILIBILI_API_VIEW = "https://api.bilibili.com/x/web-interface/view"
MID = "510515380"  # 莫大韭菜的UID


# ============ Step 1: 获取视频元数据 ============

def fetch_video_metadata(bvid: str) -> dict:
    """从Bilibili API获取视频元数据"""
    import urllib.request

    url = f"{BILIBILI_API_VIEW}?bvid={bvid}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Referer": "https://www.bilibili.com"
    })

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())

    if data["code"] != 0:
        raise RuntimeError(f"API错误: {data['message']}")

    v = data["data"]
    meta = {
        "bvid": v["bvid"],
        "aid": v["aid"],
        "title": v["title"],
        "pubdate": datetime.fromtimestamp(v["pubdate"]).strftime("%Y-%m-%d %H:%M:%S"),
        "duration_sec": v["duration"],
        "stat": {
            "view": v["stat"]["view"],
            "like": v["stat"]["like"],
            "coin": v["stat"]["coin"],
            "danmaku": v["stat"]["danmaku"],
            "reply": v["stat"]["reply"],
            "favorite": v["stat"]["favorite"],
        },
        "owner": {
            "mid": v["owner"]["mid"],
            "name": v["owner"]["name"],
        },
        "video_url": f"https://www.bilibili.com/video/{bvid}",
        "rights": v.get("rights", {}),
    }

    # 检查是否充电视频
    if v.get("rights", {}).get("is_cooperation", 0) == 1 or "upower" in str(v.get("desc", "")):
        meta["is_paid"] = True
    else:
        meta["is_paid"] = False

    return meta


def save_metadata(meta: dict) -> Path:
    """保存元数据到JSON文件"""
    date_str = meta["pubdate"][:10]  # YYYY-MM-DD
    filename = f"{date_str}_视频_{meta['bvid']}.json"
    filepath = VIDEO_DATA_DIR / filename

    VIDEO_DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"  ✅ 元数据已保存: {filepath.name}")
    return filepath


# ============ Step 2: 下载音频 ============

def download_audio(bvid: str, title: str) -> Path:
    """使用yt-dlp下载音频"""
    url = f"https://www.bilibili.com/video/{bvid}"
    safe_title = title.replace("/", "_").replace("\\", "_").replace(":", "_")
    output_path = AUDIO_DIR / f"{safe_title}.mp3"

    if output_path.exists():
        print(f"  ⏭️ 音频已存在: {output_path.name}")
        return output_path

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    cmd = [
        "yt-dlp",
        "--cookies", str(COOKIE_FILE),
        "-x", "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", str(output_path),
        url
    ]

    print(f"  ⬇️ 下载音频: {title[:40]}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  ❌ 下载失败: {result.stderr[:200]}")
        raise RuntimeError(f"yt-dlp 失败: {result.returncode}")

    if output_path.exists():
        size_mb = output_path.stat().st_size / 1024 / 1024
        print(f"  ✅ 音频已下载: {output_path.name} ({size_mb:.1f}MB)")
        return output_path
    else:
        raise RuntimeError("下载完成但文件未找到")


# ============ Step 3: 转写音频 ============

def transcribe_audio(audio_path: Path, force: bool = False, model: str = None) -> Path:
    """使用openai-whisper转写音频"""
    title = audio_path.stem
    output_txt = TRANSCRIPT_DIR / f"{title}.txt"

    if output_txt.exists() and not force:
        print(f"  ⏭️ 转写已存在: {output_txt.name}")
        return output_txt

    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["KMP_DUPLICATE_LIB_OK"] = KMP_DUPLICATE_LIB_OK

    use_model = model or WHISPER_MODEL

    cmd = [
        "whisper",
        str(audio_path),
        "--model", use_model,
        "--output_format", "txt",
        "--output_dir", str(TRANSCRIPT_DIR),
        "--language", WHISPER_LANGUAGE,
        "--device", WHISPER_DEVICE,
    ]

    print(f"  🎤 转写中 (model={use_model}, lang={WHISPER_LANGUAGE})...")
    # 估算耗时：base模型约10min/MiB on CPU
    duration_min = audio_path.stat().st_size / 1024 / 1024 * 0.1
    print(f"     预计耗时: ~{duration_min:.0f}分钟")

    result = subprocess.run(cmd, env=env, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  ❌ 转写失败: {result.stderr[:200]}")
        raise RuntimeError(f"whisper 失败: {result.returncode}")

    if output_txt.exists():
        size_kb = output_txt.stat().st_size / 1024
        print(f"  ✅ 转写完成: {output_txt.name} ({size_kb:.1f}KB)")
        return output_txt
    else:
        raise RuntimeError("转写完成但文件未找到")


# ============ Step 4: 更新索引 ============

def update_indexes(meta: dict, audio_path: Path, transcript_path: Path):
    """更新timeline、mapping、dates三个索引文件"""

    # --- timeline.jsonl ---
    timeline_file = INDEX_DIR / "timeline.jsonl"
    word_count = 0
    if transcript_path.exists():
        with open(transcript_path, "r", encoding="utf-8") as f:
            word_count = len(f.read())

    entry = {
        "filename": transcript_path.stem,
        "date": meta["pubdate"][:10],
        "size": transcript_path.stat().st_size,
        "word_count": word_count,
    }

    with open(timeline_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"  ✅ timeline.jsonl 已更新")

    # --- audio_transcript_mapping.jsonl ---
    mapping_file = INDEX_DIR / "audio_transcript_mapping.jsonl"
    entry = {
        "audio": audio_path.stem,
        "transcript": transcript_path.stem,
        "date": meta["pubdate"][:10],
        "audio_size": audio_path.stat().st_size,
    }

    with open(mapping_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"  ✅ audio_transcript_mapping.jsonl 已更新")

    # --- extracted_dates.jsonl ---
    dates_file = INDEX_DIR / "extracted_dates.jsonl"
    entry = {
        "filename": transcript_path.stem,
        "date": meta["pubdate"][:10],
        "has_audio": audio_path.exists(),
    }

    with open(dates_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"  ✅ extracted_dates.jsonl 已更新")


# ============ Step 5: 获取最新视频列表 ============

def get_latest_videos(count: int = 5) -> list:
    """获取UP主最新视频列表"""
    import urllib.request

    url = f"https://api.bilibili.com/x/space/arc/search?mid={MID}&ps={count}&pn=1&order=pubdate"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Referer": "https://www.bilibili.com"
    })

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        if data["code"] == 0:
            return data["data"]["list"]["vlist"]
    except Exception as e:
        print(f"  ⚠️ 获取视频列表失败: {e}")

    return []


def get_unprocessed_videos(count: int = 10) -> list:
    """获取尚未处理的视频列表"""
    # 获取已有转写
    existing = set()
    if TRANSCRIPT_DIR.exists():
        existing = {f.stem for f in TRANSCRIPT_DIR.glob("*.txt")}

    videos = get_latest_videos(count)
    unprocessed = []
    for v in videos:
        title = v["title"].replace("/", "_").replace("\\", "_").replace(":", "_")
        if title not in existing:
            unprocessed.append(v)

    return unprocessed


# ============ 主流程 ============

def process_video(bvid: str, skip_transcribe: bool = False, force: bool = False, model: str = None):
    """处理单个视频的完整流程"""
    print(f"\n{'='*60}")
    print(f"🎬 处理视频: {bvid}")
    print(f"{'='*60}")

    # Step 1: 元数据
    print("\n📡 Step 1: 获取视频元数据")
    meta = fetch_video_metadata(bvid)
    print(f"  标题: {meta['title']}")
    print(f"  日期: {meta['pubdate']}")
    print(f"  时长: {meta['duration_sec']//60}分{meta['duration_sec']%60}秒")
    print(f"  播放: {meta['stat']['view']}")
    save_metadata(meta)

    # Step 2: 下载音频
    print("\n⬇️ Step 2: 下载音频")
    audio_path = download_audio(bvid, meta["title"])

    # Step 3: 转写
    if skip_transcribe:
        print("\n⏭️ Step 3: 跳过转写 (--skip-transcribe)")
        transcript_path = TRANSCRIPT_DIR / f"{audio_path.stem}.txt"
    else:
        print("\n🎤 Step 3: 转写音频")
        transcript_path = transcribe_audio(audio_path, force=force, model=model)

    # Step 4: 更新索引
    print("\n📋 Step 4: 更新索引文件")
    if transcript_path.exists():
        update_indexes(meta, audio_path, transcript_path)
    else:
        print("  ⚠️ 无转写文件，跳过索引更新")

    print(f"\n{'='*60}")
    print(f"✅ {bvid} 处理完成!")
    print(f"{'='*60}")

    return {
        "bvid": bvid,
        "title": meta["title"],
        "audio": str(audio_path),
        "transcript": str(transcript_path) if transcript_path.exists() else None,
    }


def main():
    parser = argparse.ArgumentParser(description="B站视频处理管道")
    parser.add_argument("bvid", nargs="?", help="视频BV号 (如 BV13qdfBtEhF)")
    parser.add_argument("--latest", type=int, metavar="N", help="处理最新N个未处理视频")
    parser.add_argument("--skip-transcribe", action="store_true", help="跳过转写步骤")
    parser.add_argument("--force", action="store_true", help="强制重新转写")
    parser.add_argument("--model", default=WHISPER_MODEL, help=f"Whisper模型 (默认: {WHISPER_MODEL})")
    parser.add_argument("--dry-run", action="store_true", help="只显示要处理的视频，不执行")

    args = parser.parse_args()

    # 检查依赖
    for cmd in ["yt-dlp", "ffmpeg", "whisper"]:
        r = subprocess.run(["which", cmd], capture_output=True)
        if r.returncode != 0:
            print(f"❌ 缺少依赖: {cmd}")
            if cmd == "whisper":
                print("   安装: pip3.14 install openai-whisper --break-system-packages")
            else:
                print(f"   安装: brew install {cmd}")
            sys.exit(1)

    if not COOKIE_FILE.exists():
        print(f"❌ Cookie文件不存在: {COOKIE_FILE}")
        print("   请先转换Cookie为Netscape格式")
        sys.exit(1)

    if args.latest:
        # 批量处理最新视频
        print(f"🔍 查找最新 {args.latest} 个未处理视频...")
        videos = get_unprocessed_videos(args.latest)
        if not videos:
            print("✅ 所有视频都已处理，无需更新")
            return

        print(f"找到 {len(videos)} 个未处理视频:")
        for v in videos:
            print(f"  - {v['bvid']}: {v['title'][:40]}")

        if args.dry_run:
            return

        results = []
        for v in videos:
            try:
                r = process_video(v["bvid"], skip_transcribe=args.skip_transcribe, force=args.force, model=args.model)
                results.append(r)
            except Exception as e:
                print(f"❌ {v['bvid']} 处理失败: {e}")
                continue

        print(f"\n\n📊 批量处理完成: {len(results)}/{len(videos)} 成功")

    elif args.bvid:
        # 处理单个视频
        process_video(args.bvid, skip_transcribe=args.skip_transcribe, force=args.force, model=args.model)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
