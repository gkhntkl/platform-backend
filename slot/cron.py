from .models import Slot
from datetime import datetime

def update_slot():
<<<<<<< HEAD
    now = datetime.now()
    slots = Slot.objects.filter(day__lte=now)
    for deleted_slot in slots:
        deleted_slot.delete()
    day = datetime.date.today() +  datetime.timedelta(days=1850)
    Slot.objects.create(day=day)
=======
    today = datetime.today()
    slots = Slot.objects.filter(day__lt=today)
    for deleted_slot in slots:
        deleted_slot.delete()
    day = datetime.date.today() +  datetime.timedelta(days=1851)
    Slot.objects.create(day=day)
    
>>>>>>> 4fb1266e72c53cf3840a2db6eaa577d2189bcabe
