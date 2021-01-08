from .models import Reservation
from datetime import datetime

def update_reservation():
  now = datetime.now()
  reservations = Reservation.objects.filter(expired=False).filter(date__lt=now)
  for reservation in reservations:
    reservation.expired = True
    reservation.save()
