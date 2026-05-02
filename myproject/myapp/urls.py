from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login_user, name='login_no_slash'),
    path('login/', views.login_user, name='login'),
    path('login_post/', views.login_post, name='login_post'),
    path('register', views.register_user, name='register_no_slash'),
    path('register/', views.register_user, name='register'),
    path('register_post/', views.register_post, name='register_post'),
    path('home/', views.home, name='home'),
    path('upload_get/', views.upload_get, name='upload_get'),
    path('upload_and_predict/', views.upload_and_predict, name='upload_and_predict'),
    path('history/', views.history, name='history'),
    path('profile/', views.profile, name='profile'),
]