# ファイルパス: lunch/models.py

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class LunchPlace(models.Model):
    name = models.CharField(max_length=100, verbose_name='店名')
    location = models.CharField(max_length=200, verbose_name='場所')
    lunch_end_time = models.TimeField(
        verbose_name='ランチ提供終了時刻',
        help_text='ランチ提供終了時刻（例：13:30）',
    )
    estimated_time_minutes = models.PositiveIntegerField(
        verbose_name='平均所要時間（分）',
        help_text='往復・提供・食事を含めた平均所要時間（分）',
    )
    is_approved = models.BooleanField(default=False, verbose_name='承認済み')
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_lunch_places',
        verbose_name='登録者',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='登録日時')

    class Meta:
        verbose_name = '昼食先'
        verbose_name_plural = '昼食先'
        ordering = ['name']

    def __str__(self):
        return self.name


class Review(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='投稿者',
    )
    lunch_place = models.ForeignKey(
        LunchPlace,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='昼食先',
    )
    rating = models.PositiveIntegerField(
        verbose_name='評価',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(verbose_name='コメント')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='投稿日時')

    class Meta:
        verbose_name = 'レビュー'
        verbose_name_plural = 'レビュー'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.lunch_place.name} - {self.author.username} ({self.rating}★)'
