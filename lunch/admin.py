# ファイルパス: lunch/admin.py

from django.contrib import admin
from .models import LunchPlace, Review


@admin.register(LunchPlace)
class LunchPlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'lunch_end_time', 'estimated_time_minutes', 'is_approved', 'created_by', 'created_at')
    list_filter = ('is_approved',)
    list_editable = ('is_approved',)
    search_fields = ('name', 'location')
    readonly_fields = ('created_at',)

    def save_model(self, request, obj, form, change):
        """管理者が登録した場合は即時承認する"""
        if not change:
            # 新規登録時、created_by が未設定なら管理者を自動セット
            if not obj.created_by_id:
                obj.created_by = request.user
            # 管理者は即時承認
            if request.user.is_staff:
                obj.is_approved = True
        super().save_model(request, obj, form, change)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('lunch_place', 'author', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('lunch_place__name', 'author__username', 'comment')
    readonly_fields = ('created_at',)
