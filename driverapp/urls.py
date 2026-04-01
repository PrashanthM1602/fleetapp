from django.urls import path
from . import views
from .views import (driver_logout,driver_profile_view)

urlpatterns = [
    path('', views.home, name='driver_home'),
    path('login/', views.login_view, name='driver_login'),
    path('accepted/', views.accepted_view, name='driver_accepted'),
    path('booking/', views.bookings, name='booking'),
    path('package/', views.packages, name='package'),
    path('emergency/', views.emergency, name='emergency'),
    path('settings/', views.settings, name='settings'),
    path('help/', views.help, name='help'),
    path('tracking/', views.tracking_view, name='driver_tracking'),
    path('profile/', driver_profile_view, name='driver_profile'),
    path('logout/', driver_logout, name='driver_logout'),
    
]

