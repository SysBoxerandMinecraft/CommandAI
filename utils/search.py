"""
增强版联网搜索工具
支持多源：DuckDuckGo (lite) → Wikipedia → 百度（备用）
"""
import requests
from typing import List, Dict
import time

# ---------- 通用辅助 ----------
def format_search_results(results: List[Dict[str, str]]) -> str:
    if not results:
        return "未找到相关结果。"
    text = "以下是根据搜索得到的信息：\n\n"
    for idx, r in enumerate(results, 1):
        text += f"{idx}. {r['title']}\n"
        text += f"   {r['body']}\n"
        if r.get('link'):
            text += f"   链接: {r['link']}\n"
        text += "\n"
    return text

# ---------- 主入口 ----------
def search_web(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    根据查询内容自动选择搜索方式：
    - 含"天气" → 调用天气 API
    - 否则尝试 DuckDuckGo → Wikipedia → 百度
    """
    if "天气" in query:
        return _get_weather(query)

    # 尝试各搜索源
    results = _search_duckduckgo_lite(query, max_results)
    if results:
        return results

    results = _search_wikipedia(query, max_results)
    if results and results[0].get('title') != "百科查询未启用":
        return results

    # 最后尝试百度（可能被屏蔽，但作为备选）
    results = _search_baidu(query, max_results)
    if results:
        return results

    return [{
        'title': '搜索失败',
        'body': '所有搜索源均无法获取结果，请检查网络或稍后重试。',
        'link': ''
    }]

# ---------- 天气 ----------
def _get_weather(query: str) -> List[Dict[str, str]]:
    city = query.replace("天气", "").strip() or "Beijing"
    try:
        url = f"http://wttr.in/{city}?format=%C+%t"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            weather_text = resp.text.strip()
            return [{
                'title': f"{city} 天气",
                'body': f"当前天气：{weather_text}",
                'link': f"https://wttr.in/{city}"
            }]
        else:
            return [{'title': '天气查询失败', 'body': f'状态码 {resp.status_code}', 'link': ''}]
    except Exception as e:
        return [{'title': '天气服务不可用', 'body': str(e), 'link': ''}]

# ---------- DuckDuckGo Lite ----------
def _search_duckduckgo_lite(query: str, max_results: int) -> List[Dict[str, str]]:
    try:
        # 使用 ddgs 库（需安装 ddgs）
        from ddgs import DDGS
    except ImportError:
        return []   # 未安装则跳过

    results = []
    try:
        # 使用 'lite' 后端，可能对网络更友好
        with DDGS(timeout=30) as ddgs:
            for r in ddgs.text(query, max_results=max_results, backend='lite'):
                results.append({
                    'title': r.get('title', ''),
                    'body': r.get('body', ''),
                    'link': r.get('href', '')
                })
        return results
    except Exception as e:
        # 记录日志（可选），但返回空列表以继续尝试下一源
        return []

# ---------- Wikipedia ----------
def _search_wikipedia(query: str, max_results: int) -> List[Dict[str, str]]:
    try:
        import wikipedia
        wikipedia.set_lang("zh")
    except ImportError:
        return [{'title': '百科查询未启用', 'body': '请安装 wikipedia: pip install wikipedia', 'link': ''}]

    results = []
    try:
        search_results = wikipedia.search(query, results=max_results)
        for title in search_results:
            try:
                page = wikipedia.page(title)
                results.append({
                    'title': title,
                    'body': page.summary[:500],
                    'link': page.url
                })
            except (wikipedia.DisambiguationError, wikipedia.PageError):
                continue
        return results
    except Exception:
        return []

# ---------- 百度搜索（简单爬虫，备用） ----------
def _search_baidu(query: str, max_results: int) -> List[Dict[str, str]]:
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return []  # 未安装则跳过

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    url = f"https://www.baidu.com/s?wd={requests.utils.quote(query)}"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, 'html.parser')
        # 百度搜索结果通常在 class="result" 或 "c-container" 中
        items = soup.find_all('div', class_='result') or soup.find_all('div', class_='c-container')
        results = []
        for item in items[:max_results]:
            title_tag = item.find('h3') or item.find('a')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link_tag = item.find('a', href=True)
            link = link_tag['href'] if link_tag else ''
            body_tag = item.find('div', class_='c-abstract') or item.find('div', class_='content-right') or item.find('p')
            body = body_tag.get_text(strip=True) if body_tag else ''
            if title and body:
                results.append({'title': title, 'body': body, 'link': link})
        return results
    except Exception:
        return []