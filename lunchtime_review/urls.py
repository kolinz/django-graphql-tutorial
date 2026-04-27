# ファイルパス: lunchtime_review/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from strawberry.django.views import GraphQLView
from lunch.schema import schema

DEFAULT_QUERY = """\
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
}"""

_ESCAPED = DEFAULT_QUERY.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

GRAPHIQL_HTML = f"""\
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GraphiQL | LunchTime Review</title>
  <link rel="stylesheet" href="https://unpkg.com/graphiql@3/graphiql.min.css">
  <style>
    body {{ margin: 0; height: 100vh; display: flex; flex-direction: column; }}
    #graphiql {{ flex: 1; }}
  </style>
</head>
<body>
  <div id="graphiql"></div>
  <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="https://unpkg.com/graphiql@3/graphiql.min.js"></script>
  <script>
    const DEFAULT_QUERY = `{_ESCAPED}`;

    // GraphiQL が起動時に localStorage から読み込むため、
    // 事前にサンプルクエリをセットしておく
    localStorage.setItem('graphiql:query', DEFAULT_QUERY);
    window.history.replaceState({{}}, '', '/graphql/');

    const fetcher = GraphiQL.createFetcher({{ url: '/graphql/' }});
    ReactDOM.createRoot(document.getElementById('graphiql')).render(
      React.createElement(GraphiQL, {{ fetcher: fetcher }})
    );
  </script>
</body>
</html>"""

_gql_handler = csrf_exempt(GraphQLView.as_view(schema=schema, graphql_ide=None))


@login_required
@csrf_exempt
def graphql_view(request):
    if request.method == 'GET':
        return HttpResponse(GRAPHIQL_HTML, content_type='text/html')
    return _gql_handler(request)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('lunch.urls')),
    path('graphql/', graphql_view, name='graphql'),
]
