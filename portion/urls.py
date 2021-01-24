
from django.contrib import admin
from django.urls import path
from .views import PortionDetailAPIView
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    path('', csrf_exempt(PortionDetailAPIView.as_view()))
]

