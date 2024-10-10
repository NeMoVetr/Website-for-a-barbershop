from django.urls import path

from .views import index, profile, register, service_list, add_service

urlpatterns = [
    path('', index, name='index'),
    path('profile/', profile, name='profile'),
    path('register/', register, name='register'),
    path('add-service/', add_service, name='add_service'),
    path('services/', service_list, name='services'),


]