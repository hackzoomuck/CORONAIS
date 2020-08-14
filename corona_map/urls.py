from django.urls import path
from . import views



urlpatterns = [
    # loacalhost:8080/
    path('', views.coIs_home, name='coIs_home'),
    path('sidoinfo-state/', views.sidoinfo_state, name='sidoinfo_state'),
    path('folium-page/', views.folium_page, name='folium-page')

]