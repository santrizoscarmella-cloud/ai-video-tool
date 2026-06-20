"""
AI 智能模块 - 视频分析 + 文案生成 + 公众号文章
"""
import json
import requests
from datetime import datetime

from config import AI_API_KEY, AI_API_URL, AI_MODEL


def _call_ai_api(messages: list, temperature: float = 0.7) -> str:
    """调用 AI API（OpenAI 兼容格式）"""
    if not AI_API_KEY:
        raise ValueError("请先在 config.py 中配置 AI_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": AI_MODEL,
        "messages": messages,
        "temperature": temperature,
    }
    
    response = requests.post(
        f"{AI_API_URL.rstrip('/')}/chat/completions",
        headers=headers,
        json=payload,
        timeout=120,
    )
    
    if response.status_code != 200:
        raise Exception(f"AI API 调用失败: {response.status_code} - {response.text}")
    
    result = response.json()
    return result["choices"][0]["message"]["content"]


def analyze_video_for_product(
    video_title: str,
    video_description: str,
    platform: str,
    duration_text: str,
) -> dict:
    """
    分析视频内容，提取产品信息
    返回结构化结果
    """
    prompt = f"""你是一个专业的带货视频分析专家。请分析以下带货视频信息，提取关键内容。

【视频信息】
- 标题：{video_title}
- 平台：{platform}
- 时长：{duration_text}
- 简介：{video_description}

请从以下维度分析，以 JSON 格式返回（只返回 JSON，不要其他文字）：

{{
    "product_name": "产品名称或推测的产品名称",
    "product_category": "产品类别（如：美妆、食品、电子产品、家居、服饰、母婴等）",
    "product_features": ["卖点1", "卖点2", "卖点3", ...],
    "target_audience": "目标人群（如：职场女性、学生、宝妈、健身人群等）",
    "pain_points": ["解决的用户痛点1", "痛点2", ...],
    "video_style": "视频风格（如：测评对比、开箱展示、场景演绎、知识科普、素人推荐等）",
    "key_conclusion": "视频传达的核心观点或结论",
    "confidence": "对产品判断的信心指数（0-1之间的数字，数值越高表示信息越确定）"
}}
"""
    try:
        result = _call_ai_api([
            {"role": "system", "content": "你是一个专业的带货分析师，擅长从视频中提取产品信息。"},
            {"role": "user", "content": prompt},
        ], temperature=0.3)
        
        # 清理返回内容，只取 JSON 部分
        result = result.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[1]
            result = result.rsplit("```", 1)[0]
        result = result.strip()
        
        return json.loads(result)
    except Exception as e:
        return {
            "product_name": "分析失败",
            "error": str(e),
        }


def generate_sales_copy(product_info: dict, platform: str = "微信公众号") -> dict:
    """
    根据产品分析结果生成带货文案
    返回标题 + 正文 + 行动号召
    """
    info_json = json.dumps(product_info, ensure_ascii=False, indent=2)
    
    prompt = f"""你是一个顶级的带货文案写手。根据以下分析数据，生成一篇在 {platform} 发布的高转化率带货推文。

【产品分析数据】
{info_json}

要求：
1. 标题要吸引点击，可以使用数字、悬念、痛点等技巧
2. 正文结构：开头种草 → 痛点共情 → 产品亮点 → 真实体验 → 行动号召
3. 语言风格：真实、可信、不做作，就像朋友推荐
4. 合理使用 emoji 增加可读性
5. 结尾加上购买引导

以以下 JSON 格式返回（只返回 JSON，不要其他文字）：

{{
    "title": "推文标题",
    "subtitle": "推文副标题（可选）或空字符串",
    "body": "完整的推文正文（纯文本，包含 emoji，不需要 markdown 格式）",
    "highlights": ["亮点1", "亮点2", "亮点3"],
    "call_to_action": "行动号召用语",
    "hashtags": ["#标签1", "#标签2", "#标签3"]
}}
"""
    try:
        result = _call_ai_api([
            {"role": "system", "content": "你是一个顶级的带货文案专家。"},
            {"role": "user", "content": prompt},
        ], temperature=0.7)
        
        result = result.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[1]
            result = result.rsplit("```", 1)[0]
        result = result.strip()
        
        return json.loads(result)
    except Exception as e:
        return {
            "title": "带货文案生成失败",
            "body": f"生成过程中出现错误: {str(e)}",
        }


def format_wechat_article(sales_copy: dict, product_name: str) -> dict:
    """
    将带货文案格式化为微信公众号文章
    返回包含标题、作者、正文的 dict
    """
    body = sales_copy.get("body", "")
    highlights = sales_copy.get("highlights", [])
    call_to_action = sales_copy.get("call_to_action", "")
    hashtags = sales_copy.get("hashtags", [])
    
    # 构建 HTML 正文
    html_parts = []
    
    # 副标题
    subtitle = sales_copy.get("subtitle", "")
    if subtitle:
        html_parts.append(f'<p style="color:#888;font-size:16px;margin-bottom:20px;">{subtitle}</p>')
    
    # 正文（分段）
    paragraphs = body.split("\n\n") if "\n\n" in body else body.split("\n")
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        # 跳过只包含 emoji 或短句的，作为分隔
        if len(p) < 3:
            continue
        html_parts.append(f"<p>{p}</p>")
    
    # 亮点列表
    if highlights:
        html_parts.append('<div style="background:#f8f9fa;padding:15px;border-radius:8px;margin:20px 0;">')
        html_parts.append('<p style="font-weight:bold;font-size:16px;">🌟 为什么值得买</p>')
        html_parts.append("<ul>")
        for h in highlights:
            html_parts.append(f"<li>{h}</li>")
        html_parts.append("</ul></div>")
    
    # 行动号召
    if call_to_action:
        html_parts.append(
            f'<div style="background:linear-gradient(135deg,#ff6b6b,#ee5a24);color:white;'
            f'text-align:center;padding:15px;border-radius:8px;margin:20px 0;font-size:18px;font-weight:bold;">'
            f'{call_to_action}</div>'
        )
    
    # 标签
    if hashtags:
        tags_html = " ".join([
            f'<span style="display:inline-block;background:#e8f4fd;color:#2d8cf0;'
            f'padding:3px 10px;border-radius:12px;font-size:13px;margin:3px;">{tag}</span>'
            for tag in hashtags
        ])
        html_parts.append(f'<p style="margin-top:20px;">{tags_html}</p>')
    
    # 日期
    today = datetime.now().strftime("%Y年%m月%d日")
    html_parts.append(f'<p style="color:#999;font-size:13px;margin-top:15px;">发布于 {today}</p>')
    
    return {
        "title": sales_copy.get("title", f"好物推荐 | {product_name}"),
        "author": "好物推荐官",
        "content": "\n".join(html_parts),
        "digest": body[:120] if len(body) > 120 else body,
    }
