import time

from duckduckgo_search import DDGS


def find_url(school_name: str) -> str:
    """組織名からDuckDuckGo検索で公式URLを1件取得する。"""
    if not school_name.strip():
        return ""
    query = f"{school_name} 公式サイト"
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=1))
        return results[0]["href"] if results else ""
    except Exception:
        return ""
    finally:
        time.sleep(3)
