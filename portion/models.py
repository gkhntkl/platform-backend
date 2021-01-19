from django.db import models

from hall.models import Hall
from slot.models import Slot

SPOT_TYPES = (
    (0, 0), (1, 1),(2, 2),(3, 3),(4, 4),(5, 5),(6, 6),(7, 7),
    (8, 8),(9, 9),(10, 10),(11, 11),(12, 12),(13, 13),(14, 14),(15, 15),
    (16, 16),(17, 17),(18, 18),(19, 19),(20, 20),(21, 21),(22, 22),(23, 23),
)
class Portion(models.Model):

   wedding_count = models.PositiveSmallIntegerField(default=0)
   spot = models.SmallIntegerField(choices=SPOT_TYPES,default=0)
   hall = models.ForeignKey(Hall,related_name='portion_hall',on_delete=models.CASCADE)
   slot = models.ForeignKey(Slot,related_name='portion_slot',on_delete=models.CASCADE)

   class Meta:
       constraints = [
           models.UniqueConstraint(fields=['hall', 'slot','spot','wedding_count'], name="hall-portion")
       ]


