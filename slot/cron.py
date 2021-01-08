from .models import Slot
from datetime import datetime

def update_slot():
    now = datetime.now()
    slots = Slot.objects.filter(day__lte=now)
    for deleted_slot in slots:
        deleted_slot.delete()
    day = datetime.date.today() +  datetime.timedelta(days=1850)
    Slot.objects.create(day=day)
