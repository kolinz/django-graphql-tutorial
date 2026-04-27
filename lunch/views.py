# ファイルパス: lunch/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import LunchPlace


def place_list(request):
    """昼食先一覧（画面1）"""
    return render(request, 'lunch/place_list.html')


def place_detail(request, pk):
    """昼食先詳細（画面2）"""
    place = get_object_or_404(LunchPlace, pk=pk, is_approved=True)
    lunch_end = request.GET.get('lunchEnd', '13:00')
    return render(request, 'lunch/place_detail.html', {
        'place_id': pk,
        'lunch_end': lunch_end,
    })


@login_required
def review_form(request, pk):
    """レビュー投稿（画面3）"""
    place = get_object_or_404(LunchPlace, pk=pk, is_approved=True)
    return render(request, 'lunch/review_form.html', {
        'place_id': pk,
        'place_name': place.name,
    })


@login_required
def my_reviews(request):
    """自分のレビュー一覧（画面4）"""
    return render(request, 'lunch/my_reviews.html')


@login_required
def place_form(request):
    """昼食先登録（画面5）"""
    return render(request, 'lunch/place_form.html')
