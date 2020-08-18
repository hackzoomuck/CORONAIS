from django.urls import path
from . import views

from django.conf.urls import url



urlpatterns = [
    # loacalhost:8080/
    path('', views.coIs_home, name='coIs_home'),
<<<<<<< HEAD
    path('sidoinfo-state/', views.sidoinfo_state, name='sidoinfo_state'),
    path('folium-page/', views.folium_page, name='folium-page')

=======
<<<<<<< HEAD
    path('chart-bar/', views.chart_bar, name='chart-bar'),
=======
    #path('day-status/', views.day_status, name='day_status'),
    path('seoul/', views.seoul, name='seoul'),
    path('sidoinfo-state/', views.sidoinfo_state, name='sidoapi'),
    path('folium_page/', views.folium_page, name='folium')
>>>>>>> lee
>>>>>>> master
]