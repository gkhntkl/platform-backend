

from django.urls import path
from .views import *

urlpatterns = [

    path('login/', UserLoginAPIView.as_view()),
    path('signup/', UserSignupAPIView.as_view()),
    path('profile/', UserProfileAPIView.as_view()),
    path('hall/<int:id>/', UserHallAPIView.as_view()),
]
