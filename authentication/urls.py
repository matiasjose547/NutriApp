from django import views
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name="logout"),
    path('activate_account/<str:token>/', views.activate_account, name="activate_account"),
]