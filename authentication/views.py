from django.shortcuts import render, redirect
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer
from .models import CustomUser
import jwt
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.

@login_required
def profile_view(request):
    return render(request, 'main/profile.html', {'user': request.user})

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
            else:
                return render(request, 'main/login.html', {'message': 'Реєстрація успішна! Тепер ви можете увійти.'})
        if request.path.startswith('/api/'):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
                else:
                    login(request, user)  # Create session for web interface
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
                    username=email,  # Using email as username
                    first_name=first_name,
                    last_name=last_name,
                    google_id=google_id
                )

            if request.path.startswith('/api/'):
                token = self.generate_jwt_token(user)
                return Response({
                    'token': token,
                    'user': UserSerializer(user).data
                })
            else:
                login(request, user)  # Create session for web interface
                messages.success(request, 'Ви успішно увійшли через Google.')
                return redirect('index')
        except Exception as e:
            if request.path.startswith('/api/'):
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            messages.error(request, f'Помилка входу через Google: {str(e)}')
            return redirect('authentication:login')

    def generate_jwt_token(self, user):
        payload = {
            'user_id': str(user.id),
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def logout_view(request):
    logout(request)
    messages.success(request, 'Ви успішно вийшли з системи.')
    return redirect('index')
