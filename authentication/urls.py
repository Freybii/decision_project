from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('google-login/', views.GoogleLoginView.as_view(), name='google_login'),
    path('google-callback/', views.google_callback, name='google_callback'),
] 