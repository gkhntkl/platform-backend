from django.db import models


class City(models.Model):

   id = models.SmallIntegerField(primary_key=True)
   name = models.CharField(default='Istanbul',max_length=40)





