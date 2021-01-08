

from django.urls import path
from .views import *

urlpatterns = [
    path('create/',ReservationCreateAPIView.as_view()),
    path('update/<uuid:id>/', ReservationUpdateAPIView.as_view()),
    path('hallreservation/<int:id>/', ReservationHallDetailAPIView.as_view()),
    path('<uuid:id>/', ReservationDetailAPIView.as_view()),
]
