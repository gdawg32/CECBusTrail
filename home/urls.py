from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin_login', views.admin_login, name='admin_login'),
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('bus_management', views.bus_management, name='bus_management'),
    path('api/bus-stops/', views.get_bus_stops, name="bus-stops"),
    path('api/buses/', views.get_buses, name="buses"),
    path('api/add-bus-stop/', views.add_bus_stop, name="add-bus-stop"),
    path('api/add-bus/', views.add_bus, name="add-bus"),
    path('api/bus-stops/<int:bus_id>/', views.bus_stops_for_bus, name='bus_stops_for_bus'),

]