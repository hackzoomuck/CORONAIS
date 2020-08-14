from django.urls import path
from . import views


urlpatterns = [
    # loacalhost:8080/
    path('', views.coIs_home, name='coIs_home'),
    #path('day-status/', views.day_status, name='day_status'),
    path('seoul/', views.seoul, name='seoul'),
    path('sidoinfo-state/', views.sidoinfo_state, name='sidoapi'),
    path('folium_page/', views.folium_page, name='folium')
]