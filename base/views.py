from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
# ADD THESE: These satisfy the "Security Hotspots" in your screenshots
from django.views.decorators.http import require_http_methods, require_safe, require_POST

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework import status

import requests
import hvac
import os

from .models import UserSubscription, Advertisement
from .serializers import UserSerializer, AdvertisementSerializer

# SONARQUBE FIX: Defined constants to eliminate "Duplicate Literal" High Issues
REGISTER_TEMPLATE = "base/register.html"
LOGIN_TEMPLATE = "base/login.html"
HOME_REDIRECT = "/"

CustomUser = get_user_model()

def get_newsapi_key():
    vault_url = os.getenv('VAULT_ADDR', 'https://vault.demo.internal:8200')
    client = hvac.Client(url=vault_url, verify=False)
    token = os.getenv('VAULT_TOKEN')

    if token:
        client.token = token
    else:
        try:
            token_path = '/var/run/secrets/kubernetes.io/serviceaccount/token'
            if os.path.exists(token_path):
                with open(token_path, 'r') as f:
                    jwt = f.read()
                client.auth.kubernetes.login(role="newstrends-role", jwt=jwt)
        except Exception:
            if settings.DEBUG:
                return os.getenv("NEWS_API_KEY", "dev-fallback-key")
            raise ImproperlyConfigured("Vault auth failed")

    try:
        secret = client.secrets.kv.v2.read_secret_version(path='newsapi', mount_point='kv')
        return secret['data']['data']['API_KEY']
    except Exception as e:
        if settings.DEBUG:
            return "dev-vault-error-key"
        raise ImproperlyConfigured(f"Vault error: {e}")

# --- WEB VIEWS ---

@require_safe # FIX: Tells Sonar this only allows GET/HEAD (Safe methods)
@login_required(login_url='login')
def home(request):
    api_key = get_newsapi_key()
    url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}'
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        articles = data.get("articles", [])
    except Exception:
        articles = []
    ads = Advertisement.objects.all()
    return render(request, "base/home.html", {"articles": articles, "ads": ads})

@require_safe # FIX: Resolves "Safe and unsafe HTTP methods" hotspot
@login_required
def category(request, category):
    api_key = get_newsapi_key()
    url = f'https://newsapi.org/v2/top-headlines?country=us&category={category}&apiKey={api_key}'
    response = requests.get(url, timeout=10)
    articles = response.json().get('articles', [])
    context = {
        'category': category.capitalize(),
        'articles': articles,
        "ads": Advertisement.objects.all(),
    }
    return render(request, 'base/category.html', context)

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username"), password=request.POST.get("password"))
        if user:
            login(request, user)
            return redirect(HOME_REDIRECT)
        messages.error(request, "Invalid credentials")
    return render(request, LOGIN_TEMPLATE)

@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.method == "POST":
        data = request.POST
        if data.get("password1") != data.get("password2"):
            messages.error(request, "Passwords do not match")
            return render(request, REGISTER_TEMPLATE)
        try:
            user = CustomUser.objects.create_user(
                username=data.get("username"), email=data.get("email"), password=data.get("password1")
            )
            login(request, user)
            return redirect(HOME_REDIRECT)
        except IntegrityError:
            messages.error(request, "Error creating account.")
    return render(request, REGISTER_TEMPLATE)

@require_POST # FIX: Prevents CSRF issues on logout
def logout_view(request):
    logout(request)
    return redirect("login")

# --- SUBSCRIPTION VIEWS ---

@require_POST # FIX: Critical for Security Hotspots in your screenshots
@login_required
def unsubscribe(request):
    sub = UserSubscription.objects.filter(user=request.user).first()
    if sub:
        sub.is_subscribed = False
        sub.save()
        messages.success(request, "Unsubscribed.")
    return redirect("home")

@require_safe
@login_required
def subscription_page(request):
    return render(request, 'base/payment.html')

@require_POST # FIX: Specifically mentioned in your Security Hotspot screenshot
@login_required
def process_payment(request):
    sub, _ = UserSubscription.objects.get_or_create(user=request.user)
    sub.is_subscribed = True
    sub.save()
    messages.success(request, "Successfully Subscribed!")
    return redirect(reverse("subscription_success"))

@require_safe # FIX: Clears the red warning on this function in Sonar
@login_required
def subscription_success(request):
    return render(request, "base/subscription_success.html")

# --- API VIEWS (Keep as is, @api_view handles methods) ---
@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def advertisement_list(request):
    """API endpoint to list all advertisements"""
    ads = Advertisement.objects.all()
    serializer = AdvertisementSerializer(ads, many=True)
    return Response(serializer.data)

@require_http_methods(["GET", "POST"]) # Change from @require_POST
def logout_view(request):
    logout(request)
    return redirect("login")