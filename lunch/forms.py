# ファイルパス: lunch/forms.py
# GraphQL の呼び出しは JavaScript の fetch API で行うため、
# Django Form はサーバーサイドのバリデーションには使わない。
# このファイルは将来の拡張用として最小限の定義のみ置く。

from django import forms


class LunchPlaceForm(forms.Form):
    """昼食先登録フォーム（JavaScript から Mutation で送信）"""
    name = forms.CharField(max_length=100, label='店名')
    location = forms.CharField(max_length=200, label='場所')
    lunch_end_time = forms.TimeField(label='ランチ提供終了時刻')
    estimated_time_minutes = forms.IntegerField(min_value=1, label='平均所要時間（分）')


class ReviewForm(forms.Form):
    """レビュー投稿フォーム（JavaScript から Mutation で送信）"""
    rating = forms.IntegerField(min_value=1, max_value=5, label='評価')
    comment = forms.CharField(widget=forms.Textarea, label='コメント')
