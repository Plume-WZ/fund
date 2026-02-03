import importlib
import threading
import json
import os
import urllib3
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, request, Response, stream_with_context, abort
from flask_httpauth import HTTPBasicAuth
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from loguru import logger

import fund
from ai_analyzer import AIAnalyzer, search_news, fetch_webpage
from module_html import get_full_page_html

# =========================
# 基础初始化
# =========================
load_dotenv()
urllib3.disable_warnings()

app = Flask(__name__)
auth = HTTPBasicAuth()
analyzer = AIAnalyzer()

# =========================
# 认证配置（公网必须）
# =========================
WEB_USER = os.getenv("WEB_USER", "admin")
WEB_PASSWORD = os.getenv("WEB_PASSWORD", "Wangzhe521*")

USERS = {WEB_USER: WEB_PASSWORD}

@auth.verify_password
def verify_password(username, password):
    if username in USERS and USERS[username] == password:
        return username
    return None

def auth_required(func):
    """兼容 SSE 的认证装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_info = request.authorization
        if not auth_info or not verify_password(auth_info.username, auth_info.password):
            return Response(
                "Unauthorized",
                401,
                {"WWW-Authenticate": 'Basic realm="Fund Server"'}
            )
        return func(*args, **kwargs)
    return wrapper

# =========================
# 后端数据获取
# =========================
def get_real_time_data_context(user_message, history):
    try:
        my_fund = fund.MaYiFund()
        context_parts = []

        data_modules = {
            'kx': {'name': '7*24快讯', 'func': my_fund.kx_html, 'keywords': ['快讯', '新闻']},
            'marker': {'name': '全球指数', 'func': my_fund.marker_html, 'keywords': ['指数']},
            'real_time_gold': {'name': '实时贵金属', 'func': my_fund.real_time_gold_html, 'keywords': ['黄金']},
            'gold': {'name': '历史金价', 'func': my_fund.gold_html, 'keywords': ['历史金价']},
            'seven_A': {'name': '成交量趋势', 'func': my_fund.seven_A_html, 'keywords': ['成交量']},
            'A': {'name': '上证分时', 'func': my_fund.A_html, 'keywords': ['分时']},
            'fund': {'name': '自选基金', 'func': my_fund.fund_html, 'keywords': ['基金']},
            'bk': {'name': '行业板块', 'func': my_fund.bk_html, 'keywords': ['板块']},
        }

        combined_text = (user_message + " ".join(
            [m.get("content", "") for m in history[-5:]]
        )).lower()

        modules = [
            m for m in data_modules.values()
            if any(k in combined_text for k in m['keywords'])
        ] or [
            data_modules['fund'],
            data_modules['bk'],
            data_modules['kx'],
        ]

        from html.parser import HTMLParser
        class Extractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []
            def handle_data(self, d):
                if d.strip():
                    self.text.append(d.strip())
            def get(self):
                return "\n".join(self.text)

        for m in modules:
            try:
                html = m['func']()
                p = Extractor()
                p.feed(html)
                context_parts.append(f"\n=== {m['name']} ===\n{p.get()}")
            except Exception as e:
                context_parts.append(f"\n=== {m['name']} ===\n获取失败: {e}")

        return "\n".join(context_parts)

    except Exception as e:
        logger.error(e)
        return "数据获取失败"

# =========================
# Chat API（SSE + 认证）
# =========================
@app.route('/api/chat', methods=['POST'])
@auth_required
def chat():
    data = request.json or {}
    user_message = data.get("message", "")
    history = data.get("history", [])

    def generate():
        llm = analyzer.init_langchain_llm(fast_mode=True)
        if not llm:
            yield "data: {\"error\":\"LLM not ready\"}\n\n"
            return

        context = get_real_time_data_context(user_message, history)
        messages = [
            SystemMessage(content="金融分析助手"),
            HumanMessage(content=f"{context}\n\n问题：{user_message}")
        ]

        response = llm.invoke(messages)
        for i in range(0, len(response.content), 120):
            yield f"data: {json.dumps({'type':'content','chunk':response.content[i:i+120]}, ensure_ascii=False)}\n\n"
        yield "data: {\"type\":\"done\"}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

# =========================
# 页面接口（默认自选基金）
# =========================
@app.route('/fund', methods=['GET'])
@auth_required
def get_fund():
    importlib.reload(fund)
    my_fund = fund.MaYiFund()

    results = {}
    tasks = {
        'fund': my_fund.fund_html,
        'bk': my_fund.bk_html,
        'kx': my_fund.kx_html,
        'marker': my_fund.marker_html,
        'gold': my_fund.gold_html,
        'real_time_gold': my_fund.real_time_gold_html,
        'seven_A': my_fund.seven_A_html,
        'A': my_fund.A_html,
        'select_fund': my_fund.select_fund_html,
    }

    def fetch(name, func):
        try:
            results[name] = func()
        except Exception as e:
            results[name] = f"<p style='color:red'>{e}</p>"

    threads = []
    for n, f in tasks.items():
        t = threading.Thread(target=fetch, args=(n, f))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    # ⭐ 默认第一个就是「自选基金」
    tabs_data = [
        {"id": "fund", "title": "自选基金", "content": results["fund"]},
        {"id": "bk", "title": "行业板块", "content": results["bk"]},
        {"id": "kx", "title": "7*24快讯", "content": results["kx"]},
        {"id": "marker", "title": "全球指数", "content": results["marker"]},
        {"id": "real_time_gold", "title": "实时贵金属", "content": results["real_time_gold"]},
        {"id": "gold", "title": "历史金价", "content": results["gold"]},
        {"id": "seven_A", "title": "成交量趋势", "content": results["seven_A"]},
        {"id": "A", "title": "上证分时", "content": results["A"]},
        {"id": "select_fund", "title": "板块基金查询", "content": results["select_fund"]},
    ]

    return get_full_page_html(tabs_data)

# =========================
# 启动
# =========================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10111)

