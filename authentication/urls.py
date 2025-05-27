from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'authentication'

urlpatterns = [
    # API endpoints
    path('api/register/', views.RegistrationView.as_view(), name='api_register'),
    path('api/login/', views.LoginView.as_view(), name='api_login'),
    path('api/google-login/', views.GoogleLoginView.as_view(), name='api_google_login'),
    
    # Web interface endpoints
    path('web/register/', views.RegistrationView.as_view(), name='register'),
    path('web/login/', views.LoginView.as_view(), name='login'),
    path('web/profile/', views.profile_view, name='profile'),
    path('web/logout/', views.logout_view, name='logout'),
] 