"""
学校連絡先スクレイパー
====================
CSVをアップロードするだけで電話番号・FAX・メール・住所を自動取得します。
"""
import io
import re
import time
import urllib.parse

import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

from scraping.contact_extractor import extract_from_html
from scraping.url_finder import find_url

# ── ページ設定 ────────────────────────────────────────────────
st.set_page_config(
    page_title="学校連絡先スクレイパー",
    page_icon="🏫",
    layout="centered",
)

st.title("🏫 学校連絡先スクレイパー")
st.caption("CSVをアップロードするだけで、電話番号・FAX・メールアドレス・住所を自動で取得します。")
st.divider()

# ── セッション初期化 ──────────────────────────────────────────
if "result_df" not in st.session_state:
    st.session_state.result_df = None
if "last_file_name" not in st.session_state:
    st.session_state.last_file_name = None


# ── ① ファイルアップロード ────────────────────────────────────
st.subheader("① CSVファイルを選んでください")
uploaded = st.file_uploader(
    label="ファイルを選ぶ",
    type=["csv"],
    label_visibility="collapsed",
    help="学校名が入ったCSVファイルを選んでください（Excel で「CSV UTF-8」形式で保存したものが最適です）",
)

if uploaded is None:
    st.info("⬆️ 上のボタンからCSVファイルをアップロードしてください")
    st.stop()

# 新しいファイルが来たら結果をリセット
if uploaded.name != st.session_state.last_file_name:
    st.session_state.result_df = None
    st.session_state.last_file_name = uploaded.name

# エンコーディングを自動判定して読み込み
for enc in ("utf-8-sig", "cp932", "utf-8"):
    try:
        uploaded.seek(0)
        df_input = pd.read_csv(uploaded, encoding=enc)
        break
    except (UnicodeDecodeError, Exception):
        continue
else:
    st.error("CSVの読み込みに失敗しました。ファイルの形式を確認してください。")
    st.stop()

st.success(f"✅ {len(df_input):,} 件のデータを読み込みました")
with st.expander("読み込んだデータを確認する"):
    st.dataframe(df_input.head(10), use_container_width=True)


# ── ② 設定 ───────────────────────────────────────────────────
st.divider()
st.subheader("② 設定")

columns = df_input.columns.tolist()

school_col = st.selectbox(
    "学校名が入っている列",
    options=columns,
    help="学校名の列を選んでください",
)

url_col_options = ["（Googleで自動検索する）"] + columns
url_col_selection = st.selectbox(
    "URLが入っている列（すでにURLがある場合のみ選ぶ）",
    options=url_col_options,
    help="URL列があればGoogle検索をスキップできます。ない場合はそのままでOKです。",
)
has_url = url_col_selection != "（Googleで自動検索する）"
url_col = url_col_selection if has_url else None

include_subpage = st.checkbox(
    "住所が取れない場合、アクセスページ等も調べる（推奨・少し時間がかかります）",
    value=True,
)

# 推定時間
n = len(df_input)
est_sec = n * (2 if has_url else 5) * (1.4 if include_subpage else 1.0)
est_min, est_sec_r = divmod(int(est_sec), 60)
st.info(f"⏱️ 推定処理時間: 約 **{est_min}分 {est_sec_r}秒**（{n:,}件）\n\n"
        "処理中はブラウザを閉じないでください。")


# ── ③ 処理実行 ────────────────────────────────────────────────
st.divider()
st.subheader("③ 処理を開始する")

if st.button("🚀 処理開始", type="primary", use_container_width=True):
    df = df_input.copy()
    progress = st.progress(0.0, text="準備中...")
    log_box = st.empty()
    log_lines: list[str] = []

    def add_log(msg: str) -> None:
        log_lines.append(msg)
        log_box.text("\n".join(log_lines[-10:]))

    url_steps = 0 if has_url else n
    total_steps = url_steps + n + (n if include_subpage else 0)
    step = [0]  # リストにすることでネスト関数から更新可能にする

    def advance(label: str) -> None:
        step[0] += 1
        pct = min(step[0] / total_steps, 0.99)
        progress.progress(pct, text=label)

    # ── Step A: URL取得 ───────────────────────────────────────
    if not has_url:
        add_log("📡 URLを検索中...")
        urls = []
        for i, school in enumerate(df[school_col].fillna("").astype(str)):
            advance(f"URL検索中 ({i+1}/{n}): {school}")
            url = find_url(school)
            urls.append(url)
            icon = "✅" if url else "❌"
            add_log(f"{icon} [{i+1}] {school}  →  {url or '見つかりません'}")
        df["URL"] = urls
    else:
        df["URL"] = df[url_col].fillna("").astype(str)

    # ── Step B: スクレイピング＆連絡先抽出 ───────────────────
    add_log("\n🔍 各学校サイトから連絡先を取得中...")
    contacts: list[dict] = []
    _headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    _empty = {"電話番号": "", "FAX番号": "", "メールアドレス": "", "住所": ""}

    for i, row in df.iterrows():
        school = str(row[school_col])
        url = str(row["URL"])
        advance(f"スクレイピング中 ({i+1}/{n}): {school}")

        if not url.startswith("http"):
            contacts.append(_empty.copy())
            add_log(f"⚠️ [{i+1}] {school}: URLが無効のためスキップ")
            continue

        try:
            resp = requests.get(url, timeout=10, headers=_headers)
            resp.encoding = resp.apparent_encoding
            html = resp.text
            contact = extract_from_html(html)

            # サブページで住所を補完
            if include_subpage and not contact["住所"]:
                advance(f"サブページ検索中 ({i+1}/{n}): {school}")
                soup = BeautifulSoup(html, "lxml")
                for a_tag in soup.find_all("a", href=True):
                    link_text = a_tag.get_text(strip=True)
                    if re.search(r"アクセス|所在地|交通|学校案内|概要|施設", link_text):
                        sub_url = urllib.parse.urljoin(url, a_tag["href"])
                        try:
                            sub_resp = requests.get(sub_url, timeout=8, headers=_headers)
                            sub_resp.encoding = sub_resp.apparent_encoding
                            sub = extract_from_html(sub_resp.text)
                            if sub["住所"]:
                                contact["住所"] = sub["住所"]
                                if not contact["電話番号"]:
                                    contact["電話番号"] = sub["電話番号"]
                                if not contact["メールアドレス"]:
                                    contact["メールアドレス"] = sub["メールアドレス"]
                                break
                        except Exception:
                            pass

            contacts.append(contact)
            got = [k for k, v in contact.items() if v]
            add_log(f"✅ [{i+1}] {school}: {', '.join(got) if got else '取得できず'}")

        except Exception:
            contacts.append(_empty.copy())
            add_log(f"❌ [{i+1}] {school}: 取得失敗（接続エラー）")

        time.sleep(1)

    # ── 結果をDataFrameにまとめる ─────────────────────────────
    result = df_input.copy()
    result["URL"] = df["URL"]
    contacts_df = pd.DataFrame(contacts)
    for col_name in contacts_df.columns:
        result[col_name] = contacts_df[col_name].values

    progress.progress(1.0, text="✅ 完了！")
    st.session_state.result_df = result


# ── ④ 結果表示＆ダウンロード ──────────────────────────────────
if st.session_state.result_df is not None:
    result_df = st.session_state.result_df

    st.divider()
    st.subheader("④ 結果")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("総件数", f"{len(result_df):,}")
    c2.metric("電話番号あり", f"{result_df['電話番号'].str.strip().ne('').sum():,}")
    c3.metric("メールあり", f"{result_df['メールアドレス'].str.strip().ne('').sum():,}")
    c4.metric("住所あり", f"{result_df['住所'].str.strip().ne('').sum():,}")

    st.dataframe(result_df, use_container_width=True, height=400)

    buf = io.BytesIO()
    result_df.to_csv(buf, index=False, encoding="utf-8-sig")
    buf.seek(0)
    st.download_button(
        label="📥 CSVをダウンロード",
        data=buf,
        file_name="contacts_result.csv",
        mime="text/csv",
        type="primary",
        use_container_width=True,
    )
