
from django.contrib import admin
from django.urls import path
from .views import HallDetailAPIView,HallListAPIView,HallCreateAPIView,HallSearchAPIView,HallNameSearchAPIView

urlpatterns = [
    path('', HallListAPIView.as_view()),
    path('search/', HallSearchAPIView.as_view()),
    path('searchname/', HallNameSearchAPIView.as_view()),
    path('create/', HallCreateAPIView.as_view()),
    path('<int:id>/', HallDetailAPIView.as_view()),
]

