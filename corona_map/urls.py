from django.urls import path
from . import views

#from corona_map.Api import Infection_city

from django.conf.urls import url

urlpatterns = [
    # loacalhost:8080/
    path('', views.coIs_home, name='coIs_home'),

    # loacalhost:8080/chart-bar : 시도별 확진자 추이, 날짜별 확진자 추이 시각화 페이지
    path('chart-bar/', views.chart_bar, name='chart-bar'),

    # loacalhost:8080/by-age-gender : 연령별/성별 치명률 시각화 페이지
    path('by-age-gender/', views.chart_bar_by_age_gender, name='by-age-gender'),
    
    # loacalhost:8080/cois-main : 템플릿 적용한 메인 페이지
    path('cois-main/', views.cois_main, name='cois-main'),

    #
    path('seoul/', views.seoul, name='seoul'),
    #
    path('folium_page/', views.folium_page, name='folium'),
    # 함수로 사용하면서, local mongo에서 get하는 중
    path('sidoinfo_state/', views.sidoinfo_state, name='sido'),
    # 완치자 데이터를 가져오는 페이지
    path('cure_people/', views.cure_people ,name='cure_people')

]