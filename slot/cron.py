from .models import Slot
from datetime import datetime

def update_slot():
    today = datetime.today()
    slots = Slot.objects.filter(day__lt=today)
    for deleted_slot in slots:
        deleted_slot.delete()
    day = datetime.date.today() +  datetime.timedelta(days=1851)
    Slot.objects.create(day=day)
    
