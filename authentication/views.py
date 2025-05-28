from django.shortcuts import render, redirect
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer
)
from .models import CustomUser
import jwt
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.


@login_required
def profile_view(request):
    return render(request, 'main/profile.html', {'user': request.user})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.bio = request.POST.get('bio', user.bio)
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        user.save()
        messages.success(request, 'Профіль успішно оновлено.')
        return redirect('authentication:profile')
    return render(request, 'main/edit_profile.html', {'user': request.user})


@login_required
def google_callback(request):
    """Handle Google OAuth callback."""
    try:
        code = request.GET.get('code')
        if not code:
            messages.error(
                request, 'Не вдалося отримати код авторизації від Google.'
            )
            return redirect('authentication:login')
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'code': code,
            'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
            'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            'redirect_uri': settings.GOOGLE_OAUTH2_REDIRECT_URI,
            'grant_type': 'authorization_code',
        }
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        userinfo_response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {tokens["access_token"]}'}
        )
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()
        email = userinfo['email']
        try:
            user = CustomUser.objects.get(email=email)
            if not user.google_id:
                user.google_id = userinfo['sub']
                user.save()
        except CustomUser.DoesNotExist:
            user = CustomUser.objects.create(
                email=email,
                username=email,
                first_name=userinfo.get('given_name', ''),
                last_name=userinfo.get('family_name', ''),
                google_id=userinfo['sub']
            )
        login(request, user)
        messages.success(request, 'Ви успішно увійшли через Google.')
        return redirect('index')
    except Exception as e:
        messages.error(request, f'Помилка входу через Google: {str(e)}')
        return redirect('authentication:login')


class RegistrationView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = self.generate_jwt_token(user)
            if request.path.startswith('/api/'):
                return Response({
                    'token': token,
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
            return render(
                request, 'main/login.html',
                {'message': 'Реєстрація успішна! Тепер ви можете увійти.'}
            )
        if request.path.startswith('/api/'):
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        return render(request, 'main/register.html', {'errors': serializer.errors})

    def get(self, request):
        return render(request, 'main/register.html')

    def generate_jwt_token(self, user):
        payload = {
            'user_id': str(user.id),
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


class LoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                request,
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            if user:
                if request.path.startswith('/api/'):
                    token = self.generate_jwt_token(user)
                    return Response({
                        'token': token,
                        'user': UserSerializer(user).data
                    })
                login(request, user)
                messages.success(request, 'Ви успішно увійшли в систему.')
                return redirect('index')
            if request.path.startswith('/api/'):
                return Response(
                    {'error': 'Невірний email або пароль'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            messages.error(request, 'Невірний email або пароль')
            return render(request, 'main/login.html')
        if request.path.startswith('/api/'):
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        return render(request, 'main/login.html', {'errors': serializer.errors})

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        return render(request, 'main/login.html')

    def generate_jwt_token(self, user):
        payload = {
            'user_id': str(user.id),
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


class GoogleLoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            token = request.data.get('token')
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_OAUTH2_CLIENT_ID
            )
            email = idinfo['email']
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            google_id = idinfo['sub']
            try:
                user = CustomUser.objects.get(email=email)
                if not user.google_id:
                    user.google_id = google_id
                    user.save()
            except CustomUser.DoesNotExist:
                user = CustomUser.objects.create(
                    email=email,
                    username=email,
                    first_name=first_name,
                    last_name=last_name,
                    google_id=google_id
                )
            login(request, user)
            messages.success(request, 'Ви успішно увійшли через Google.')
            return redirect('index')
        except Exception as e:
            messages.error(request, f'Помилка входу через Google: {str(e)}')
            return redirect('authentication:login')


def logout_view(request):
    logout(request)
    return redirect('authentication:login')
