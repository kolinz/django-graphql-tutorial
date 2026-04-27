# Software Design Document (SDD) v3.4

## 学生向け昼食レビューシステム
（仮称：LunchTime Review）

**Claude.ai 実装用・完成版**

---

## 改訂履歴

| バージョン | 変更内容 |
|-----------|---------|
| v1.0 | Copilot 初稿 |
| v2.0 | GraphiQL 要件追加・GraphQL 構文修正・Resolver 仕様明確化 |
| v2.1 | Section 8 UI仕様を画面ごとに具体化 |
| v3.0 | GraphQL ライブラリを Graphene-Django → Strawberry に変更 |
| v3.1 | 実装プロンプト集に Step 0（環境構築）を追加 |
| v3.2 | ReviewType に lunch_place フィールドを追加（循環参照を Annotated で解決） |
| v3.3 | SECRET_KEY を環境変数化・python-dotenv 導入・requirements.txt 更新 |
| v3.4 | ドキュメントバージョンを全ファイルで統一 |

---

## 1. システム概要

### 1.1 システム名

学生向け昼食レビューシステム（LunchTime Review）

### 1.2 目的

大学生が昼休みという限られた時間内で、

- 行って
- 食べて
- 授業に戻って来られる

昼食先を判断・共有できる Web アプリケーションを提供する。

本システムは **GraphQL（Strawberry + strawberry-graphql-django）を学習するための教材**として設計する。
授業中に学生自身が GraphiQL を操作することで、GraphQL の仕組みを体験的に習得する。

---

## 2. 想定ユーザー

| 区分 | 説明 |
|------|------|
| 学生（レビューアー） | 昼食先を閲覧・検索・レビューする。GraphiQL を操作して学習する |
| 管理者 | 昼食先の承認・管理を行う |

---

## 3. 技術スタック

| レイヤ | 技術 |
|--------|------|
| 実行環境 | Python 3.12 / WSL2 + Ubuntu |
| Backend | Django 5.2 |
| API | Strawberry + strawberry-graphql-django |
| API 管理 UI | GraphiQL（カスタム HTML・CDN 経由） |
| DB | SQLite |
| 認証 | Django 標準認証（username / password） |
| UI | Django Template + Bootstrap 5 |
| 管理画面 | Django Admin |
| 対応デバイス | PC / Smartphone（レスポンシブ） |
| 環境変数管理 | python-dotenv |

---

## 4. 設計方針（重要）

1. **昼食に間に合うかどうかは DB フラグで持たない**
2. 判定は **Strawberry のフィールドリゾルバーで動的に計算**する
3. UI は **Mobile First**
4. Django が得意なこと（認証・管理）は Django に任せる
5. GraphQL は「画面が欲しい形のデータを返す API」として使う
6. **GraphiQL は学習ツールとして正式に位置づける**（Swagger 相当）
7. スキーマは **Python の型ヒントで定義**する（Strawberry の強み）
8. **SECRET_KEY は環境変数で管理**し、コードに直書きしない

---

## 5. 機能要件

### 5.1 認証・認可

- Django 標準の認証を使用（セッションベース）
- 未ログインユーザーは閲覧のみ可能
- 管理者：`User.is_staff == True`

---

### 5.2 昼食先（LunchPlace）登録

- 管理者・レビューアーともにアプリ内画面から登録可能
- 入力項目：店名・場所・ランチ提供終了時刻・平均所要時間
- 管理者が登録 → 即時公開（`is_approved = True`）
- レビューアーが登録 → 承認待ち（`is_approved = False`）
- 承認操作は Django Admin で行う

---

### 5.3 昼食に間に合うかの判定

```
現在時刻 + 所要時間 ≤ 昼休み終了時刻
現在時刻 + 所要時間 ≤ ランチ提供終了時刻
```

この判定は **Strawberry のフィールドリゾルバー（`can_make_it`）** として提供する。DB には保存しない。

---

### 5.4 レビュー機能

- ログインユーザーのみ投稿可能
- レビュー項目：評価（1〜5）・コメント
- 投稿後の編集・削除は行わない（v1）

---

### 5.5 自分のレビュー管理

- ログインユーザーは自分のレビュー一覧を確認可能
- 他人のレビュー詳細には直接アクセス不可

---

### 5.6 GraphiQL（学習用 API 管理 UI）

- エンドポイント：`/graphql/`
- ログインユーザーのみアクセス可
- スキーマのブラウズ・クエリ実行・変数入力・レスポンス確認
- 授業用4ステップのサンプルクエリを初期表示
- 実装：カスタム HTML（CDN 経由で GraphiQL v3 をロード）・GET/POST 分離ビュー

---

## 6. データ設計（Django Models）

### 6.1 LunchPlace

```python
class LunchPlace(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    lunch_end_time = models.TimeField(
        help_text="ランチ提供終了時刻"
    )
    estimated_time_minutes = models.PositiveIntegerField(
        help_text="往復・提供・食事を含めた平均所要時間（分）"
    )
    is_approved = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_lunch_places"
    )
```

### 6.2 Review

```python
class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    lunch_place = models.ForeignKey(
        LunchPlace, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveIntegerField()  # 1〜5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 7. GraphQL API 設計（Strawberry）

### 7.1 スキーマ設計方針

- 型定義は **Python の型ヒント** + `@strawberry.type` デコレーターで行う
- `@strawberry_django.type(Model)` でモデルフィールドを自動マッピングする
- `can_make_it` はフィールド引数 `lunch_end: datetime.time` を受け取るリゾルバーとして定義する
- 未承認（`is_approved=False`）はリゾルバーレベルで除外する
- `ReviewType` の `lunch_place` は `Annotated` + `strawberry.lazy()` で循環参照を解決する

### 7.2 型定義（schema.py）

```python
import datetime
from typing import Annotated
import strawberry
import strawberry_django
from strawberry import auto
from strawberry.types import Info
from django.contrib.auth.models import User

@strawberry_django.type(User)
class UserType:
    username: auto

@strawberry_django.type(Review)
class ReviewType:
    id: auto
    rating: auto
    comment: auto
    created_at: auto
    author: UserType
    lunch_place: Annotated["LunchPlaceType", strawberry.lazy("lunch.schema")]

@strawberry_django.type(LunchPlace)
class LunchPlaceType:
    id: auto
    name: auto
    location: auto
    lunch_end_time: auto
    estimated_time_minutes: auto
    reviews: list[ReviewType]

    @strawberry.field(description="指定した昼休み終了時刻までに間に合うかどうか")
    def can_make_it(self, lunch_end: datetime.time) -> bool:
        now = datetime.datetime.now().time()
        base = datetime.datetime.combine(datetime.date.today(), now)
        finish = (base + datetime.timedelta(minutes=self.estimated_time_minutes)).time()
        return finish <= lunch_end and finish <= self.lunch_end_time

    @strawberry.field
    def average_rating(self) -> float | None:
        reviews = self.reviews.all()
        if not reviews.exists():
            return None
        return sum(r.rating for r in reviews) / reviews.count()
```

**注意：`can_make_it` はフィールド引数を持つリゾルバーとして定義する。**
これにより GraphiQL 上でフィールドごとに引数を確認・入力できる。

### 7.3 Query

```graphql
query GetLunchPlaces($lunchStart: Time!, $lunchEnd: Time!) {
  lunchPlaces(lunchStart: $lunchStart, lunchEnd: $lunchEnd) {
    id
    name
    location
    lunchEndTime
    estimatedTimeMinutes
    averageRating
    canMakeIt(lunchEnd: $lunchEnd)
  }
}
```

```graphql
query GetLunchPlace($id: ID!, $lunchEnd: Time!) {
  lunchPlace(id: $id, lunchEnd: $lunchEnd) {
    name
    location
    lunchEndTime
    estimatedTimeMinutes
    canMakeIt(lunchEnd: $lunchEnd)
    reviews {
      rating
      comment
      author { username }
    }
  }
}
```

```graphql
query GetMyReviews {
  myReviews {
    id
    rating
    comment
    lunchPlace { name }
    createdAt
  }
}
```

### 7.4 Mutation

```graphql
mutation CreateLunchPlace(
  $name: String!, $location: String!,
  $lunchEndTime: Time!, $estimatedTimeMinutes: Int!
) {
  createLunchPlace(
    name: $name, location: $location,
    lunchEndTime: $lunchEndTime, estimatedTimeMinutes: $estimatedTimeMinutes
  ) {
    id
    name
  }
}
```

```graphql
mutation CreateReview($lunchPlaceId: ID!, $rating: Int!, $comment: String!) {
  createReview(lunchPlaceId: $lunchPlaceId, rating: $rating, comment: $comment) {
    id
  }
}
```

### 7.5 授業向け GraphiQL 初期クエリ

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

---

## 8. UI 設計

### 8.1 共通方針

- Bootstrap 5 使用・Mobile First
- カスタム CSS は最小限
- 全画面で Bootstrap のグリッドを使いレスポンシブ対応
- 未ログイン時の GraphQL エラーはユーザーフレンドリーなメッセージで表示

---

### 8.2 画面一覧

| # | 画面名 | URL | 認証 |
|---|--------|-----|------|
| 1 | 昼食先一覧 | `/` | 不要 |
| 2 | 昼食先詳細 | `/places/<id>/` | 不要 |
| 3 | レビュー投稿 | `/places/<id>/review/` | 必要 |
| 4 | 自分のレビュー一覧 | `/myreviews/` | 必要 |
| 5 | 昼食先登録 | `/places/new/` | 必要 |
| 6 | GraphiQL | `/graphql/` | 必要 |

---

### 8.3 画面仕様

#### 画面1：昼食先一覧

- 時間入力：`<input type="time">` × 2、GET パラメータで `lunchStart` / `lunchEnd` を渡す
- `canMakeIt = true`：緑バッジ「✓ 間に合う」
- `canMakeIt = false`：赤バッジ「✗ 難しい」
- 未ログイン時：「ログインが必要です」リンク付きメッセージを表示
- カードクリックで詳細画面へ

#### 画面2：昼食先詳細

- 4カードグリッドでランチ終了時刻・所要時間・平均評価・今日の判定を表示
- レビュー一覧
- ログイン時のみ「レビューを投稿する」ボタンを表示

#### 画面3：レビュー投稿

- 評価（★1〜★5）・コメント入力
- fetch API で Mutation を送信

#### 画面4：自分のレビュー一覧

- カードリスト形式・`created_at` を `Y-m-d` 形式で表示・ログイン必須

#### 画面5：昼食先登録

- 店名・場所・ランチ終了時刻・所要時間（分）
- 管理者以外は承認待いメッセージを表示

#### 画面6：GraphiQL

- エンドポイント：`/graphql/`
- ログイン必須（未ログインはログイン画面へリダイレクト）
- カスタム HTML で GraphiQL v3 を CDN からロード
- localStorage にサンプルクエリをセットして初期表示
- GET（IDE 表示）と POST（GraphQL 処理）を分離した関数ビューで実装

---

### 8.4 ナビゲーション

```
[LunchTime Review]  昼食先を探す | 昼食先を登録する | マイレビュー | GraphiQL | ログアウト
```

---

## 9. 将来拡張（学生課題として実施）

- 通知機能・地図連携・SNS 連携
- レビュー編集・削除（投稿者）

---

## 10. 非機能要件

- 同時接続・高負荷対応は考慮しない
- DB は SQLite のみ使用
- セキュリティは Django 標準に委ねる
- SECRET_KEY は環境変数で管理する

---

## 11. 実装上の注意（Claude 向け）

- `User` モデルは拡張しない
- `can_make_it` の判定は **必ずフィールドリゾルバーで実装**（DB フラグ禁止）
- `can_make_it` の `lunch_end` 引数は **フィールド引数**として定義する
- 未承認の昼食先はリゾルバーレベルで除外する
- GraphiQL は `login_required` でラップする
- View は同期版 `GraphQLView`（`strawberry.django.views`）を使用する
- GraphQL の呼び出しは Django Template 上の **fetch API（JavaScript）** で行う
- `ReviewType` の `lunch_place` は `Annotated` + `strawberry.lazy("lunch.schema")` で定義する
- `SECRET_KEY` は `os.environ.get()` で読み込み、未設定時は `ValueError` を送出する
- GraphiQL は GET/POST 分離の関数ビューで実装し、GET はカスタム HTML を返す

---

## 12. 設計思想の要約

> 本システムは
> **学生の昼休みという現実的制約から API を設計し、
> GraphQL の強み（派生データ・柔軟な取得）を体験的に学ぶ教材**
> として設計されている。
>
> Strawberry を採用することで、**Python の型ヒントと GraphQL スキーマの対応**を
> 学生が視覚的に理解できる構成とする。
>
> GraphiQL は Swagger 相当の API 管理 UI として正式に位置づけ、
> 授業中に学生が自らクエリを発行・確認することで
> 「なぜ REST ではなく GraphQL か」を実感できる設計とする。
