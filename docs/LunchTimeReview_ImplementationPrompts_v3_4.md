# LunchTime Review 実装プロンプト集 v3.4

Claude.ai に順番に貼り付けて使用する。  
**各 Step は前の Step の出力が存在する前提**で書かれている。

---

## 使い方

1. Claude.ai で **Project を作成**する
2. `LunchTimeReview_ProjectPrompt_v3.4.md` をカスタム指示に貼り付ける
3. `SDD_LunchTimeReview_v3.4.md` をナレッジに追加する
4. **Step 0 の手順に従い、WSL2 上で開発環境を構築する**（Claude へのプロンプト不要。ターミナル操作のみ）
5. Step 1 から順に、各プロンプトを Claude に貼り付ける
6. 各 Step の完了後、ダウンロードしたファイルを VS Code で開いたプロジェクトに配置する

---

## Step 0 ： 開発環境の構築（ターミナル操作のみ・Claude 不要）

> ⚠️ **以降の操作はすべて WSL（Ubuntu）のターミナルで実行してください。**  
> Windows の PowerShell やコマンドプロンプトでは動作しません。

### 0-1. WSL2 の確認

Windows の PowerShell を開き、以下を実行して WSL2 が有効になっているか確認します。

```powershell
wsl --list --verbose
```

`VERSION` 列に `2` と表示されていれば OK です。  
表示されない場合は担当教員に相談してください。

---

### 0-2. Ubuntu のターミナルを開く

スタートメニューから「Ubuntu」を起動するか、Windows Terminal から Ubuntu を選択してください。  
**以降の手順はすべて Ubuntu のターミナルで実行します。**

---

### 0-3. Python 3.12 のインストール

Ubuntu の標準リポジトリには Python 3.12 が含まれていない場合があります。  
`deadsnakes` PPA を使ってインストールします。

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev
```

途中で `[Enter]` キーの入力を求められた場合は Enter を押してください。  
インストール完了後、バージョンを確認します。

```bash
python3.12 --version
```

`Python 3.12.x` と表示されれば成功です。

---

### 0-4. プロジェクトディレクトリの作成と venv のセットアップ

```bash
cd ~
mkdir lunchtime_review
cd lunchtime_review
```

Python 3.12 を指定して仮想環境（venv）を作成します。

```bash
python3.12 -m venv venv
```

venv を有効化します。

```bash
source venv/bin/activate
```

**成功すると、プロンプトの先頭に `(venv)` が表示されます。**

```
(venv) yourname@DESKTOP:~/lunchtime_review$
```

> 💡 ターミナルを新しく開いたときは、毎回 `source venv/bin/activate` を実行してから作業してください。

pip を最新版にアップグレードします。

```bash
pip install --upgrade pip
```

---

### 0-5. Django のインストールとプロジェクト骨格の作成

> ✅ **以降の手順はすべて `(venv)` が表示されている状態で実行してください。**

まず Django だけを先にインストールします（`requirements.txt` は Step 1 で生成します）。

```bash
pip install "Django>=5.2,<6.0"
```

Django プロジェクトを作成します（末尾の `.` を忘れずに）。

```bash
django-admin startproject lunchtime_review .
```

> ⚠️ 末尾の `.`（ドット）は「現在のディレクトリをプロジェクトルートにする」指定です。省略しないでください。

`lunch` アプリを作成します。

```bash
python manage.py startapp lunch
```

fixtures ディレクトリを作成します。

```bash
mkdir -p lunch/fixtures
```

---

### 0-6. ディレクトリ構成の確認

```bash
ls -la
```

以下の構成になっていれば Step 0 は完了です。

```
lunchtime_review/          ← 作業ルート（現在地）
├── manage.py              ← django-admin が自動生成
├── lunchtime_review/      ← Django プロジェクト設定フォルダ
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── lunch/                 ← Django アプリ
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── tests.py
    ├── views.py
    └── fixtures/          ← mkdir -p で作成したもの
```

---

### 0-7. VS Code でプロジェクトを開く

以降の Step でダウンロードしたファイルを配置するときは **VS Code** を使うと便利です。  
以下のコマンドを実行すると、WSL 上のプロジェクトフォルダを Windows の VS Code で開けます。

```bash
code .
```

> 💡 初回実行時は VS Code Server のインストールが自動で行われます。完了すると Windows 側に VS Code が起動します。  
> `code` コマンドが見つからない場合は、Windows 側で VS Code をインストールし「WSL」拡張機能を追加してから再試行してください。

VS Code が開いたら、左サイドバーのエクスプローラーでファイルツリーが確認できます。  
各 Step でダウンロードしたファイルは、ここにドラッグ＆ドロップするか、既存ファイルを開いて内容を貼り付けて上書き保存してください。

**Step 1 のプロンプトを Claude に貼り付けて**実装を開始してください。

---

## Step 1 ： プロジェクト初期化・Models・Admin・初期データ

### ファイルの配置について

Claude がファイルを生成したら、ダウンロードして以下のパスに配置してください。  
VS Code のエクスプローラーで対象ファイルを開き、内容をそのまま貼り付けて上書き保存するのが確実です。

| ファイル | 配置先パス |
|---|---|
| `requirements.txt` | `~/lunchtime_review/requirements.txt` |
| `settings.py` | `~/lunchtime_review/lunchtime_review/settings.py` |
| `urls.py` | `~/lunchtime_review/lunchtime_review/urls.py` |
| `models.py` | `~/lunchtime_review/lunch/models.py` |
| `admin.py` | `~/lunchtime_review/lunch/admin.py` |
| `initial_data.json` | `~/lunchtime_review/lunch/fixtures/initial_data.json` |
| `.env` | `~/lunchtime_review/.env` |
| `manage.py` | `~/lunchtime_review/manage.py` |

配置後、ターミナルで以下を実行してください。

```bash
pip install -r requirements.txt
python manage.py makemigrations lunch
python manage.py migrate
python manage.py loaddata initial_data
python manage.py runserver
```

`http://localhost:8000/admin/` で Django Admin が開けば Step 1 完了です。  
`http://localhost:8000/` は Step 3 完了後まで 404 になります（正常な挙動です）。

### Claude へのプロンプト

```
以下の仕様に従い、Django プロジェクト「lunchtime_review」の初期実装を行ってください。
仕様の詳細は SDD Section 3・6 を参照してください。

## 出力形式

コードブロックでの表示は不要です。
以下のファイルをそれぞれ実際のファイルとして作成し、ダウンロードできる状態にしてください。

## 作成するファイル

1. requirements.txt
2. lunchtime_review/settings.py
3. lunchtime_review/urls.py（仮版。lunch.urls と GraphQL エンドポイントは Step 3・4 で追加）
4. lunch/models.py
5. lunch/admin.py
6. lunch/fixtures/initial_data.json
7. .env（ローカル開発用の環境変数ファイル）
8. manage.py（python-dotenv の load_dotenv() を追加したもの）

## 仕様

### 実行環境

- Python 3.12 / WSL2 + Ubuntu / Django 5.2

### requirements.txt

- Django>=5.2,<6.0
- strawberry-graphql-django
- python-dotenv

### settings.py

- SECRET_KEY は os.environ.get('DJANGO_SECRET_KEY') で読み込む。未設定時は ValueError を送出する
- DEBUG は os.environ.get('DJANGO_DEBUG', 'False') == 'True' で読み込む
- INSTALLED_APPS に "strawberry_django" と "lunch" を追加する
- LANGUAGE_CODE = 'ja'
- TIME_ZONE = 'Asia/Tokyo'
- USE_TZ = True
- LOGIN_URL = '/accounts/login/'
- LOGIN_REDIRECT_URL = '/'

### urls.py（仮版）

- urlpatterns には admin/ と accounts/ のみ含める
- include('lunch.urls') は含めない（lunch/urls.py は Step 3 で作成するため）

### .env

- DJANGO_SECRET_KEY にランダムな秘密鍵を設定する
- DJANGO_DEBUG=True を設定する

### manage.py

- 先頭に from dotenv import load_dotenv と load_dotenv() を追加する

### models.py・admin.py・fixtures

SDD Section 6 のモデル定義に従って実装すること。
fixtures には管理者・一般ユーザー・承認済み昼食先3件・承認待ち1件・レビュー3件を含めること。

## 注意事項

- User モデルは拡張しない
- マイグレーションファイルは作成しない
- 出力されるファイルは `django-admin startproject` で作成済みの骨格に上書きする前提
```

---

## Step 2 ： Strawberry スキーマ・Resolver

### ファイルの配置について

| ファイル | 配置先パス |
|---|---|
| `schema.py` | `~/lunchtime_review/lunch/schema.py` |

配置後、ターミナルで以下を実行してエラーが出ないことを確認してください。

```bash
python manage.py check
```

### Claude へのプロンプト

```
以下の仕様に従い、GraphQL スキーマを実装してください。
仕様の詳細は SDD Section 7 を参照してください。

## 出力形式

コードブロックでの表示は不要です。
以下のファイルを実際のファイルとして作成し、ダウンロードできる状態にしてください。

## 作成するファイル

1. lunch/schema.py

## 仕様

SDD Section 7.1〜7.4 に従い以下を実装すること。

### 型定義

- UserType・ReviewType・LunchPlaceType を @strawberry_django.type で定義する
- ReviewType の lunch_place は Annotated + strawberry.lazy("lunch.schema") で定義する（循環参照対策）
- LunchPlaceType に can_make_it フィールドリゾルバーを実装する（SDD Section 7.2 の実装をそのまま使う）
- LunchPlaceType に average_rating フィールドリゾルバーを実装する

### Query

- lunch_places(lunch_start, lunch_end): 承認済みのみ返す
- lunch_place(id, lunch_end): 承認済みのみ返す
- my_reviews(): ログイン必須。未ログインは PermissionError

### Mutation

- create_lunch_place(...): ログイン必須。管理者は即時承認・一般は承認待ち
- create_review(...): ログイン必須。rating 範囲外は ValueError

## 注意事項

- import datetime を使い datetime.time 等で参照すること
- strawberry.ID を使うこと
- ファイル末尾に schema = strawberry.Schema(query=Query, mutation=Mutation) を記載すること
```

---

## Step 3 ： Views・Forms・URLs・Templates

### ファイルの配置について

テンプレートディレクトリを事前に作成してから配置してください。

```bash
mkdir -p lunch/templates/lunch
mkdir -p templates/registration
```

| ファイル | 配置先パス |
|---|---|
| `views.py` | `~/lunchtime_review/lunch/views.py` |
| `forms.py` | `~/lunchtime_review/lunch/forms.py` |
| `urls.py`（lunch） | `~/lunchtime_review/lunch/urls.py` |
| `urls.py`（最終版） | `~/lunchtime_review/lunchtime_review/urls.py` |
| `base.html` | `~/lunchtime_review/lunch/templates/lunch/base.html` |
| `place_list.html` | `~/lunchtime_review/lunch/templates/lunch/place_list.html` |
| `place_detail.html` | `~/lunchtime_review/lunch/templates/lunch/place_detail.html` |
| `review_form.html` | `~/lunchtime_review/lunch/templates/lunch/review_form.html` |
| `my_reviews.html` | `~/lunchtime_review/lunch/templates/lunch/my_reviews.html` |
| `place_form.html` | `~/lunchtime_review/lunch/templates/lunch/place_form.html` |
| `login.html` | `~/lunchtime_review/templates/registration/login.html` |

配置後、`python manage.py runserver` を起動し `http://localhost:8000/` でトップページが表示されれば完了です。

### Claude へのプロンプト

```
以下の仕様に従い、Django の View・Form・URL・Template を実装してください。
仕様の詳細は SDD Section 8 を参照してください。

## 出力形式

コードブロックでの表示は不要です。
以下のファイルをそれぞれ実際のファイルとして作成し、ダウンロードできる状態にしてください。

## 作成するファイル

1. lunch/views.py
2. lunch/forms.py
3. lunch/urls.py
4. lunchtime_review/urls.py（最終版）
5. lunch/templates/lunch/base.html
6. lunch/templates/lunch/place_list.html
7. lunch/templates/lunch/place_detail.html
8. lunch/templates/lunch/review_form.html
9. lunch/templates/lunch/my_reviews.html
10. lunch/templates/lunch/place_form.html
11. templates/registration/login.html

## 仕様

### 共通

- Bootstrap 5 CDN を使用する（Mobile First）
- base.html にナビバー・CSRF meta タグ・gqlFetch 共通関数を実装する
- GraphQL の呼び出しはすべて JavaScript の fetch API で行う（サーバーサイドから直接呼ばない）
- gqlFetch はレスポンスが HTML の場合（未ログイン時のリダイレクト）を検知し、
  「ログインが必要です」とリンク付きのユーザーフレンドリーなメッセージを表示する

### 各画面の仕様

SDD Section 8.3 の画面仕様に従うこと。

- place_list: ページロード時に 12:00〜13:00 で自動検索する
- place_detail: URL の id と GET パラメータの lunchEnd をテンプレートに渡す
- review_form / place_form: フォーム submit を preventDefault して Mutation を fetch で送信する
- GraphQL クエリ・Mutation の内容は SDD Section 7.3・7.4 を参照すること

## 注意事項

- @login_required が必要なビューには必ずつける
- Bootstrap 5 のクラスを活用しカスタム CSS は最小限にする
```

---

## Step 4 ： GraphiQL 設定・動作確認手順書

### ファイルの配置について

| ファイル | 配置先パス |
|---|---|
| `urls.py`（最終版） | `~/lunchtime_review/lunchtime_review/urls.py` |
| `verification_guide.md` | `~/lunchtime_review/verification_guide.md` |

配置後、`python manage.py runserver` を起動し `http://localhost:8000/graphql/` で GraphiQL が開けば完了です。

### Claude へのプロンプト

```
以下の仕様に従い、GraphiQL の最終設定と動作確認手順書を作成してください。
仕様の詳細は SDD Section 5.6・7.5 を参照してください。

## 出力形式

コードブロックでの表示は不要です。
以下のファイルをそれぞれ実際のファイルとして作成し、ダウンロードできる状態にしてください。

## 作成するファイル

1. lunchtime_review/urls.py（GraphiQL 設定を含む最終版）
2. verification_guide.md（動作確認手順書。そのまま学生に配布できる内容）

## GraphiQL 設定仕様

- エンドポイント: /graphql/
- login_required + csrf_exempt でラップする
- GET リクエスト時はカスタム HTML（CDN 経由で GraphiQL v3 をロード）を返す
- POST リクエスト時は GraphQLView.as_view(schema=schema, graphql_ide=None) に委譲する
- localStorage.setItem('graphiql:query', DEFAULT_QUERY) でサンプルクエリを初期表示する
- SDD Section 7.5 の授業用4ステップのサンプルクエリを DEFAULT_QUERY として定義する

## verification_guide.md の内容

以下のセクションを含む Markdown を作成すること。

### 1. セットアップ手順
WSL2 Ubuntu 上でのコマンドをすべてコードブロックで記載する。
venv 作成 → pip install → makemigrations → migrate → loaddata → runserver の順。

### 2. 動作確認チェックリスト
冒頭にテスト用アカウント一覧（ユーザー名・パスワード・権限・用途）を表形式で記載する。
以下の12項目を表形式で記載する。
1. トップページ表示 / 2. canMakeIt 判定（正） / 3. canMakeIt 判定（否）
4. 詳細表示 / 5. ログイン / 6. レビュー投稿 / 7. 昼食先登録（一般）
8. 承認（管理者） / 9. GraphiQL アクセス / 10. GraphiQL Step1 実行
11. GraphiQL Step4 実行 / 12. 未ログイン GraphiQL

### 3. よくあるエラーと対処
- ModuleNotFoundError: strawberry_django
- Time 型エラー（HH:MM:SS 形式の確認）
- SynchronousOnlyOperation（同期版 GraphQLView の確認）
- canMakeIt が常に false（TIME_ZONE の確認）
- DJANGO_SECRET_KEY が設定されていない（.env ファイルの確認）

## 注意事項

- 手順書は学生がそのまま読んで操作できる丁寧な表現にすること
```

---

## 完了後のディレクトリ構成

全 Step の実装が完了したら、以下の構成になっていることを確認する。

```
lunchtime_review/
├── manage.py
├── requirements.txt
├── .env                   ← Git 管理対象外
├── env.example            ← Git 管理対象（雛形）
├── verification_guide.md
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

## GitHub 公開前のチェックリスト

| 確認項目 | 内容 |
|---|---|
| `.gitignore` に `.env` を追加 | SECRET_KEY を公開しないために必須 |
| `.gitignore` に `db.sqlite3` を追加 | 個人データを含むため |
| `.gitignore` に `venv/` を追加 | 仮想環境は各自で作成するため |
| `env.example` をコミット | 環境変数の雛形として共有 |
| `README.md` にセットアップ手順を記載 | clone 後の手順（.env 作成・pip install・migrate・loaddata）を記載 |

---

## GitHub へのファイル追加・更新手順

> ⚠️ **GitHub へのファイル追加・更新は必ずターミナルの git コマンドで行ってください。**  
> GitHub のブラウザ画面からファイルをアップロードすると `.gitignore` が無視され、
> `db.sqlite3` や `.env` などの除外すべきファイルが誤って公開されます。

### 初回：リモートリポジトリと接続して push する

GitHub でリポジトリを作成したら、WSL のターミナルで以下を実行します。

```bash
cd ~/lunchtime_review
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<ユーザー名>/<リポジトリ名>.git
git push -u origin main
```

> 💡 `git add .` を実行すると `.gitignore` に記載されたファイルは自動的に除外されます。
> `git add .` の前に `git status` を実行して、追加されるファイルを確認する習慣をつけてください。

### 2回目以降：ファイルを更新して push する

```bash
cd ~/lunchtime_review
git add .
git status        # 追加・変更されるファイルを確認する
git commit -m "変更内容の説明"
git push
```

### 誤って不要なファイルを push してしまった場合

`db.sqlite3` などを誤って push してしまった場合は以下で取り消します。

```bash
git rm --cached db.sqlite3
git commit -m "Remove db.sqlite3 from tracking"
git push
```

> ⚠️ `git rm --cached` はリポジトリからの追跡を外すだけで、ローカルのファイルは削除されません。
