# django-graphql-tutorial

Django + Strawberry（strawberry-graphql-django）を使い、GraphQLを動かすフロントの環境「GraphiQL」を Swagger相当の学習UI として活用します。

## 🍱 LunchTime Review

大学生向け **GraphQL 学習教材** として設計された昼食レビュー Web アプリケーションです。  

## 概要

昼休みという限られた時間内に「行って・食べて・授業に戻れる」昼食先を学生同士が共有するシステムです。  
授業中に学生が GraphiQL を操作することで、GraphQL の仕組みを体験的に習得します。

---

## 技術スタック

| レイヤ | 技術 |
|--------|------|
| 実行環境 | Python 3.12 / Ubuntu , 開発時は、Python 3.12 / WSL2+Ubuntu|
| Backend | Django 5.2 |
| API | Strawberry + strawberry-graphql-django |
| API 管理 UI | GraphiQL（カスタム HTML・CDN 経由） |
| DB | SQLite |
| 認証 | Django 標準認証（セッションベース） |
| UI | Django Template + Bootstrap 5 |
| 環境変数管理 | python-dotenv |

---

## セットアップ

詳細な手順・テスト用アカウント・動作確認チェックリストは  
👉 **[docs/verification_guide.md](https://github.com/kolinz/django-graphql-tutorial/blob/main/docs/verification_guide.md)** を参照してください。

---

## 画面一覧

| 画面 | URL | 認証 |
|------|-----|------|
| 昼食先一覧 | `/` | 必要 |
| 昼食先詳細 | `/places/<id>/` | 必要 |
| レビュー投稿 | `/places/<id>/review/` | 必要 |
| 自分のレビュー一覧 | `/myreviews/` | 必要 |
| 昼食先登録 | `/places/new/` | 必要 |
| GraphiQL | `/graphql/` | 必要 |
| Django Admin | `/admin/` | 管理者のみ |

---

## GraphQLを動かすフロントの環境「GraphiQL」の使い方（授業向け）

`http://localhost:8000/graphql/` にログイン済みの状態でアクセスすると GraphiQL が開きます。  
画面には授業用の4ステップのサンプルクエリが初期表示されています。

```graphql
# ステップ1: 昼食先の一覧を取得する
query Step1_GetLunchPlaces {
  lunchPlaces(lunchStart: "12:00:00", lunchEnd: "13:00:00") {
    id
    name
    location
    averageRating
    canMakeIt(lunchEnd: "13:00:00")
  }
}

# ステップ2: 特定の昼食先の詳細とレビューを取得する
query Step2_GetLunchPlaceDetail {
  lunchPlace(id: "1", lunchEnd: "13:00:00") {
    name
    lunchEndTime
    estimatedTimeMinutes
    canMakeIt(lunchEnd: "13:00:00")
    reviews {
      rating
      comment
      author { username }
    }
  }
}

# ステップ3: 自分のレビューを確認する（要ログイン）
query Step3_MyReviews {
  myReviews {
    id
    rating
    comment
    lunchPlace { name }
    createdAt
  }
}

# ステップ4: レビューを投稿する（要ログイン）
mutation Step4_CreateReview {
  createReview(
    lunchPlaceId: "1"
    rating: 4
    comment: "ランチが美味しかったです"
  ) {
    id
  }
}
```

> 💡 Time 型の引数は `HH:MM:SS` 形式（秒まで）で入力してください。

---

## ディレクトリ構成

```
lunchtime_review/
├── manage.py
├── requirements.txt
├── .env                   ← Git 管理対象外（env.example をコピーして作成）
├── env.example
├── docs/
│   └── verification_guide.md
├── lunchtime_review/
│   ├── settings.py
│   └── urls.py
├── templates/
│   └── registration/
│       └── login.html
└── lunch/
    ├── models.py
    ├── schema.py
    ├── views.py
    ├── forms.py
    ├── urls.py
    ├── admin.py
    ├── fixtures/
    │   └── initial_data.json
    └── templates/
        └── lunch/
            ├── base.html
            ├── place_list.html
            ├── place_detail.html
            ├── review_form.html
            ├── my_reviews.html
            └── place_form.html

```
---

## SDD（仕様駆動開発）のためのドキュメント

このアプリケーションは、SDD（仕様駆動開発）により開発しています。SDDのための各種ドキュメントは下記になります。

| ドキュメント | 説明 |
|---|---|
| [システム仕様書](docs/SDD_LunchTimeReview_v3_4.md) | アーキテクチャ・データモデル・API・画面仕様の全詳細 |
| [実装プロンプト集](docs/LunchTimeReview_ImplementationPrompts_v3_4.md) | AI コーディングアシスタント向け実装プロンプト |
| [プロジェクトプロンプト](docs/LunchTimeReview_ProjectPrompt_v3_4.md) | 生成AIで実装する際に用いるシステムプロンプトのこと |

---

## ライセンス

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
