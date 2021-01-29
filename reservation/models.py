import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from boto3.session import Session
from api import settings
from django.db import models
from hall.models import Hall
from django.contrib.postgres.fields import ArrayField
from datetime import datetime,timedelta
from django.utils.dateparse import parse_datetime
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from botocore.client import Config

session = Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

s3_client = session.client('sns','us-east-2')


SERVICE_TYPES = (
        (1, "Wedding"),
        (2, "Preaching"),
        (3, "Circumcision"),
        (4, "Other"),
        (5, "Wedding2")
    )

class Reservation(models.Model):

    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    service_type = models.PositiveSmallIntegerField(choices=SERVICE_TYPES, default=1)
    name1 = models.TextField(max_length=100,default="",blank=True,null=True)
    name2 = models.TextField(max_length=50,default="",blank=True,null=True)
    phone = models.TextField(max_length=10)
    hall = models.ForeignKey(Hall, on_delete=models.PROTECT, related_name="hall")
    date = models.DateTimeField(default=datetime.now)
    expired = models.BooleanField(default=False)
    portion = ArrayField(ArrayField(models.SmallIntegerField()))
    wedding_count = models.PositiveSmallIntegerField(default=1)
    duration = models.PositiveIntegerField(default=5)
    duration_end = models.DateTimeField(default=datetime.now)
    payment_done = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if isinstance(self.date,datetime):
            self.duration_end = self.date + timedelta(weeks=52 * self.duration)
        else:
            self.duration_end = parse_datetime(self.date) + timedelta(weeks=52 * self.duration)

        super().save(*args, **kwargs)



class ReservationImage(models.Model):
    reservation = models.ForeignKey(Reservation, related_name='images',on_delete=models.CASCADE)
    name = models.SlugField()

    def __str__(self):
        return self.name


@receiver(pre_delete, sender=Reservation)
def log_deleted_question(sender, instance, using, **kwargs):
    images = ReservationImage.objects.filter(reservation=instance)

    s3_client = session.client('s3', region_name="us-east-2",
                               config=Config(signature_version='s3v4'))
    s3_resource = session.resource('s3', region_name="us-east-2", config=Config(signature_version='s3v4'))
    my_bucket = s3_resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    my_bucket_resized = s3_resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME_RESIZED)
    obj = []
    obj_resized = []

    for image in images:
        obj.append({'Key': 'photos/' + str(instance.id) + '/' + image.name + "/image.jpg"})
        obj_resized.append({'Key': 'resized-photos/' + str(instance.id) + '/' + image.name + "/image.jpg"})

    my_bucket.delete_objects(
        Delete={
            'Objects': obj,
        }
    )
    my_bucket_resized.delete_objects(
        Delete={
            'Objects': obj_resized,
        }
    )







