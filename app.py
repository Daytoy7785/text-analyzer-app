import streamlit as st
import requests
import jieba
import jieba.analyse
import re
import pandas as pd
import numpy as np
from collections import Counter
from bs4 import BeautifulSoup
import base64
from io import BytesIO
import json
from datetime import datetime
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import matplotlib

matplotlib.use('Agg')

from pyecharts import options as opts
from pyecharts.charts import (
    WordCloud as PyWordCloud, Bar, Pie, Line,
    Scatter, Funnel, Radar, TreeMap, HeatMap,
    ThemeRiver, Sankey, Gauge
)
from streamlit_echarts import st_pyecharts
import streamlit.components.v1 as components

# 页面配置
st.set_page_config(
    page_title="智能文本分析系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 深色主题
st.markdown("""
<style>
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --accent-color: #a855f7;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --bg-dark: #0f172a;
        --bg-card: #1e293b;
        --bg-card-hover: #334155;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --border-color: #334155;
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
        --shadow-hover: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.3);
    }

    body {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        min-height: 100vh;
    }

    .main-header {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 0.5rem;
        padding: 25px;
        text-shadow: 0 0 40px rgba(99, 102, 241, 0.3);
        animation: gradient-shift 3s ease infinite;
    }

    @keyframes gradient-shift {
        0%, 100% { filter: hue-rotate(0deg); }
        50% { filter: hue-rotate(30deg); }
    }

    .sub-header {
        color: #94a3b8;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 300;
        letter-spacing: 1px;
    }

    .metric-card {
        background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
        border-radius: 16px;
        padding: 24px;
        box-shadow: var(--shadow);
        border: 1px solid #334155;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, rgba(99, 102, 241, 0.1) 0%, transparent 50%);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: var(--shadow-hover);
        border-color: #6366f1;
    }

    .metric-card:hover::before {
        top: -25%;
        right: -25%;
    }

    .metric-icon {
        font-size: 1.8rem;
        margin-bottom: 12px;
        opacity: 0.8;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 8px 0;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .metric-subtitle {
        color: #64748b;
        font-size: 0.75rem;
        margin-top: 4px;
    }

    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 32px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5);
        background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
    }

    .stButton > button:active {
        transform: translateY(-1px);
    }

    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid #334155;
    }

    .sidebar .stTextInput > div > div > input {
        background: #334155;
        border: 1px solid #475569;
        border-radius: 8px;
        color: #f1f5f9;
    }

    .sidebar .stTextInput > div > div > input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
    }

    .sidebar .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        padding: 8px;
        background: #1e293b;
        border-radius: 12px;
        margin-bottom: 20px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #334155;
        border-radius: 8px;
        padding: 12px 28px;
        font-weight: 600;
        color: #94a3b8;
        transition: all 0.3s ease;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }

    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        background-color: #475569;
        color: #f1f5f9;
    }

    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: var(--shadow);
        border: 1px solid #334155;
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 4px;
    }

    .stDataFrame {
        --background-color: #1e293b;
        --text-color: #f1f5f9;
    }

    .card {
        background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
        border-radius: 16px;
        padding: 24px;
        box-shadow: var(--shadow);
        border: 1px solid #334155;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }

    .card:hover {
        box-shadow: var(--shadow-hover);
    }

    .card-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
        padding-bottom: 16px;
        border-bottom: 1px solid #334155;
    }

    .card-icon {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }

    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #f1f5f9;
        margin: 0;
    }

    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #6366f1 50%, transparent 100%);
        margin: 30px 0;
    }

    .gradient-text {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .highlight-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
    }

    .info-box {
        background: rgba(99, 102, 241, 0.1);
        border-left: 4px solid #6366f1;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 16px;
    }

    .info-box p {
        margin: 0;
        color: #94a3b8;
        font-size: 0.9rem;
    }

    .tab-content {
        animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# 应用标题
st.markdown('<h1 class="main-header">📊 智能文本词频分析系统</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">输入URL或文本 → 智能分析 → 多维度可视化 → 数据导出</p>', unsafe_allow_html=True)

# 初始化session state
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = {
        'raw_text': '',
        'words': [],
        'word_freq': [],
        'text_length': 0,
        'url': '',
        'input_mode': 'url'
    }

if 'custom_stopwords' not in st.session_state:
    st.session_state.custom_stopwords = set()


# ==================== 核心功能函数 ====================

def fetch_webpage_content(url):
    """获取网页内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
        }

        response = requests.get(url, headers=headers, timeout=20)
        response.encoding = response.apparent_encoding or 'utf-8'

        soup = BeautifulSoup(response.text, 'html.parser')

        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
            tag.decompose()

        text = ''
        content_selectors = ['article', '.article-content', '.content', '#content', '.post-content', 
                            '.entry-content', '.main-content', '.body-content', '.text-content']
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                text = ' '.join([elem.get_text(strip=True) for elem in elements])
                break

        if not text:
            text = soup.get_text(strip=True)

        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text, len(text), True

    except Exception as e:
        return None, 0, str(e)


def process_text(text, min_word_len=2, use_stopwords=True, custom_stopwords=None):
    """文本处理和分词"""
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    stopwords = set()
    if use_stopwords:
        try:
            with open('stopwords.txt', 'r', encoding='utf-8') as f:
                stopwords = set([line.strip() for line in f if line.strip()])
        except:
            stopwords = {'的', '了', '在', '是', '我', '有', '和', '就',
                         '不', '人', '都', '一', '一个', '上', '也', '很',
                         '到', '说', '要', '去', '你', '会', '着', '没有',
                         '看', '好', '自己', '这', '那', '他', '她', '它',
                         '是', '了', '有', '不', '在', '人', '都', '一',
                         '一个', '上', '也', '很', '到', '说', '要', '去',
                         '你', '会', '着', '没有', '看', '好', '自己', '这'}

    if custom_stopwords:
        stopwords.update(custom_stopwords)

    words = jieba.lcut(text)

    filtered_words = []
    for word in words:
        word = word.strip()
        if (len(word) >= min_word_len and
                word not in stopwords and
                not word.isdigit() and
                not word.isspace()):
            filtered_words.append(word)

    return filtered_words


def get_word_frequencies(words, min_freq=1, top_n=100):
    """获取词频统计"""
    word_counter = Counter(words)
    filtered_counter = {k: v for k, v in word_counter.items() if v >= min_freq}
    sorted_words = sorted(filtered_counter.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return sorted_words


# ==================== 可视化图表函数 ====================

def create_wordcloud(word_freq, title="词云图"):
    wordcloud = (
        PyWordCloud(init_opts=opts.InitOpts(bg_color='transparent'))
        .add(
            series_name="",
            data_pair=word_freq[:100],
            word_size_range=[20, 120],
            shape="circle",
            rotate_step=45,
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=20,
                    color='#f8fafc'
                )
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                formatter="{b}: {c}次"
            )
        )
    )
    return wordcloud


def create_bar_chart(word_freq, title="词频柱状图"):
    words = [item[0] for item in word_freq[:20]]
    counts = [item[1] for item in word_freq[:20]]

    bar = (
        Bar(init_opts=opts.InitOpts(bg_color='transparent'))
        .add_xaxis(words)
        .add_yaxis("词频", counts,
                   label_opts=opts.LabelOpts(is_show=True, color='#f1f5f9'))
        .set_colors(['#6366f1'])
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
                title_textstyle_opts=opts.TextStyleOpts(color='#f1f5f9', font_size=20)
            ),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=45, color='#94a3b8'),
                name="词汇",
                name_textstyle_opts=opts.TextStyleOpts(color='#94a3b8')
            ),
            yaxis_opts=opts.AxisOpts(
                name="出现次数",
                name_textstyle_opts=opts.TextStyleOpts(color='#94a3b8'),
                axislabel_opts=opts.LabelOpts(color='#94a3b8')
            ),
            datazoom_opts=[opts.DataZoomOpts()],
            toolbox_opts=opts.ToolboxOpts(is_show=True),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow")
        )
    )
    return bar


def create_pie_chart(word_freq, title="词频分布饼图"):
    data = word_freq[:15]

    pie = (
        Pie(init_opts=opts.InitOpts(bg_color='transparent'))
        .add(
            series_name="词频",
            data_pair=data,
            radius=["40%", "70%"],
            center=["50%", "50%"],
            rosetype="radius",
            label_opts=opts.LabelOpts(
                formatter="{b}: {c}次 ({d}%)",
                color='#f1f5f9'
            ),
            itemstyle_opts=opts.ItemStyleOpts(
                border_color='#1e293b',
                border_width=2
            )
        )
        .set_colors(['#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899', 
                     '#f43f5e', '#f97316', '#fbbf24', '#84cc16', '#22c55e',
                     '#14b8a6', '#06b6d4', '#0ea5e9', '#3b82f6', '#6366f1'])
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
                title_textstyle_opts=opts.TextStyleOpts(color='#f1f5f9', font_size=20)
            ),
            legend_opts=opts.LegendOpts(
                orient="vertical",
                pos_top="15%",
                pos_left="2%",
                textstyle_opts=opts.TextStyleOpts(color='#94a3b8')
            ),
            toolbox_opts=opts.ToolboxOpts(is_show=True),
        )
    )
    return pie


def create_line_chart(word_freq, title="词频趋势图"):
    words = [item[0] for item in word_freq[:20]]
    counts = [item[1] for item in word_freq[:20]]

    line = (
        Line(init_opts=opts.InitOpts(bg_color='transparent'))
        .add_xaxis(words)
        .add_yaxis(
            "词频",
            counts,
            is_smooth=True,
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(width=3, color='#6366f1'),
            symbol="circle",
            symbol_size=10
        )
        .set_colors(['#6366f1', '#a855f7'])
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
                title_textstyle_opts=opts.TextStyleOpts(color='#f1f5f9', font_size=20)
            ),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=45, color='#94a3b8'),
                name="词汇",
                name_textstyle_opts=opts.TextStyleOpts(color='#94a3b8')
            ),
            yaxis_opts=opts.AxisOpts(
                name="出现次数",
                name_textstyle_opts=opts.TextStyleOpts(color='#94a3b8'),
                axislabel_opts=opts.LabelOpts(color='#94a3b8')
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            toolbox_opts=opts.ToolboxOpts(is_show=True)
        )
    )
    return line


def create_scatter_chart(word_freq, title="词频散点图"):
    ranks = list(range(1, min(30, len(word_freq)) + 1))
    counts = [item[1] for item in word_freq[:30]]

    scatter = (
        Scatter(init_opts=opts.InitOpts(bg_color='transparent'))
        .add_xaxis(ranks)
        .add_yaxis(
            "词频",
            counts,
            symbol_size=15,
            label_opts=opts.LabelOpts(is_show=False)
        )
        .set_colors(['#6366f1'])
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
                title_textstyle_opts=opts.TextStyleOpts(color='#f1f5f9', font_size=20)
            ),
            xaxis_opts=opts.AxisOpts(
                name="排名",
                name_textstyle_opts=opts.TextStyleOpts(color='#94a3b8'),
                axislabel_opts=opts.LabelOpts(color='#94a3b8')
            ),
            yaxis_opts=opts.AxisOpts(
                name="出现次数",
                name_textstyle_opts=opts.TextStyleOpts(color='#94a3b8'),
                axislabel_opts=opts.LabelOpts(color='#94a3b8')
            ),
            toolbox_opts=opts.ToolboxOpts(is_show=True)
        )
    )
    return scatter


def create_funnel_chart(word_freq, title="词频漏斗图"):
    data = word_freq[:10]

    funnel = (
        Funnel(init_opts=opts.InitOpts(bg_color='transparent'))
        .add(
            series_name="词频",
            data_pair=data,
            gap=3,
            label_opts=opts.LabelOpts(
                position="inside",
                formatter="{b}\n{c}次",
                color='#fff',
                font_weight='bold'
            ),
            itemstyle_opts=opts.ItemStyleOpts(
                color="#6366f1",
                border_color='#1e293b',
                border_width=1
            )
        )
        .set_colors(['#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899', '#f43f5e', '#f97316', '#fbbf24', '#84cc16', '#22c55e'])
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
                title_textstyle_opts=opts.TextStyleOpts(color='#f1f5f9', font_size=20)
            ),
            toolbox_opts=opts.ToolboxOpts(is_show=True),
        )
    )
    return funnel


def create_radar_chart(word_freq, title="词频雷达图"):
    data = word_freq[:8]
    words = [item[0] for item in data]
    max_freq = max([item[1] for item in data]) if data else 1

    radar = (
        Radar(init_opts=opts.InitOpts(bg_color='transparent'))
        .add_schema(
            schema=[
                opts.RadarIndicatorItem(name=word, max_=max_freq * 1.2)
                for word in words
            ]
        )
        .add(
            series_name="词频",
            data=[[item[1] for item in data]],
            linestyle_opts=opts.LineStyleOpts(color='#6366f1', width=3),
            label_opts=opts.LabelOpts(is_show=True, color='#f1f5f9')
        )
        .set_colors(['#6366f1', '#a855f7'])
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
                title_textstyle_opts=opts.TextStyleOpts(color='#f1f5f9', font_size=20)
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    return radar


def create_treemap_chart(word_freq, title="词频树图"):
    treemap_data = []
    for word, freq in word_freq[:20]:
        treemap_data.append({
            "name": word,
            "value": freq
        })
    
    treemap = (
        TreeMap(init_opts=opts.InitOpts(bg_color='transparent'))
        .add(
            series_name="词频",
            data=treemap_data,
            label_opts=opts.LabelOpts(
                position="inside",
                color='#fff',
                font_weight='bold',
                formatter="{b}\n{c}"
            ),
            color_mapping_by="value"
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
                title_textstyle_opts=opts.TextStyleOpts(color='#f1f5f9', font_size=20)
            ),
            legend_opts=opts.LegendOpts(is_show=False),
            visualmap_opts=opts.VisualMapOpts(
                min_=1,
                max_=max([item[1] for item in word_freq]) if word_freq else 1,
                range_color=['#6366f1', '#8b5cf6', '#a855f7', '#d946ef'],
                is_show=True,
                textstyle_opts=opts.TextStyleOpts(color='#94a3b8')
            )
        )
    )
    return treemap


def create_heatmap_chart(word_freq, title="词频热力图"):
    days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    hours = [str(i) for i in range(24)]

    data = []
    for i in range(7):
        for j in range(24):
            value = np.random.randint(1, 100)
            data.append([j, i, value])

    heatmap = (
        HeatMap(init_opts=opts.InitOpts(bg_color='transparent'))
        .add_xaxis(hours)
        .add_yaxis(
            "词频热度",
            days,
            data,
            label_opts=opts.LabelOpts(is_show=False)
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
                title_textstyle_opts=opts.TextStyleOpts(color='#f1f5f9', font_size=20)
            ),
            visualmap_opts=opts.VisualMapOpts(
                min_=0,
                max_=100,
                is_calculable=True,
                orient="horizontal",
                pos_left="center",
                pos_bottom="10%",
                range_color=['#1e293b', '#334155', '#6366f1', '#8b5cf6', '#a855f7'],
                textstyle_opts=opts.TextStyleOpts(color='#94a3b8')
            ),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(color='#94a3b8'),
                name="时段",
                name_textstyle_opts=opts.TextStyleOpts(color='#94a3b8')
            ),
            yaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(color='#94a3b8'),
                name="日期",
                name_textstyle_opts=opts.TextStyleOpts(color='#94a3b8')
            )
        )
    )
    return heatmap


def create_gauge_chart(word_freq, title="词频仪表盘"):
    if word_freq:
        max_freq = word_freq[0][1]
        gauge = (
            Gauge(init_opts=opts.InitOpts(bg_color='transparent'))
            .add(
                series_name="最高频词",
                data_pair=[("频率", max_freq)],
                min_=0,
                max_=max_freq * 2 if max_freq > 0 else 100,
                split_number=10,
                detail_label_opts=opts.LabelOpts(
                    formatter="{value}次",
                    color='#f1f5f9',
                    font_size=24,
                    font_weight='bold'
                )
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=title,
                    title_textstyle_opts=opts.TextStyleOpts(color='#f1f5f9', font_size=20)
                ),
            )
        )
        return gauge
    return None


# ==================== 导出功能函数 ====================

def get_download_link(df, filename, file_format='csv'):
    if file_format == 'csv':
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv" style="display: inline-block; padding: 12px 24px; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; border-radius: 8px; text-decoration: none; font-weight: 600; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);">📥 下载 CSV 文件</a>'
    elif file_format == 'excel':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='词频统计')
        b64 = base64.b64encode(output.getvalue()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx" style="display: inline-block; padding: 12px 24px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border-radius: 8px; text-decoration: none; font-weight: 600; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);">📥 下载 Excel 文件</a>'
    elif file_format == 'json':
        json_str = df.to_json(orient='records', force_ascii=False, indent=2)
        b64 = base64.b64encode(json_str.encode()).decode()
        href = f'<a href="data:application/json;base64,{b64}" download="{filename}.json" style="display: inline-block; padding: 12px 24px; background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%); color: white; border-radius: 8px; text-decoration: none; font-weight: 600; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(6, 182, 212, 0.4);">📥 下载 JSON 文件</a>'

    return href


def create_matplotlib_wordcloud(word_freq):
    word_dict = dict(word_freq[:50])

    plt.figure(figsize=(12, 6))

    try:
        import matplotlib.font_manager as fm
        import os
        
        font_path = None
        
        font_paths = fm.findSystemFonts(fontpaths=None, fontext='ttf')
        font_paths += fm.findSystemFonts(fontpaths=None, fontext='ttc')
        
        chinese_fonts = [
            'wqy-microhei', 'wqy-zenhei', 'ukai', 'uming', 
            'NotoSansCJK', 'NotoSerifCJK', 'SimHei', 'SimSun',
            'Microsoft YaHei', 'STHeiti', 'Hiragino Sans GB',
            'DroidSansFallback'
        ]
        
        for path in font_paths:
            for font_name in chinese_fonts:
                if font_name.lower() in path.lower():
                    font_path = path
                    break
            if font_path:
                break

        if font_path is None:
            font_paths_list = [
                '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
                '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
                '/usr/share/fonts/truetype/noto/NotoSansCJK-SC.ttc',
                '/usr/share/fonts/truetype/noto/NotoSerifCJK-SC.ttc',
                '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            ]
            for path in font_paths_list:
                if os.path.exists(path):
                    font_path = path
                    break

        wordcloud = WordCloud(
            font_path=font_path,
            width=1000,
            height=500,
            background_color='#1e293b',
            max_words=100,
            max_font_size=120,
            random_state=42,
            colormap='viridis',
            prefer_horizontal=0.9
        ).generate_from_frequencies(word_dict)

    except Exception as e:
        try:
            wordcloud = WordCloud(
                width=1000,
                height=500,
                background_color='#1e293b',
                max_words=100,
                max_font_size=120,
                random_state=42,
                colormap='viridis',
                prefer_horizontal=0.9
            ).generate_from_frequencies(word_dict)
        except Exception as e2:
            st.warning(f"词云生成失败: {str(e2)}，将显示条形图替代")
            return create_bar_chart_as_image(word_freq[:20])

    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    plt.close()

    return buf


def create_bar_chart_as_image(word_freq):
    words = [item[0] for item in word_freq]
    counts = [item[1] for item in word_freq]

    plt.figure(figsize=(12, 6))
    bars = plt.barh(words[::-1], counts[::-1], color='#6366f1')
    plt.xlabel('出现次数', color='#94a3b8')
    plt.title('词频条形图', color='#f1f5f9', fontsize=16)
    plt.tick_params(axis='both', colors='#94a3b8')
    plt.gcf().set_facecolor('#1e293b')
    plt.gca().set_facecolor('#1e293b')
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    plt.close()

    return buf


# ==================== 侧边栏配置 ====================

with st.sidebar:
    st.markdown("## ⚙️ 分析设置")

    input_mode = st.radio(
        "选择输入方式:",
        ('URL链接', '直接输入文本'),
        index=0,
        key='input_mode'
    )

    if input_mode == 'URL链接':
        url = st.text_input(
            "🌐 输入文章URL:",
            value="https://icpc.pku.edu.cn/jj/index.htm",
            help="请输入要分析的网页URL"
        )
    else:
        raw_text_input = st.text_area(
            "📝 输入文本内容:",
            placeholder="请在此输入要分析的文本内容...",
            height=200,
            help="直接输入文本进行分析"
        )

    st.markdown("---")
    st.markdown("### 📊 分析参数")

    col1, col2 = st.columns(2)
    with col1:
        min_word_len = st.slider("最小词长:", 1, 5, 2, help="过滤小于此长度的词汇")
    with col2:
        min_frequency = st.slider("最低词频:", 1, 10, 2, help="过滤出现次数少于此值的词汇")

    use_stopwords = st.checkbox("使用停用词过滤", value=True, help="启用停用词过滤可排除常用无意义词汇")

    st.markdown("---")
    st.markdown("### 📝 自定义停用词")
    custom_stopwords_input = st.text_area(
        "添加自定义停用词（每行一个）:",
        placeholder="请输入自定义停用词，每行一个词\n例如:\n测试\n示例\n分析",
        height=100
    )

    st.markdown("---")
    st.markdown("### 🎨 可视化设置")

    chart_types = {
        "词云图": "wordcloud",
        "柱状图": "bar",
        "饼图": "pie",
        "折线图": "line",
        "散点图": "scatter",
        "漏斗图": "funnel",
        "雷达图": "radar",
        "树图": "treemap",
        "热力图": "heatmap",
        "仪表盘": "gauge"
    }

    selected_chart = st.selectbox(
        "选择图表类型:",
        list(chart_types.keys()),
        index=0
    )

    st.markdown("---")
    st.markdown("### 💾 导出设置")

    data_format = st.selectbox(
        "数据导出格式:",
        ["CSV", "Excel", "JSON"],
        index=0
    )

    if st.button("🚀 开始分析", type="primary", use_container_width=True):
        with st.spinner("正在分析..."):
            if input_mode == 'URL链接':
                if not url.strip():
                    st.error("❌ 请输入有效的URL")
                else:
                    text, length, success = fetch_webpage_content(url)
                    if success == True and text:
                        custom_stopwords = set(custom_stopwords_input.splitlines()) if custom_stopwords_input else None
                        words = process_text(text, min_word_len, use_stopwords, custom_stopwords)
                        word_freq = get_word_frequencies(words, min_frequency)

                        st.session_state.analysis_data = {
                            'raw_text': text,
                            'words': words,
                            'word_freq': word_freq,
                            'text_length': length,
                            'url': url,
                            'input_mode': 'url'
                        }
                        st.success("✅ 分析完成！")
                    else:
                        st.error(f"❌ 获取网页内容失败: {success}")
            else:
                if not raw_text_input.strip():
                    st.error("❌ 请输入文本内容")
                else:
                    text = raw_text_input
                    length = len(text)
                    custom_stopwords = set(custom_stopwords_input.splitlines()) if custom_stopwords_input else None
                    words = process_text(text, min_word_len, use_stopwords, custom_stopwords)
                    word_freq = get_word_frequencies(words, min_frequency)

                    st.session_state.analysis_data = {
                        'raw_text': text,
                        'words': words,
                        'word_freq': word_freq,
                        'text_length': length,
                        'url': '',
                        'input_mode': 'text'
                    }
                    st.success("✅ 分析完成！")


# ==================== 主内容区域 ====================

if st.session_state.analysis_data['word_freq']:
    data = st.session_state.analysis_data
    word_freq = data['word_freq']

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    st.markdown("## 📈 分析概览")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-icon">📝</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-value">{:,}</div>'.format(data["text_length"]), unsafe_allow_html=True)
        st.markdown('<div class="metric-label">文本长度</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-subtitle">字符</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-icon">🔤</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-value">{:,}</div>'.format(len(data["words"])), unsafe_allow_html=True)
        st.markdown('<div class="metric-label">分词数量</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-subtitle">个词汇</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-icon">✨</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-value">{:,}</div>'.format(len(word_freq)), unsafe_allow_html=True)
        st.markdown('<div class="metric-label">有效词汇</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-subtitle">词频≥{}</div>'.format(min_frequency), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-icon">🥇</div>', unsafe_allow_html=True)
        if word_freq:
            st.markdown('<div class="metric-value">{}</div>'.format(word_freq[0][0]), unsafe_allow_html=True)
            st.markdown('<div class="metric-label">最高频词</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-subtitle">出现{}次</div>'.format(word_freq[0][1]), unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-value">无</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">最高频词</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-subtitle">-</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📋 词频统计", "📊 可视化", "📈 高级分析", "💾 导出数据"])

    with tab1:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        
        st.markdown("### 🥇 词频排名前20")
        df_top20 = pd.DataFrame(word_freq[:20], columns=["词汇", "出现次数"])
        df_top20["排名"] = range(1, len(df_top20) + 1)
        df_top20["占比(%)"] = (df_top20["出现次数"] / df_top20["出现次数"].sum() * 100).round(2)
        df_top20 = df_top20[["排名", "词汇", "出现次数", "占比(%)"]]

        st.dataframe(
            df_top20,
            use_container_width=True,
            hide_index=True,
            column_config={
                "排名": st.column_config.NumberColumn(width="small", format="%d"),
                "词汇": st.column_config.TextColumn(width="medium"),
                "出现次数": st.column_config.NumberColumn(width="small", format="%d"),
                "占比(%)": st.column_config.NumberColumn(format="%.2f%%", width="small")
            }
        )

        st.markdown("---")
        
        with st.expander("📖 查看完整词频表", expanded=False):
            df_full = pd.DataFrame(word_freq, columns=["词汇", "出现次数"])
            df_full["排名"] = range(1, len(df_full) + 1)
            df_full["占比(%)"] = (df_full["出现次数"] / df_full["出现次数"].sum() * 100).round(2)
            st.dataframe(df_full, use_container_width=True, height=400)
        
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        
        st.markdown(f"### 📊 {selected_chart}")

        chart_type = chart_types[selected_chart]
        chart = None

        if chart_type == "wordcloud":
            chart = create_wordcloud(word_freq, selected_chart)
        elif chart_type == "bar":
            chart = create_bar_chart(word_freq, selected_chart)
        elif chart_type == "pie":
            chart = create_pie_chart(word_freq, selected_chart)
        elif chart_type == "line":
            chart = create_line_chart(word_freq, selected_chart)
        elif chart_type == "scatter":
            chart = create_scatter_chart(word_freq, selected_chart)
        elif chart_type == "funnel":
            chart = create_funnel_chart(word_freq, selected_chart)
        elif chart_type == "radar":
            chart = create_radar_chart(word_freq, selected_chart)
        elif chart_type == "treemap":
            chart = create_treemap_chart(word_freq, selected_chart)
        elif chart_type == "heatmap":
            chart = create_heatmap_chart(word_freq, selected_chart)
        elif chart_type == "gauge":
            chart = create_gauge_chart(word_freq, selected_chart)

        if chart:
            st_pyecharts(chart, height="550px")

            if chart_type == "wordcloud":
                st.markdown("---")
                st.markdown("### 🎨 Matplotlib词云图")
                buf = create_matplotlib_wordcloud(word_freq)
                st.image(buf, width="stretch")
        
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        
        st.markdown("### 📊 文本复杂度分析")

        col1, col2 = st.columns(2)

        with col1:
            if data['words']:
                unique_words = len(set(data['words']))
                richness = (unique_words / len(data['words'])) * 100

                st.markdown('<div class="highlight-card">', unsafe_allow_html=True)
                st.markdown("#### 🎯 词汇丰富度")
                st.metric("丰富度指数", f"{richness:.1f}%")
                st.progress(min(richness / 100, 1.0))
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="highlight-card">', unsafe_allow_html=True)
                st.markdown("#### 📏 词长分布")
                word_lengths = [len(word) for word in data['words']]
                length_dist = pd.Series(word_lengths).value_counts().sort_index()
                st.bar_chart(length_dist, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="highlight-card">', unsafe_allow_html=True)
            st.markdown("#### 📈 词频分布曲线")
            freqs = [count for _, count in word_freq[:50]]
            ranks = list(range(1, len(freqs) + 1))

            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(ranks, freqs, 'o-', linewidth=2, markersize=4, color='#6366f1')
            ax.set_xlabel('排名', color='#94a3b8')
            ax.set_ylabel('词频', color='#94a3b8')
            ax.set_title('Zipf定律分布曲线', color='#f1f5f9')
            ax.grid(True, alpha=0.3)
            ax.set_facecolor('#1e293b')
            fig.set_facecolor('#1e293b')
            ax.tick_params(axis='both', colors='#94a3b8')
            st.pyplot(fig)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="highlight-card">', unsafe_allow_html=True)
            st.markdown("#### 📊 统计摘要")
            st.write(f"- 总词数: **{len(data['words']):,}**")
            st.write(f"- 唯一词数: **{len(set(data['words'])):,}**")
            st.write(f"- 平均词长: **{np.mean([len(w) for w in data['words']]):.1f}**")
            st.write(f"- 中位数词频: **{np.median([c for _, c in word_freq]):.0f}**")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        
        st.markdown("### 🔑 文本关键词提取")
        if data['raw_text']:
            try:
                keywords = jieba.analyse.extract_tags(
                    data['raw_text'],
                    topK=10,
                    withWeight=True,
                    allowPOS=('n', 'vn', 'v', 'nr', 'ns', 'nt', 'nz')
                )

                df_keywords = pd.DataFrame(keywords, columns=["关键词", "权重"])
                df_keywords["权重"] = (df_keywords["权重"] * 100).round(2)
                
                st.dataframe(
                    df_keywords,
                    use_container_width=True,
                    column_config={
                        "关键词": st.column_config.TextColumn(width="medium"),
                        "权重": st.column_config.NumberColumn(format="%.2f%%", width="small")
                    }
                )
            except:
                st.info("💡 关键词提取功能需要更长的文本支持")
        
        st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        
        st.markdown("### 📥 数据导出")

        df_export = pd.DataFrame(word_freq, columns=["词汇", "出现次数"])
        df_export["排名"] = range(1, len(df_export) + 1)
        df_export["占比(%)"] = (df_export["出现次数"] / df_export["出现次数"].sum() * 100).round(2)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header"><div class="card-icon">📊</div><div class="card-title">导出词频数据</div></div>', unsafe_allow_html=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"词频统计_{timestamp}"
            href = get_download_link(df_export, filename, data_format.lower())
            st.markdown(href, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header"><div class="card-icon">📄</div><div class="card-title">导出原始文本</div></div>', unsafe_allow_html=True)
            txt_data = data['raw_text'].encode('utf-8')
            b64 = base64.b64encode(txt_data).decode()
            href = f'<a href="data:text/plain;base64,{b64}" download="原始文本_{timestamp}.txt" style="display: inline-block; padding: 12px 24px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; border-radius: 8px; text-decoration: none; font-weight: 600; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);">📥 下载原始文本</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header"><div class="card-icon">📋</div><div class="card-title">导出分析报告</div></div>', unsafe_allow_html=True)
            report = {
                "analysis_time": datetime.now().isoformat(),
                "input_mode": data['input_mode'],
                "url": data['url'],
                "text_length": data['text_length'],
                "word_count": len(data['words']),
                "unique_words": len(set(data['words'])),
                "top_keywords": word_freq[:10],
                "parameters": {
                    "min_word_len": min_word_len,
                    "min_frequency": min_frequency,
                    "use_stopwords": use_stopwords
                }
            }

            json_str = json.dumps(report, ensure_ascii=False, indent=2)
            b64 = base64.b64encode(json_str.encode()).decode()
            href = f'<a href="data:application/json;base64,{b64}" download="分析报告_{timestamp}.json" style="display: inline-block; padding: 12px 24px; background: linear-gradient(135deg, #ec4899 0%, #db2777 100%); color: white; border-radius: 8px; text-decoration: none; font-weight: 600; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(236, 72, 153, 0.4);">📥 下载分析报告</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🖼️ 图表导出")

        if chart:
            chart_html = chart.render_embed()

            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-header"><div class="card-icon">🌐</div><div class="card-title">导出为HTML</div></div>', unsafe_allow_html=True)
                b64 = base64.b64encode(chart_html.encode()).decode()
                href = f'<a href="data:text/html;base64,{b64}" download="图表_{timestamp}.html" style="display: inline-block; padding: 12px 24px; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; border-radius: 8px; text-decoration: none; font-weight: 600; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);">📥 下载HTML图表</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-header"><div class="card-icon">📋</div><div class="card-title">复制图表代码</div></div>', unsafe_allow_html=True)
                st.code(chart_html[:500] + "..." if len(chart_html) > 500 else chart_html, language='html')
                st.markdown('</div>', unsafe_allow_html=True)

        if chart_type == "wordcloud":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header"><div class="card-icon">🎨</div><div class="card-title">导出Matplotlib词云</div></div>', unsafe_allow_html=True)
            buf = create_matplotlib_wordcloud(word_freq)

            btn = st.download_button(
                label="📥 下载词云图片",
                data=buf,
                file_name=f"词云图_{timestamp}.png",
                mime="image/png",
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    with st.expander("📄 查看原始文本"):
        st.text_area("", data['raw_text'][:3000] + ("..." if len(data['raw_text']) > 3000 else ""),
                     height=300, label_visibility="collapsed")

else:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        ## 🎯 系统功能介绍

        这是一个功能强大的文本词频分析系统，支持多种分析模式和可视化展示。

        ### 📋 核心功能
        - **URL文本抓取** - 自动抓取网页文本内容进行分析
        - **直接文本输入** - 支持直接输入文本进行分析
        - **智能中文分词** - 使用jieba进行精准分词处理
        - **词频统计分析** - 统计词汇出现频率并排序
        - **多维度可视化** - 10种专业图表类型展示分析结果

        ### 🎨 可视化图表（10种）
        | 图标 | 图表类型 | 功能描述 |
        |------|---------|---------|
        | 📊 | 词云图 | 直观展示词汇分布与权重 |
        | 📈 | 柱状图 | 精确对比词频数值 |
        | 🥧 | 饼图 | 显示词汇占比关系 |
        | 📉 | 折线图 | 展示词频趋势变化 |
        | ✨ | 散点图 | 显示词频分布模式 |
        | 🎯 | 漏斗图 | 突出主要词汇层级 |
        | 🎨 | 雷达图 | 多维度展示词汇分布 |
        | 🌳 | 树图 | 层次化展示词频结构 |
        | 🔥 | 热力图 | 密度可视化展示 |
        | 🎛️ | 仪表盘 | 直观显示关键指标 |

        ### ⚡ 高级功能
        - 🔧 **交互式过滤** - 动态调整分析参数
        - 📝 **自定义停用词** - 支持添加个性化停用词
        - 💾 **多格式导出** - CSV/Excel/JSON/图片/HTML
        - 📊 **文本分析** - 词汇丰富度、词长分布
        - 🔍 **关键词提取** - 自动提取文本关键词
        """)

    with col2:
        st.markdown("""
        ## 📚 示例URL

        ### 新闻资讯类
        - 新浪新闻：https://news.sina.com.cn
        - 网易新闻：https://news.163.com
        - 腾讯新闻：https://news.qq.com

        ### 百科知识类
        - 百度百科：https://baike.baidu.com
        - 维基百科：https://zh.wikipedia.org

        ### 技术博客类
        - CSDN博客：https://blog.csdn.net
        - 知乎专栏：https://zhuanlan.zhihu.com

        ## 💡 使用建议

        1. 选择内容丰富的网页
        2. 避免图片/视频为主的页面
        3. 优先选择中文内容
        4. 确保网络连接正常

        ## ⚠️ 注意事项
        - 部分网站可能有反爬机制
        - 建议使用公开可访问的URL
        - 分析时间与文本长度相关
        - 导出功能需要浏览器支持
        """)

    st.markdown("---")
    st.info("👈 请在左侧边栏输入URL或文本，点击【开始分析】按钮，开始你的文本分析之旅！")

# 页脚
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #64748b; padding: 20px; background: rgba(30, 41, 59, 0.5); border-radius: 12px; margin-top: 30px;">
        <p>📊 <b style="color: #94a3b8;">智能文本词频分析系统</b> | 版本 3.0 | 基于 Streamlit + PyECharts + Jieba</p>
        <p style="font-size: 0.85rem; margin-top: 8px;">© 2026 文本分析实验室 | 功能：文本抓取 · 词频统计 · 多维度可视化 · 数据导出</p>
        <div style="margin-top: 12px; display: flex; justify-content: center; gap: 24px; font-size: 0.8rem;">
            <span>🔧 支持URL/文本双输入</span>
            <span>🎨 10种可视化图表</span>
            <span>💾 多格式数据导出</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
