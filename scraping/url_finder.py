import time

try:
    from googlesearch import search
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False


def find_url(school_name: str) -> str:
    """学校名からGoogle検索で公式URLを1件取得する。"""
    if not _AVAILABLE or not school_name.strip():
        return ""
    query = f"{school_name} 公式サイト"
    try:
        results = list(search(query, num_results=1, lang="ja"))
        return results[0] if results else ""
    except Exception:
        return ""
    finally:
        time.sleep(2)  # Google へのレート制限
