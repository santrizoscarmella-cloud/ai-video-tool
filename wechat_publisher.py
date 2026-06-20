"""
微信公众号发布模块
"""
import json
import requests
from datetime import datetime

from config import WECHAT_APP_ID, WECHAT_APP_SECRET


def _get_access_token() -> str:
    """获取微信公众号的 access_token"""
    if not WECHAT_APP_ID or not WECHAT_APP_SECRET:
        raise ValueError("请先在 config.py 中配置 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
    
    url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": WECHAT_APP_ID,
        "secret": WECHAT_APP_SECRET,
    }
    
    response = requests.get(url, params=params, timeout=10)
    if response.status_code != 200:
        raise Exception(f"获取 access_token 失败: {response.status_code}")
    
    data = response.json()
    if "access_token" not in data:
        raise Exception(f"获取 access_token 失败: {data.get('errmsg', '未知错误')}")
    
    return data["access_token"]


def upload_image(token: str, image_path: str) -> str | None:
    """上传图片到微信公众号素材库，返回 media_id"""
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
    try:
        with open(image_path, "rb") as f:
            files = {"media": f}
            response = requests.post(url, files=files, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data.get("media_id")
    except Exception as e:
        print(f"图片上传失败: {e}")
    return None


def create_draft(article_data: dict) -> dict:
    """
    创建公众号草稿
    article_data 格式:
    {
        "title": "标题",
        "author": "作者",
        "content": "正文(HTML)",
        "digest": "摘要",
        "thumb_media_id": "封面图片 media_id（可选）"
    }
    返回: {"success": True/False, "media_id": "xxx", "message": "提示信息"}
    """
    try:
        token = _get_access_token()
        url = "https://api.weixin.qq.com/cgi-bin/draft/add"
        
        body = {
            "articles": [
                {
                    "title": article_data.get("title", "好物推荐"),
                    "author": article_data.get("author", "好物推荐官"),
                    "content": article_data.get("content", ""),
                    "digest": article_data.get("digest", ""),
                    "need_open_comment": 1,
                    "only_fans_can_comment": 0,
                }
            ]
        }
        
        # 如果有封面图 media_id
        thumb = article_data.get("thumb_media_id")
        if thumb:
            body["articles"][0]["thumb_media_id"] = thumb
        
        response = requests.post(
            f"{url}?access_token={token}",
            json=body,
            timeout=30,
        )
        
        result = response.json()
        if "media_id" in result:
            return {
                "success": True,
                "media_id": result["media_id"],
                "message": "草稿创建成功！可在公众号后台「草稿箱」中查看并发布。",
            }
        else:
            return {
                "success": False,
                "media_id": None,
                "message": f"草稿创建失败: {result.get('errmsg', '未知错误')}",
            }
            
    except ValueError as e:
        return {"success": False, "media_id": None, "message": str(e)}
    except Exception as e:
        return {"success": False, "media_id": None, "message": f"发布失败: {str(e)}"}


def preview_article(article_data: dict, wechat_id: str) -> dict:
    """
    发送预览到指定微信号
    """
    try:
        token = _get_access_token()
        url = "https://api.weixin.qq.com/cgi-bin/message/preview"
        
        # 需要先创建草稿获取 media_id
        draft = create_draft(article_data)
        if not draft["success"]:
            return draft
        
        payload = {
            "touser": wechat_id,
            "mpnews": {
                "media_id": draft["media_id"],
            },
            "msgtype": "mpnews",
        }
        
        response = requests.post(
            f"{url}?access_token={token}",
            json=payload,
            timeout=10,
        )
        
        result = response.json()
        if result.get("errcode") == 0:
            return {"success": True, "message": f"预览已发送到 {wechat_id}，请在微信中查看。"}
        else:
            return {"success": False, "message": f"预览发送失败: {result.get('errmsg')}"}
            
    except ValueError as e:
        return {"success": False, "message": str(e)}
    except Exception as e:
        return {"success": False, "message": f"预览失败: {str(e)}"}
