"""
AI 带货视频工具 - 主程序
=========================
运行方式：streamlit run app.py
"""
import os
import json
import sys
from datetime import datetime

import streamlit as st

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from video_utils import (
    is_video_url,
    get_platform_name,
    download_video,
    extract_video_info,
    format_duration,
)
from ai_utils import (
    analyze_video_for_product,
    generate_sales_copy,
    format_wechat_article,
)
from wechat_publisher import create_draft, preview_article

# ======================== 页面配置 ========================
st.set_page_config(
    page_title="AI 带货视频工具",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ======================== 样式 ========================
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .step-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 4px solid #ff6b6b;
    }
    .success-card {
        background: #d4edda;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 4px solid #28a745;
    }
    .info-card {
        background: #e8f4fd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ======================== 侧边栏 ========================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/youtube--v1.png", width=60)
    st.markdown("## 🎬 AI 带货视频工具")
    st.markdown("---")
    
    st.markdown("### 💡 使用流程")
    st.markdown("""
    1. **粘贴视频链接**
    2. **AI 分析视频**
    3. **生成带货文案**
    4. **发布到公众号**
    """)
    
    st.markdown("---")
    st.markdown("### 📋 配置检查")
    
    from config import (
        AI_API_KEY, AI_API_URL, AI_MODEL,
        WECHAT_APP_ID, WECHAT_APP_SECRET,
    )
    
    api_ok = bool(AI_API_KEY)
    wechat_ok = bool(WECHAT_APP_ID) and bool(WECHAT_APP_SECRET)
    
    col1, col2 = st.columns(2)
    with col1:
        if api_ok:
            st.success("✅ AI 已配置")
        else:
            st.error("❌ 未配置 AI")
    with col2:
        if wechat_ok:
            st.success("✅ 公众号已配置")
        else:
            st.info("⚙️ 未配置公众号")
    
    if not api_ok or not wechat_ok:
        st.markdown("---")
        with st.expander("📝 如何配置"):
            st.markdown("""
            打开 `config.py` 文件，填入以下信息：
            
            **AI API 配置**（推荐 DeepSeek）：
            - 注册 [DeepSeek](https://platform.deepseek.com)
            - 创建 API Key
            - 填入 `AI_API_KEY`
            
            **微信公众号配置**：
            - 登录微信公众号后台
            - 开发 → 基本配置
            - 获取 AppID 和 AppSecret
            """)

# ======================== 主界面 ========================
st.markdown('<div class="main-header">🎬 AI 带货视频 → 公众号文章</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">粘贴带货视频链接，AI 自动分析并生成公众号推文，一键发布</div>',
    unsafe_allow_html=True,
)

# ======================== 步骤 1：输入视频 ========================
st.markdown("---")
st.markdown("### 📌 第一步：粘贴带货视频链接")
st.markdown("支持：YouTube / B站 / 抖音 / 小红书 / 快手 / 微博 等主流平台")

url = st.text_input(
    "视频链接",
    placeholder="例如：https://www.douyin.com/video/xxxxxxxxx",
    label_visibility="collapsed",
)

# ======================== 步骤 2：分析视频 ========================
if url and is_video_url(url):
    platform = get_platform_name(url)
    
    # 显示视频基本信息
    with st.spinner("🔍 正在获取视频信息..."):
        try:
            video_info = extract_video_info(url)
            st.markdown(
                f'<div class="info-card">'
                f'🎬 **来源平台**：{platform}<br>'
                f'📺 **标题**：{video_info.get("title", "未知")}<br>'
                f'⏱ **时长**：{format_duration(video_info.get("duration", 0))}'
                f'</div>',
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.warning(f"获取视频详情失败（不影响后续分析）: {str(e)}")
            video_info = {"title": url, "description": ""}
    
    # 分析按钮
    st.markdown("---")
    st.markdown("### 🤖 第二步：AI 智能分析")
    st.markdown("AI 会自动分析视频内容，提取产品信息和卖点")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_btn = st.button("🚀 开始 AI 分析", type="primary", use_container_width=True)
    
    if analyze_btn:
        # AI 分析视频
        with st.spinner("🧠 AI 正在分析视频内容，这可能需要 10-30 秒..."):
            try:
                product_analysis = analyze_video_for_product(
                    video_title=video_info.get("title", url),
                    video_description=video_info.get("description", ""),
                    platform=platform,
                    duration_text=format_duration(video_info.get("duration", 0)),
                )
                
                st.session_state["product_analysis"] = product_analysis
                st.session_state["video_url"] = url
                st.session_state["video_info"] = video_info
                st.session_state["platform"] = platform
                
            except Exception as e:
                st.error(f"❌ AI 分析失败: {str(e)}")
                st.stop()
        
        # 显示分析结果
        if "product_analysis" in st.session_state:
            pa = st.session_state["product_analysis"]
            
            if "error" in pa:
                st.error(f"分析失败: {pa.get('error', '未知错误')}")
                st.stop()
            
            st.success("✅ AI 分析完成！")
            
            with st.expander("📊 查看详细分析结果", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**产品名称**：{pa.get('product_name', '未知')}")
                    st.markdown(f"**产品类别**：{pa.get('product_category', '未知')}")
                    st.markdown(f"**目标人群**：{pa.get('target_audience', '未知')}")
                    if pa.get("confidence"):
                        score = pa["confidence"]
                        stars = "⭐" * int(score * 5)
                        st.markdown(f"**分析可信度**：{stars} ({score:.0%})")
                
                with col2:
                    st.markdown("**核心卖点**：")
                    for f in pa.get("product_features", []):
                        st.markdown(f"- ✅ {f}")
                    
                    st.markdown("**用户痛点**：")
                    for p in pa.get("pain_points", []):
                        st.markdown(f"- 💡 {p}")
                
                st.markdown(f"**视频风格**：{pa.get('video_style', '未知')}")
                st.markdown(f"**核心观点**：{pa.get('key_conclusion', '未知')}")
            
            # ======================== 步骤 3：生成文案 ========================
            st.markdown("---")
            st.markdown("### ✍️ 第三步：生成带货文案")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                generate_btn = st.button(
                    "📝 生成带货推文", 
                    type="primary", 
                    use_container_width=True,
                )
            
            if generate_btn:
                with st.spinner("✍️ AI 正在撰写带货文案..."):
                    try:
                        sales_copy = generate_sales_copy(pa)
                        st.session_state["sales_copy"] = sales_copy
                        
                        article = format_wechat_article(
                            sales_copy, 
                            pa.get("product_name", "好物"),
                        )
                        st.session_state["article"] = article
                        
                    except Exception as e:
                        st.error(f"❌ 文案生成失败: {str(e)}")
                        st.stop()
                
                if "sales_copy" in st.session_state:
                    sc = st.session_state["sales_copy"]
                    art = st.session_state["article"]
                    
                    st.success("✅ 文案生成成功！")
                    
                    # 标题预览
                    st.markdown(f"## 📰 `{art['title']}`")
                    
                    # 正文预览
                    st.markdown("### 正文预览")
                    st.markdown(
                        f'<div style="background:white;padding:20px;border:1px solid #ddd;'
                        f'border-radius:8px;max-height:400px;overflow-y:auto;">'
                        f'{art["content"]}</div>',
                        unsafe_allow_html=True,
                    )
                    
                    # 亮点
                    if sc.get("highlights"):
                        st.markdown("### 🌟 文章亮点")
                        for h in sc["highlights"]:
                            st.markdown(f"- {h}")
                    
                    # 行动号召
                    if sc.get("call_to_action"):
                        st.markdown(f"### 🎯 行动号召\n{sc['call_to_action']}")
                    
                    # 标签
                    if sc.get("hashtags"):
                        st.markdown("### 🏷️ 推荐标签\n" + " ".join(sc["hashtags"]))
                    
                    # ======================== 步骤 4：发布 ========================
                    st.markdown("---")
                    st.markdown("### 📤 第四步：发布到微信公众号")
                    
                    publish_tab, preview_tab = st.tabs(["📢 发布草稿", "👁️ 发送预览"])
                    
                    with publish_tab:
                        st.info(
                            "发布后，文章会出现在公众号后台的「草稿箱」中，"
                            "你可以在后台编辑、配图后再正式群发。"
                        )
                        
                        if st.button("📤 创建公众号草稿", type="primary", use_container_width=True):
                            with st.spinner("正在发布到公众号..."):
                                try:
                                    result = create_draft(art)
                                    if result["success"]:
                                        st.success(f"✅ {result['message']}")
                                    else:
                                        st.warning(f"ℹ️ {result['message']}")
                                except Exception as e:
                                    st.error(f"❌ 发布失败: {str(e)}")
                    
                    with preview_tab:
                        st.markdown("发送预览到你的个人微信号，先看效果再发布")
                        wechat_id = st.text_input(
                            "你的微信号",
                            placeholder="填写你的微信号",
                            key="wechat_id_input",
                        )
                        
                        if st.button("📲 发送预览", use_container_width=True):
                            if not wechat_id:
                                st.warning("请先输入你的微信号")
                            else:
                                with st.spinner("正在发送预览..."):
                                    try:
                                        result = preview_article(art, wechat_id)
                                        if result["success"]:
                                            st.success(f"✅ {result['message']}")
                                        else:
                                            st.warning(f"ℹ️ {result['message']}")
                                    except Exception as e:
                                        st.error(f"❌ 预览发送失败: {str(e)}")
        
        # 重新生成文案的按钮
        if "article" in st.session_state:
            st.markdown("---")
            if st.button("🔄 不满意？重新生成文案", use_container_width=True):
                for key in ["sales_copy", "article"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.info("已清除当前文案，请重新点击「生成带货推文」")
                st.rerun()

else:
    # 未输入链接时显示引导
    st.markdown("""
    <div style="text-align:center;padding:40px 20px;color:#888;">
        <div style="font-size:48px;margin-bottom:20px;">🔗</div>
        <div style="font-size:18px;">在上方输入框粘贴带货视频链接，开始 AI 分析</div>
        <div style="font-size:14px;margin-top:10px;">
            支持：抖音 / B站 / YouTube / 小红书 / 快手 / 微博 / 淘宝直播 等
        </div>
    </div>
    """, unsafe_allow_html=True)

# ======================== 页脚 ========================
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#999;font-size:13px;padding:10px;">'
    'AI 带货视频工具 v1.0 | 数据仅供本地处理，不会上传到第三方服务器'
    '</div>',
    unsafe_allow_html=True,
)
