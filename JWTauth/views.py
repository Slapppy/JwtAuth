import jwt
from datetime import datetime, timedelta

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.conf import settings
from .models import CustomUser


@csrf_exempt
def register(request):
    email = request.POST.get("email")
    password = request.POST.get("password")
    name = request.POST.get("name")

    if not email or not password:
        return JsonResponse({"error": "Email and password are required."})

    user = CustomUser.objects.create_user(email=email, password=password, name=name)
    return JsonResponse({"success": "User created successfully."})


@csrf_exempt
def login(request):
    email = request.POST.get("email")
    password = request.POST.get("password")

    if not email or not password:
        return JsonResponse({"error": "Email and password are required."})

    user = authenticate(email=email, password=password)

    if user is not None:
        token = jwt.encode(
            {"id": user.id, "exp": datetime.utcnow() + timedelta(minutes=60)},
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        return JsonResponse({"token": token})
    else:
        return JsonResponse({"error": "Invalid credentials."})


def protected_view(request):
    
    token = request.META.get("HTTP_AUTHORIZATION", "").split("")[1]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload["id"]
        user = CustomUser.objects.get(id=user_id)
        return JsonResponse({"success": f"Hello, {user.email}!"})
    except jwt.exceptions.DecodeError:
        return JsonResponse({"error": "Invalid token."})
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "User not found."})


def main(request):
    return render(request, "JWTauth/Test.html")
