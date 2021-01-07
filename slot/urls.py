from django.urls import path
from .views import SlotListAPIView,SlotDetailAPIView,SlotSearchAPIView
from django.urls import  re_path
urlpatterns = [
    path('', SlotListAPIView.as_view()),
    path('<int:pk>/', SlotDetailAPIView.as_view()),
    path('search/', SlotSearchAPIView.as_view()),
    re_path(r'^(?P<date>\d{4}-\d{2}-\d{2})/$', SlotDetailAPIView.as_view())
]