from .models import Slot
from datetime import datetime

def update_slot():
    now = datetime.now()
    deleted_slot = Slot.objects.filter(day__lte=now).first()
    deleted_slot.delete()
    new_slot = datetime.date(now.year + 5, now.month, now.day)
    Slot.objects.create(day=new_slot)
