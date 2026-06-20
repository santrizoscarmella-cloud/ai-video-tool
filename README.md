# 🎬 AI 带货视频工具

## 这是什么？

**输入带货视频链接 → AI 自动分析 → 生成公众号推文 → 一键发布**

帮你把抖音/B站/YouTube 上的带货视频，快速变成你自己的公众号文章。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API

打开 `config.py`，填入以下信息：

#### AI API（二选一）

**推荐 DeepSeek**（便宜，1 块钱能生成几百篇文章）：
1. 注册 https://platform.deepseek.com
2. 创建 API Key
3. 填入 `AI_API_KEY`

或者用 OpenAI / 通义千问 等任何兼容 OpenAI 格式的 API。

#### 微信公众号（可选，不配置也可以预览文案）
1. 登录公众号后台 → 开发 → 基本配置
2. 获取 AppID 和 AppSecret
3. 填入 `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET`

### 3. 启动工具

```bash
streamlit run app.py
```

浏览器会自动打开 http://localhost:8501

### 4. 开始使用

1. 粘贴带货视频链接
2. 点击「开始 AI 分析」
3. 查看分析结果
4. 点击「生成带货推文」
5. 预览文案，满意后发布到公众号

## 文件说明

```
ai-video-tool/
├── app.py              # 主程序（Streamlit 界面）
├── config.py           # 配置文件（API Key 等）
├── ai_utils.py         # AI 智能模块
├── video_utils.py      # 视频下载与处理
├── wechat_publisher.py # 公众号发布
├── requirements.txt    # Python 依赖
├── README.md           # 本文件
└── downloads/          # 下载的视频（自动创建）
```

## 技术栈

- **前端/界面**：Streamlit
- **视频处理**：yt-dlp
- **AI 模型**：DeepSeek / OpenAI 兼容 API
- **公众号对接**：微信公众平台 API
- **语言**：Python

## 注意事项

- AI 分析基于视频标题和描述，准确度取决于视频信息质量
- 首次使用建议先预览文案，不满意可以重新生成
- 发布到公众号后，记得在后台配图和调整格式
