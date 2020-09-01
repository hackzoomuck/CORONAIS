from django.urls import path
from . import views

# from corona_map.Api import Infection_city

from django.conf.urls import url

urlpatterns = [
    # loacalhost:8080/seoul-main/ : 서울클릭시 이동하는 서울메인 페이지
    path('seoul-main/', views.seoul_main, name='seoul-main'),
    # 서울지도
    path('seoul-map/', views.seoul_map, name='seoul-map'),

]
