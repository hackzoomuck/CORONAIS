from django.urls import path
from . import views

#from corona_map.Api import Infection_city

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
    # 함수로 사용하면서, local mongo에서 get하는 중
    path('sidoinfo_state/', views.sidoinfo_state, name='sido'),

]