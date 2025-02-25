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
    path('delete-bus/<int:bus_id>/', views.delete_bus, name='delete-bus'),
    path('drivers/', views.driver_management, name='driver_management'),
    path('delete-driver/<int:driver_id>/', views.delete_driver, name='delete-driver'),
    path("get-driver/<int:driver_id>/", views.get_driver, name="get_driver"),
    path("edit-driver/<int:driver_id>/", views.edit_driver, name="edit_driver"),
    path("driver-login/", views.driver_login, name="driver_login"),
    path("driver-logout/", views.driver_logout, name="driver_logout"),
    path("driver-dashboard/", views.driver_dashboard, name="driver_dashboard"),
    path("student-application/", views.student_application, name="student_application"),
    path("admin_dashboard/student-management/", views.student_management, name="student_management"),
    path("admin_dashboard/approve-student/<int:application_id>/", views.approve_student, name="approve_student"),
    path("admin_dashboard/reject-student/<int:application_id>/", views.reject_student, name="reject_student"),
    path("student/login/", views.student_login, name="student_login"),
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),
    path("student/logout/", views.student_logout, name="student_logout"),
    path("edit-profile/", views.edit_student_profile, name="edit_student_profile"),

]