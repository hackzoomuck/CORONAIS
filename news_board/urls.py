from django.urls import path
from . import views

# from corona_map.Api import Infection_city

from django.conf.urls import url

urlpatterns = [
    # loacalhost:8080/board-list : 코로나 뉴스게시판 리스트 페이지
    path('board-list/', views.news_board, name='board-list'),
    # localhost:8080/news-board-list : 코로나 뉴스 크롤링 데이터값 확인 페이지
    path('news-board-list/', views.news_board_list, name='news-board-list'),
    # localhost:8080/news-board-detail/<str:pk_id> : 코로나 뉴스게시판 상세페이지
    path('news-board-detail/<str:id>', views.news_board_detail, name='news-board-detail'),
    # localhost:8080/news-comment-insert : 댓글 insert (Ajax)
    path('news-comment-insert/', views.news_comment_insert, name='news-comment-insert'),
    # localhost:8080/news-comment-list : 댓글 조회 select (Ajax)
    path('news-comment-list/<str:id>', views.news_comment_list, name='news-comment-list'),
]
