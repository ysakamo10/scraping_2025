# 連絡先スクレイパー

組織名（学校・企業など）のCSVをアップロードするだけで、電話番号・FAX・メールアドレス・住所を自動取得するWebアプリです。

## 使い方（アプリ利用者向け）

1. ブラウザでアプリのURLを開く
2. 組織名が入ったCSVをアップロード
3. 「処理開始」ボタンを押す（処理中はブラウザを閉じない）
4. 完了したら「CSVをダウンロード」

### CSVファイルの形式

Excelで作成する場合は「名前を付けて保存 → CSV UTF-8（コンマ区切り）」を選んでください。

| 組織名 |
|--------|
| ○○高等学校 |
| △△株式会社 |

**URLがすでにある場合は列として含めておくことを強く推奨します。**
URL列があると自動検索をスキップできるため、速く・確実に動きます。

---

## URL自動検索について（重要）

URL列なしで実行すると、DuckDuckGoで自動検索しますが、**ブロックされて全件×になることがあります。**

### ブロックされた場合の対処

- 数時間〜半日待ってから再実行する
- それでも動かない場合は、URLを手動でExcelに入力してからアップロードする

### ブロックされにくくするために

- `scraping/url_finder.py` の `time.sleep(3)` を **5秒以上** に増やす（件数が多い場合）
- 1回の実行件数を減らす（50件ずつ分割するなど）

### 過去の実績

- 2025年5月：1191件、sleep=3秒ペースで約60分かけて全件取得できた
- 2026年2月：176件、sleep=1秒で実行 → Googleにブロックされ全件×
  → sleep=3秒に修正済み（`url_finder.py` 更新済み）

---

## GitHubへのアップロード方法（初回のみ）

### 1. GitHubアカウントを作成

https://github.com にアクセスしてアカウントを作成してください（無料）。

### 2. 新しいリポジトリを作成

1. GitHub右上の「+」→「New repository」をクリック
2. Repository name: `school-scraper`（任意）
3. **「Private」を選択**（コードを非公開にする）
4. 「Create repository」をクリック

### 3. ファイルをアップロード

1. リポジトリのページで「uploading an existing file」をクリック
2. このフォルダ（`my_scraper`）の中身を**すべて選択してドラッグ＆ドロップ**
   - `app.py`
   - `requirements.txt`
   - `scraping/` フォルダ（中のファイルごとアップロード）
3. 「Commit changes」をクリック

> ⚠️ `*.csv` や `data/` フォルダは個人情報が含まれるためアップロードしないでください。

---

## Streamlit Community Cloudへのデプロイ方法（初回のみ）

### 1. Streamlit Cloud にサインアップ

https://share.streamlit.io にアクセスし、「Continue with GitHub」でGitHubアカウントと連携してサインアップします。

### 2. アプリをデプロイ

1. 「New app」をクリック
2. 以下を入力：
   - **Repository**: `自分のGitHubユーザー名/school-scraper`
   - **Branch**: `main`
   - **Main file path**: `app.py`
3. 「Deploy」をクリック

数分後に `https://○○.streamlit.app` のURLが発行されます。

### 3. URLを社内に共有

発行されたURLを社員にSlackやメールで共有するだけでOKです。
アプリはブラウザで動くためインストール不要です。

---

## 注意事項

- 処理中はブラウザを閉じないでください（処理がキャンセルされます）
- URL自動検索あり・100件の場合：約8〜10分（sleep=3秒×件数）
- URL自動検索なし（URL列あり）・100件の場合：約3〜5分
- URL検索がブロックされた場合は上記「URL自動検索について」を参照
- 取得できない組織は空欄になります（手動で補完してください）

## ファイル構成

```
my_scraper/
├── app.py                    # Streamlitアプリ本体
├── requirements.txt          # 必要なパッケージ一覧
├── .gitignore                # GitHubに上げないファイルの設定
└── scraping/
    ├── url_finder.py         # DuckDuckGo検索でURL取得（sleep=3秒）
    └── contact_extractor.py  # HTMLから連絡先を抽出
```