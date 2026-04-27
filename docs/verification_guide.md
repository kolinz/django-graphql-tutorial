# LunchTime Review 動作確認手順書

本手順書は **LunchTime Review** の動作確認を行うための手順書です。  
WSL2（Ubuntu）上での操作を前提としています。

---

## 1. セットアップ手順

> ⚠️ **以降の操作はすべて WSL（Ubuntu）のターミナルで実行してください。**

### 1-1. Python 3.12 のインストール

Ubuntu の標準リポジトリには Python 3.12 が含まれていない場合があります。  
`deadsnakes` PPA を使ってインストールします。

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev
```

インストール完了後、バージョンを確認します。

```bash
python3.12 --version
```

`Python 3.12.x` と表示されれば成功です。

---

### 1-2. リポジトリをクローンする

```bash
cd ~
git clone https://github.com/kolinz/django-graphql-tutorial.git lunchtime_review
cd lunchtime_review
```

---

### 1-3. 仮想環境（venv）を作成して有効化する

```bash
python3.12 -m venv venv
source venv/bin/activate
```

プロンプトの先頭に `(venv)` が表示されていることを確認してください。

```
(venv) yourname@DESKTOP:~/lunchtime_review$
```

> 💡 ターミナルを新しく開いたときは、毎回 `source venv/bin/activate` を実行してから作業してください。

---

### 1-4. `.env` ファイルを作成する

リポジトリに含まれている `env.example` をコピーして `.env` を作成します。

```bash
cp env.example .env
```

`.env` をテキストエディタで開き、`DJANGO_SECRET_KEY` に任意の秘密鍵を設定してください。

```bash
# VS Code で開く場合
code .env
```

`.env` の内容例：

```
DJANGO_SECRET_KEY=ここに任意の長いランダム文字列を設定する
DJANGO_DEBUG=True
```

> ⚠️ `.env` は Git 管理対象外です。他人に見せたり GitHub に上げたりしないでください。

---

### 1-5. パッケージをインストールする

```bash
pip install -r requirements.txt
```

---

### 1-6. マイグレーションを実行する

```bash
python manage.py migrate
```

以下のように表示されれば成功です。

```
Running migrations:
  Applying lunch.0001_initial... OK
  ...
```

> 💡 `makemigrations` はモデルを変更したときに開発者が実行するコマンドです。
> クローン後のセットアップでは `migrate` だけで OK です。

---

### 1-7. 初期データをロードする

```bash
python manage.py loaddata initial_data
```

`Installed 9 object(s) from 1 fixture(s)` と表示されれば成功です。

---

### 1-8. 開発サーバーを起動する

```bash
python manage.py runserver
```

以下が表示されれば起動成功です。

```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Windows 側のブラウザで `http://localhost:8000/` にアクセスしてください。

---

## 2. 動作確認チェックリスト

### テスト用アカウント

| ユーザー名 | パスワード | 権限 | 用途 |
|-----------|-----------|------|------|
| `admin` | `admin1234` | 管理者（スーパーユーザー） | Django Admin・承認操作 |
| `tanaka` | `student1234` | 一般ユーザー | ログイン・レビュー投稿・GraphiQL 操作 |
| `yamada` | `student1234` | 一般ユーザー | 複数ユーザーのテスト用 |

各項目を順番に確認し、問題なければ ✅ を付けてください。

| # | 確認項目 | 操作手順 | 期待される結果 |
|---|---------|---------|--------------|
| 1 | トップページ表示 | ログイン後、`http://localhost:8000/` にアクセスする | 昼食先一覧が表示され、学食 A棟・ラーメン 龍・カフェ サンライズの3件が表示される |
| 2 | canMakeIt 判定（正） | トップページの昼休み終了を `13:00` にして検索する | 学食 A棟（20分）・カフェ サンライズ（25分）に「✓ 間に合う」バッジが表示される |
| 3 | canMakeIt 判定（否） | トップページの昼休み終了を `12:30` にして検索する | ラーメン 龍（35分）に「✗ 難しい」バッジが表示される |
| 4 | 詳細表示 | ログイン後、一覧からいずれかのカードをクリックする | 昼食先の詳細（所要時間・ランチ終了時刻・判定・レビュー）が表示される |
| 5 | ログイン | `http://localhost:8000/accounts/login/` にアクセスし `tanaka` / `student1234` でログインする | ナビバーに「ログイン中：tanaka」と表示され、トップページにリダイレクトされる |
| 6 | レビュー投稿 | 詳細画面下部の「レビューを投稿する」をクリックし、評価とコメントを入力して投稿する | 「レビューを投稿しました！」と表示され、詳細画面に戻る。レビューが追加されている |
| 7 | 昼食先登録（一般） | ナビバーの「昼食先を登録する」から店名・場所・時刻・所要時間を入力して登録する | 「登録しました！承認後に公開されます。」と表示される。一覧には表示されない（承認待ち） |
| 8 | 承認（管理者） | `http://localhost:8000/admin/` に `admin` / `admin1234` でログインし、登録した昼食先の「承認済み」にチェックを入れて保存する | 承認後、一覧に表示されるようになる |
| 9 | GraphiQL アクセス | `http://localhost:8000/graphql/` にアクセスする | GraphiQL の画面が開き、授業用4ステップのサンプルクエリが初期表示される |
| 10 | GraphiQL Step1 実行 | GraphiQL で `Step1_GetLunchPlaces` クエリを選択して実行する | 承認済み昼食先の一覧が JSON で返される。`canMakeIt` の値が含まれる |
| 11 | GraphiQL Step4 実行 | GraphiQL で `Step4_CreateReview` Mutation を実行する | レビューが作成され、`id` が返される |
| 12 | 未ログイン GraphiQL | ログアウト後に `http://localhost:8000/graphql/` にアクセスする | ログイン画面にリダイレクトされる（GraphiQL は表示されない） |
| 13 | 開発サーバーの停止 | ターミナル画面で、Ctrl + cキーを押す | プロンプトの先頭に `(venv)` が表示されている状態になる |
| 14 | 仮想環境(venv)の無効化 | ターミナル画面で、deactivate と入力しEnterキーを押す | プロンプトの先頭から `(venv)` が外れる |

---

## 3. よくあるエラーと対処

### ModuleNotFoundError: No module named 'strawberry_django'

**原因：** `pip install -r requirements.txt` が完了していない。

**対処：**

```bash
source venv/bin/activate
pip install -r requirements.txt
```

venv が有効化されている（プロンプトに `(venv)` が表示されている）状態で実行してください。

---

### ValueError: 環境変数 DJANGO_SECRET_KEY が設定されていません

**原因：** `.env` ファイルが作成されていないか、`DJANGO_SECRET_KEY` が未設定です。

**対処：**

```bash
cp env.example .env
code .env  # DJANGO_SECRET_KEY に値を設定して保存する
```

---

### GraphQL で Time 型のエラーが出る

**エラー例：** `Expected type 'Time', found "13:00"`

**原因：** Time 型の値は `HH:MM:SS` 形式（秒まで）で指定する必要があります。

**対処：** GraphiQL でクエリを実行する際は、時刻を以下の形式で入力してください。

```graphql
# ❌ 誤り
lunchPlaces(lunchStart: "12:00", lunchEnd: "13:00")

# ✅ 正しい
lunchPlaces(lunchStart: "12:00:00", lunchEnd: "13:00:00")
```

---

### SynchronousOnlyOperation エラーが出る

**エラー例：** `SynchronousOnlyOperation: You cannot call this from an async context`

**原因：** `GraphQLView` に非同期版（`AsyncGraphQLView`）が使われています。

**対処：** `lunchtime_review/urls.py` の import を確認し、以下のように **同期版** を使用してください。

```python
# ❌ 誤り
from strawberry.django.views import AsyncGraphQLView

# ✅ 正しい
from strawberry.django.views import GraphQLView
```

---

### canMakeIt が常に false になる

**原因：** `settings.py` の `TIME_ZONE` が正しく設定されていないため、現在時刻の判定がずれています。

**対処：** `lunchtime_review/settings.py` を開き、以下の設定を確認してください。

```python
TIME_ZONE = 'Asia/Tokyo'
USE_TZ = True
```

設定変更後、サーバーを再起動してください（`Ctrl+C` で停止 → `python manage.py runserver` で再起動）。
