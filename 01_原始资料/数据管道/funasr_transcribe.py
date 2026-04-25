#!/usr/bin/env python3
"""
FunASR 转写测试 - 带热词
"""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from funasr import AutoModel

# 热词文件
hotwords_file = "/Users/humiles/OpenClaw项目/莫大韭菜/01_原始资料/数据管道/funasr_hotwords.txt"

# 加载热词
with open(hotwords_file) as f:
    hotwords = f.read().strip()

print(f"加载热词 {len(hotwords.splitlines())} 个")

# 使用Paraformer模型 - hub=modelscope
model = AutoModel(
    model="paraformer-large",
    hub="modelscope",
    model_revision="v2.0.4",
    device="cpu",
    disable_update=True,
    ncpu=4,
)

# 测试音频
audio_file = "/Users/humiles/OpenClaw项目/莫大韭菜/01_原始资料/B站音频/2021年总结及展望，降低风险偏好，关注低位疫情受损股、北京房产.mp3"

print(f"开始转写: {audio_file}")

# 转写
result = model.generate(
    input=audio_file,
    batch_size_s=300,
    merge_vad=True,
    merge_length_stridem=1000,
)

print("转写结果:")
print(result[0]["text"])