"""HTMLから連絡先（電話・FAX・メール・住所）を抽出するモジュール。"""
import re
from bs4 import BeautifulSoup

# ── 正規表現パターン ───────────────────────────────────────────
TEL_PATTERN = re.compile(
    r"(?:tel|電話|ＴＥＬ)[^\d\(]*(\(?\d{2,4}\)?[ー－\-\s]?\d{1,4}[ー－\-\s]?\d{4})",
    re.IGNORECASE,
)
FAX_PATTERN = re.compile(
    r"(?:fax|ファックス|ＦＡＸ)[^\d\(]*(\(?\d{2,4}\)?[ー－\-\s]?\d{1,4}[ー－\-\s]?\d{4})",
    re.IGNORECASE,
)
MAIL_PATTERN = re.compile(
    r"(?:mail|e-?mail)[^\S\r\n]*[:：]?\s*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})",
    re.IGNORECASE,
)
_OBF_AT = r"(?:@|\(at\)|\[at\]|&#64;|＠)"
_OBF_DOT = r"(?:\.|\(dot\)|\[dot\]|&#46;|．)"
EMAIL_OBF_PATTERN = re.compile(
    rf"([A-Za-z0-9._%+-]+)\s*{_OBF_AT}\s*([A-Za-z0-9.-]+)(?:\s*{_OBF_DOT}\s*([A-Za-z]{{2,}}))?",
    re.IGNORECASE,
)
POSTCODE_PATTERN = re.compile(r"(〒\s*\d{3}-\d{4}\s*[^\n]+)")
ADDR_LABEL_PATTERN = re.compile(r"住所[：:]\s*(.+)")


def extract_from_html(html: str) -> dict:
    """HTML文字列から連絡先情報を抽出し、辞書で返す。"""
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text("\n")

    # <address> タグ
    addr_tag = soup.find("address")
    addr_text = addr_tag.get_text(" ", strip=True) if addr_tag else ""

    # #tel 要素
    tel_div = soup.select_one("#tel")
    div_tel, div_addr = "", ""
    if tel_div:
        parts = tel_div.get_text("\n").split("\n")
        div_tel = parts[0].strip()
        if len(parts) > 1:
            div_addr = parts[1].strip()

    # ── メールアドレス ────────────────────────────────────────
    mail = ""
    a_mailto = soup.select_one('a[href^="mailto:"]')
    if a_mailto:
        mail = a_mailto["href"].split(":", 1)[1].strip()
    if not mail:
        m = MAIL_PATTERN.search(text)
        mail = m.group(1) if m else ""
    if not mail:
        m2 = EMAIL_OBF_PATTERN.search(text)
        if m2:
            user, domain, tld = m2.group(1), m2.group(2), m2.group(3)
            mail = f"{user}@{domain}" + (f".{tld}" if tld else "")

    # ── 電話番号 ──────────────────────────────────────────────
    tel = ""
    if div_tel and re.match(r"[\d\(\)ー－\-\s]{7,}", div_tel):
        tel = div_tel
    elif addr_text:
        m = re.search(r"電話番号[：:]\s*([\d\(\)ー－\-\s]{7,})", addr_text)
        tel = m.group(1) if m else ""
    if not tel:
        m = TEL_PATTERN.search(text)
        tel = m.group(1) if m else ""

    # ── FAX番号 ───────────────────────────────────────────────
    fax = ""
    if addr_text:
        m = re.search(r"FAX[：:]\s*([\d\(\)ー－\-\s]{7,})", addr_text, re.IGNORECASE)
        fax = m.group(1) if m else ""
    if not fax:
        m = FAX_PATTERN.search(text)
        fax = m.group(1) if m else ""

    # ── 住所 ─────────────────────────────────────────────────
    address = ""
    if addr_text:
        address = addr_text
    elif div_addr:
        address = div_addr
    else:
        m = POSTCODE_PATTERN.search(text)
        if m:
            address = m.group(1)
        else:
            m2 = ADDR_LABEL_PATTERN.search(text)
            address = m2.group(1) if m2 else ""

    return {
        "電話番号": tel.strip(),
        "FAX番号": fax.strip(),
        "メールアドレス": mail.strip(),
        "住所": address.strip(),
    }
