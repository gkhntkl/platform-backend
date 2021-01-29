from .models import Reservation
from datetime import datetime,timedelta
from boto3.session import Session
from django.conf import settings

session = Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

s3_client = session.client('sns','us-east-2')

def update_reservation():
  now = datetime.now()
  reservations = Reservation.objects.filter(expired=False).filter(date__lt=now)
  for reservation in reservations:
    reservation.expired = True
    reservation.save()


def notify_duration():
  start = datetime.now() + timedelta(days=29)
  end = datetime.now() + timedelta(days=30)
  reservations = Reservation.objects.filter(expired=True).filter(duration_end__range=(start,end))
  message = "Merhabalar,\n30 gün içinde süresi uzatılmadığı takdirde Albümünüz silinecektir.\nBu konu hakkında bizimle irtibata geçebilirsiniz.İyi günler dileriz\nsalonayır.com/contact"

  for reservation in reservations:
    if reservation.hall.num_of_messages < reservation.hall.quota_of_messages:
      if reservation.phone != "+90":
        #s3_client.publish(PhoneNumber="+90"+reservation.phone, Message=message)
        reservation.hall.num_of_messages = reservation.hall.num_of_messages + 1
        reservation.hall.save()

def delete_photos_not_extended():

  Reservation.objects.filter(duration_end__lt=datetime.now()).delete()


