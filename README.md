# 学校連絡先スクレイパー

学校名のCSVをアップロードするだけで、電話番号・FAX・メールアドレス・住所を自動取得するWebアプリです。

## 使い方（アプリ利用者向け）

1. ブラウザでアプリのURLを開く
2. 学校名が入ったCSVをアップロード
3. 「処理開始」ボタンを押す（処理中はブラウザを閉じない）
4. 完了したら「CSVをダウンロード」

### CSVファイルの形式

Excelで作成する場合は「名前を付けて保存 → CSV UTF-8（コンマ区切り）」を選んでください。

| 学校名 |
|--------|
| ○○高等学校 |
| △△高校 |

URLがすでにある場合は列として含めておくと、Google検索をスキップできて高速になります。

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
- 大量の学校（100件以上）は処理に数十分かかる場合があります
- Google検索を使うため、短時間に多数のリクエストを送るとブロックされることがあります。その場合は時間をおいて再実行してください
- 取得できない学校は空欄になります（手動で補完してください）

## ファイル構成

```
my_scraper/
├── app.py                    # Streamlitアプリ本体
├── requirements.txt          # 必要なパッケージ一覧
├── .gitignore                # GitHubに上げないファイルの設定
└── scraping/
    ├── url_finder.py         # Google検索でURL取得
    └── contact_extractor.py  # HTMLから連絡先を抽出
```