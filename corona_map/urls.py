from django.urls import path
from . import views

from django.conf.urls import url

urlpatterns = [
    # loacalhost:8080/
    path('', views.coIs_home, name='coIs_home'),
    #
    path('chart-bar/', views.chart_bar, name='chart-bar'),
    #
    path('seoul/', views.seoul, name='seoul'),

    #
    path('folium_page/', views.folium_page, name='folium'),
    # 완치자 데이터를 가져오는 페이지
    path('cure_people/', views.cure_people ,name='cure_people')

]