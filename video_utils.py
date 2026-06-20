"""
视频下载与处理模块
"""
import os
import re
import json
import subprocess
from pathlib import Path
from urllib.parse import urlparse
import yt_dlp


def is_video_url(url: str) -> bool:
    """检查是否为有效的视频 URL"""
    if not url or not url.strip():
        return False
    url = url.strip()
    # 支持的平台
    supported_domains = [
        "youtube.com", "youtu.be",
        "bilibili.com", "b23.tv",
        "douyin.com", "iesdouyin.com",
        "kuaishou.com",
        "weibo.com",
        "xiaohongshu.com",
        "v.qq.com", "v.youku.com", "v.xigua.com",
    ]
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        for d in supported_domains:
            if d in domain:
                return True
        # 如果不是已知平台，也认为可能是其它视频链接
        return True
    except:
        return False


def get_platform_name(url: str) -> str:
    """从 URL 判断视频平台"""
    url = url.lower()
    if "youtube.com" in url or "youtu.be" in url:
        return "YouTube"
    elif "bilibili.com" in url or "b23.tv" in url:
        return "B站"
    elif "douyin.com" in url or "iesdouyin.com" in url:
        return "抖音"
    elif "kuaishou.com" in url:
        return "快手"
    elif "weibo.com" in url:
        return "微博"
    elif "xiaohongshu.com" in url:
        return "小红书"
    elif "v.qq.com" in url:
        return "腾讯视频"
    elif "v.youku.com" in url:
        return "优酷"
    elif "v.xigua.com" in url:
        return "西瓜视频"
    else:
        return "其他平台"


def download_video(url: str, output_dir: str = "downloads") -> str | None:
    """
    下载视频，返回本地文件路径
    如果下载失败，返回 None
    """
    os.makedirs(output_dir, exist_ok=True)
    
    ydl_opts = {
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # 修正文件名（可能是 webm/mkv 等格式）
            base = os.path.splitext(filename)[0]
            mp4_path = f"{base}.mp4"
            
            # 如果 mp4 已存在就直接返回
            if os.path.exists(mp4_path):
                return mp4_path
            
            # 查找目录下刚刚下载的文件
            output_dir_path = Path(output_dir)
            video_files = list(output_dir_path.glob(f"{Path(filename).stem}.*"))
            if video_files:
                return str(video_files[0])
            
            return mp4_path
    except Exception as e:
        raise Exception(f"视频下载失败: {str(e)}")


def extract_video_info(url: str) -> dict:
    """提取视频基本信息（不下载）"""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title", "未知标题"),
                "description": info.get("description", "")[:500] if info.get("description") else "",
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader", "未知作者"),
                "view_count": info.get("view_count", 0),
                "like_count": info.get("like_count", 0),
                "tags": info.get("tags", []),
                "categories": info.get("categories", []),
            }
    except Exception as e:
        return {"title": "无法获取视频信息", "error": str(e)}


def format_duration(seconds: int) -> str:
    """将秒数格式化为 时:分:秒"""
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"
