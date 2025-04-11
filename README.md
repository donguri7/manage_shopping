# 🛒 manage_shopping_web

忙しい人のために買い物支援を行うWebアプリケーション

<p align="center">
  <img width="1438" alt="Image" src="https://github.com/user-attachments/assets/40f07e1d-1db7-444e-8f49-c9120c5b2fdb" />
</p>

---

## 📌 概要

大学院生や社会人など、忙しくて買い物の在庫管理が難しい人のために、**レシート画像から購入品情報を抽出し、日用品や食料品の買い忘れを防ぐアプリ**です。

- レシートを撮影・アップロードするだけで商品を記録
- 商品の使用頻度をもとに次回の購入タイミングを予測
- 必需品の欠品を防ぐ通知＆買い物リスト自動作成

---

## 📷 利用シーン

- 食料品や洗剤など「気づいたら無くなってる」消耗品の管理
- 忙しい平日の中でもスムーズに買い物できるように準備
- まとめ買いを効率化し、買い物回数を最小限に

---

## 🛠️ 機能一覧

- [x] レシート画像アップロード
- [x] Google Cloud Vision API による商品名のOCR解析
- [x] 購入履歴の登録・管理
- [x] 使用頻度をもとにした在庫切れ予測

---

## 🧑‍💻 使用技術

- **バックエンド**: Python, Flask
- **OCR処理**: Google Cloud Vision API
- **データベース**: SQLite（将来的にPostgreSQL等にも対応予定）
- **デプロイ**: Heroku

---

## 🌐 デモ（Heroku）

[アプリを開く](https://mani-shop-web-14e12abc7a0a.herokuapp.com/)

---

## 🚀 セットアップ方法

```bash
# 1. リポジトリをクローン
git clone https://github.com/donguri7/manage_shopping.git
cd manage_shopping

# 2. 仮想環境の作成と有効化（必要に応じて）
python -m venv venv
source venv/bin/activate  # Windowsなら venv\Scripts\activate

# 3. 依存パッケージのインストール
pip install -r requirements.txt

# 4. 環境変数を設定（Google Cloudの認証キー）
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credential.json"

# 5. アプリを起動
python run.py
