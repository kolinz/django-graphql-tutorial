# ファイルパス: lunch/urls.py

from django.urls import path
from . import views

app_name = 'lunch'

urlpatterns = [
    path('', views.place_list, name='place_list'),
    path('places/<int:pk>/', views.place_detail, name='place_detail'),
    path('places/<int:pk>/review/', views.review_form, name='review_form'),
    path('myreviews/', views.my_reviews, name='my_reviews'),
    path('places/new/', views.place_form, name='place_form'),
]
