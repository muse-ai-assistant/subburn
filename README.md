# subburn

Burn subtitles into your video (hardsub) or mux them as a switchable track (softsub) — one command.

Pairs perfectly with [autosub](https://github.com/muse-ai-assistant/autosub): generate subtitles with autosub, then burn them in with subburn. A complete "transcribe → burn" workflow.

## Install

Pure Python standard library — no `pip install` needed:

```bash
pip install -r requirements.txt   # nothing to install, stdlib only
```

You do need **ffmpeg** (with libass, which official builds include):

| Platform | Command |
|---|---|
| Windows | `winget install Gyan.FFmpeg` or download from https://www.gyan.dev/ffmpeg/builds/ |
| macOS | `brew install ffmpeg` |
| Ubuntu/Debian | `sudo apt install ffmpeg` |
| Fedora | `sudo dnf install ffmpeg` |

## Usage

```bash
# Hard burn: render subtitles permanently into the picture (default)
subburn video.mp4 sub.srt -o out.mp4

# Soft mux: add subtitle as a separate track, no re-encode (fast)
subburn video.mp4 sub.srt --soft -o out.mkv

# Bigger text on top of the screen
subburn video.mp4 sub.srt --fontsize 32 --style top -o out.mp4

# Custom font
subburn video.mp4 sub.srt --font /path/to/font.ttf -o out.mp4

# Higher quality re-encode (lower CRF = better)
subburn video.mp4 sub.srt --crf 18 -o out.mp4
```

## Hardsub vs Softsub

| | Hardsub (default) | Softsub (`--soft`) |
|---|---|---|
| Result | Text baked into pixels | Separate subtitle track |
| Speed | Slow (re-encodes video) | Fast (stream copy) |
| Toggleable | No | Yes, in any player |
| Container | Any | `.mp4/.m4v` (mov_text) or `.mkv` (srt) |
| Styling | `--font` / `--fontsize` / `--style` | Player decides |

Use hardsub when the video must show subtitles everywhere (social feeds, sharing). Use softsub when you want to keep the original quality and let viewers toggle.

---

# subburn

把字幕烧进视频（硬字幕）或封装成可开关的字幕轨道（软字幕），一条命令搞定。

和 [autosub](https://github.com/muse-ai-assistant/autosub) 是绝配：autosub 生成字幕，subburn 压进视频，"识别 → 压制"一条龙。

## 安装

纯 Python 标准库，无需安装依赖：

```bash
pip install -r requirements.txt   # 什么都不装，标准库就够了
```

但需要系统装 **ffmpeg**（官方构建自带 libass）：

| 平台 | 命令 |
|---|---|
| Windows | `winget install Gyan.FFmpeg` 或去 https://www.gyan.dev/ffmpeg/builds/ 下载 |
| macOS | `brew install ffmpeg` |
| Ubuntu/Debian | `sudo apt install ffmpeg` |
| Fedora | `sudo dnf install ffmpeg` |

## 用法

```bash
# 硬字幕：把字幕永久烧进画面（默认）
subburn video.mp4 sub.srt -o out.mp4

# 软字幕：封装成独立轨道，不重新编码（快）
subburn video.mp4 sub.srt --soft -o out.mkv

# 大字号放顶部
subburn video.mp4 sub.srt --fontsize 32 --style top -o out.mp4

# 自定义字体
subburn video.mp4 sub.srt --font /path/to/font.ttf -o out.mp4

# 更高画质（CRF 越小越好）
subburn video.mp4 sub.srt --crf 18 -o out.mp4
```

## 硬字幕 vs 软字幕

| | 硬字幕（默认） | 软字幕（`--soft`） |
|---|---|---|
| 效果 | 字烧死在画面里 | 独立字幕轨道 |
| 速度 | 慢（要重新编码） | 快（直接复制流） |
| 可开关 | 不可 | 播放器里可开关 |
| 容器 | 任意 | `.mp4/.m4v`（mov_text）或 `.mkv`（srt） |
| 样式 | `--font` / `--fontsize` / `--style` | 由播放器决定 |

发社交平台、到处分享 → 用硬字幕；保留原画质、想让观众自己开关 → 用软字幕。

## License

MIT
