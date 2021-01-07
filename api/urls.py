from django.contrib import admin
from django.urls import path,include,re_path

from django.db import transaction
import datetime

import pytz
from pytz import timezone
from celery.schedules import crontab
from celery.task import periodic_task


from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/hall/', include('hall.urls')),
    path('api/user/', include('user.urls')),
    path('api/slot/', include('slot.urls')),
    path('api/reservation/', include('reservation.urls')),
    re_path('.*',views.index,name='index')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





