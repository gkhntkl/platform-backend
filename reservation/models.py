import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from boto3.session import Session
from api import settings
from django.db import models
from hall.models import Hall

session = Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

s3_client = session.client('sns','us-east-2')


SERVICE_TYPES = (
        (1, "Wedding"),
        (2, "Preaching"),
        (3, "Circumcision"),
        (4, "Other")
    )

class Reservation(models.Model):

    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    service_type = models.PositiveSmallIntegerField(choices=SERVICE_TYPES, default=1)
    name1 = models.TextField(max_length=100,default="",blank=True,null=True)
    name2 = models.TextField(max_length=50,default="",blank=True,null=True)
    phone = models.TextField(max_length=10)
    hall = models.ForeignKey(Hall, on_delete=models.PROTECT, related_name="hall")
    date = models.DateTimeField()
    expired = models.BooleanField(default=False)



@receiver(post_save, sender=Reservation)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        phoneNumber = "+90" + instance.phone
        hall = instance.hall
        city = instance.hall.city
        message = "http://18.218.147.80:3000/reservation/"+str(instance.id)

       # print(message)
       # s3_client.publish(PhoneNumber=phoneNumber,Message=message)








