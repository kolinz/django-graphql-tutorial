# ファイルパス: lunch/schema.py

import datetime
from typing import Annotated
import strawberry
import strawberry_django
from strawberry import auto
from strawberry.types import Info
from django.contrib.auth.models import User
from .models import LunchPlace, Review


# ─── 型定義 ───────────────────────────────────────────────

@strawberry_django.type(User)
class UserType:
    username: auto


# LunchPlaceType との循環参照を前方参照で回避
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


# ─── Query ───────────────────────────────────────────────

@strawberry.type
class Query:

    @strawberry.field
    def lunch_places(
        self,
        info: Info,
        lunch_start: datetime.time,
        lunch_end: datetime.time,
    ) -> list[LunchPlaceType]:
        """承認済みの昼食先一覧を返す"""
        return LunchPlace.objects.filter(is_approved=True)

    @strawberry.field
    def lunch_place(
        self,
        info: Info,
        id: strawberry.ID,
        lunch_end: datetime.time,
    ) -> LunchPlaceType | None:
        """承認済みの昼食先1件を返す。未承認または存在しない場合は None"""
        try:
            return LunchPlace.objects.get(pk=id, is_approved=True)
        except LunchPlace.DoesNotExist:
            return None

    @strawberry.field
    def my_reviews(self, info: Info) -> list[ReviewType]:
        """ログインユーザー自身のレビュー一覧を返す。未ログインはエラー"""
        user = info.context.request.user
        if not user.is_authenticated:
            raise PermissionError("ログインが必要です。")
        return Review.objects.filter(author=user).select_related("lunch_place")


# ─── Mutation ────────────────────────────────────────────

@strawberry.type
class Mutation:

    @strawberry.mutation
    def create_lunch_place(
        self,
        info: Info,
        name: str,
        location: str,
        lunch_end_time: datetime.time,
        estimated_time_minutes: int,
    ) -> LunchPlaceType:
        """
        昼食先を登録する。
        - 管理者（is_staff=True）は即時承認
        - 一般ユーザーは承認待ち（is_approved=False）
        """
        user = info.context.request.user
        if not user.is_authenticated:
            raise PermissionError("ログインが必要です。")

        is_approved = user.is_staff
        place = LunchPlace.objects.create(
            name=name,
            location=location,
            lunch_end_time=lunch_end_time,
            estimated_time_minutes=estimated_time_minutes,
            is_approved=is_approved,
            created_by=user,
        )
        return place

    @strawberry.mutation
    def create_review(
        self,
        info: Info,
        lunch_place_id: strawberry.ID,
        rating: int,
        comment: str,
    ) -> ReviewType:
        """
        レビューを投稿する。
        - rating は 1〜5 の範囲でなければならない
        """
        user = info.context.request.user
        if not user.is_authenticated:
            raise PermissionError("ログインが必要です。")

        if not (1 <= rating <= 5):
            raise ValueError(f"rating は 1〜5 で指定してください（指定値: {rating}）")

        try:
            place = LunchPlace.objects.get(pk=lunch_place_id, is_approved=True)
        except LunchPlace.DoesNotExist:
            raise ValueError(f"昼食先 id={lunch_place_id} が見つかりません。")

        review = Review.objects.create(
            author=user,
            lunch_place=place,
            rating=rating,
            comment=comment,
        )
        return review


# ─── スキーマ ─────────────────────────────────────────────

schema = strawberry.Schema(query=Query, mutation=Mutation)
