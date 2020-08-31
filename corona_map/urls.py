from django.urls import path
from . import views

#from corona_map.Api import Infection_city

from django.conf.urls import url

urlpatterns = [
    # loacalhost:8000/
    path('', views.coIs_home, name='coIs_home'),

    # loacalhost:8000/chart-bar : 시도별 확진자 추이, 날짜별 확진자 추이 시각화 페이지
    path('chart-bar/', views.chart_bar, name='chart-bar'),

    # loacalhost:8000/by-age-gender : 연령별/성별 치명률 시각화 페이지
    path('by-age-gender/', views.chart_bar_by_age_gender, name='by-age-gender'),
    
    # loacalhost:8000/cois-main : 템플릿 적용한 메인 페이지
    path('cois-main/', views.cois_main, name='cois-main'),

    #
    path('seoul/', views.seoul, name='seoul'),

    #
    path('folium_page/', views.folium_page, name='folium'),

    # 테스트 페이지
    path('test_api/', views.news_board_list, name='test_api'),

    # 완치자 데이터를 가져오는 페이지
    path('gugun-info/', views.call_gugun_info ,name='gugun-info')


    # loacalhost:8080/board-list : 코로나 뉴스게시판 리스트 페이지
    #path('board-list/', views.seoul_map, name='board-list'),

]
