from django.urls import path
from . import views

# from corona_map.Api import Infection_city

from django.conf.urls import url

urlpatterns = [
    # loacalhost:8080/board-list : 템플릿 적용한 메인 페이지
    path('board-list/', views.news_board, name='board-list'),
    path('news-board-list/', views.news_board_list, name='news-board-list'),
]
