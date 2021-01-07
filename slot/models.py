from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from hall.models import Hall

class Slot(models.Model):


   available = models.BooleanField(default=True)
   halls = models.ManyToManyField(Hall,blank=True,related_name='slots')
   day = models.DateField(unique=True,primary_key=True)

   def __str__(self):
      return str(self.day)




