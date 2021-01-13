from django.db import models
from django.db.models.signals import post_save
from django.db.models.signals import post_save, pre_save


from django.dispatch import receiver
from user.models import User
from city.models import City


class Hall(models.Model):

    SERVE_TYPES = (
        (1, "With Food"),
        (2, "Without Food"),
        (3, "Both ")
    )
    BEVERAGE_TYPES = (
        (1, "Alcohol Allowed"),
        (2, "Not Allowed"),
    )
    AIR_TYPES = (
        (1, "Open"),
        (2, "Close"),
        (3, "Both")
    )
    OCCURENCE_TYPES = (
        (1, "More Than One Wedding At The Same Time"),
        (2, "Just One Wedding"),
    )
    LIVE_MUSIC_TYPES = (
        (1,"Live Music Available"),
        (2,"Not Available"),
    )
    PHOTOGRAPHY_TYPES  = (
        (1,"3th Parthy Photograpy Allowed"),
        (2,"Not Allowed"),
    )
    PARKING_TYPES = (
        (1, "Park Available"),
        (2, "Not Available"),
    )
    VALE_TYPES = (
        (1, "Vale Available"),
        (2, "Not Available"),
    )
    CHILD_PARK_TYPES = (
        (1, "Vale Available"),
        (2, "Not Available"),
    )
    SERVICE_TYPES = (
        (0, "Not Available"),
        (1, "Service Available"),
    )

    WHEELCHAIR_TYPES = (
        (1, "Wheelchair Entrance Available"),
        (2, "Not Available"),
    )


    PRAYING_TYPES = (
        (1, "Praying Available"),
        (2, "Not Available"),
    )


    name = models.TextField(blank=False)
    name2 = models.TextField(blank=False)
    city_name = models.TextField(blank=False)
    website = models.TextField(blank=True,default="")
    phone = models.TextField(blank=True,default="",null=True)
    email = models.EmailField(blank=True,default="")
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=False, default=1, related_name="cities")
    district = models.CharField(max_length=30,default="Besiktas")
    address = models.TextField(default="No Address")
    lat = models.DecimalField(blank=True, null=True, max_digits=18, decimal_places=15)
    lng = models.DecimalField(blank=True, null=True, max_digits=18, decimal_places=15)
    user = models.ForeignKey(User,on_delete=models.CASCADE,blank=False,default=25,related_name="halls")
    open_capacity = models.IntegerField(blank=False)
    close_capacity = models.IntegerField(blank=False)
    child_park_type = models.PositiveSmallIntegerField(choices=CHILD_PARK_TYPES, default=1)
    serve_type = models.PositiveSmallIntegerField(choices=SERVE_TYPES, default=1)
    beverage_type = models.PositiveSmallIntegerField(choices=BEVERAGE_TYPES, default=1)
    air_type = models.PositiveSmallIntegerField(choices=AIR_TYPES, default=1)
    occurrence_type = models.PositiveSmallIntegerField(choices=OCCURENCE_TYPES, default=1)
    live_music_type = models.PositiveSmallIntegerField(choices=LIVE_MUSIC_TYPES, default=1)
    photograpy_type = models.PositiveSmallIntegerField(choices=PHOTOGRAPHY_TYPES, default=1)
    parking_type = models.PositiveSmallIntegerField(choices=PARKING_TYPES, default=1)
    vale_type = models.PositiveSmallIntegerField(choices=VALE_TYPES, default=1)
    opening_time = models.CharField(max_length=10,default="00:00")
    closing_time = models.CharField(max_length=10,default="00:00")
    wheelchair_type = models.PositiveSmallIntegerField(choices=WHEELCHAIR_TYPES, default=1)
    praying_type = models.PositiveSmallIntegerField(choices=PRAYING_TYPES, default=1)
    service_type1 = models.PositiveSmallIntegerField(choices=SERVICE_TYPES, default=0)
    service_type2 = models.PositiveSmallIntegerField(choices=SERVICE_TYPES, default=0)
    service_type3 = models.PositiveSmallIntegerField(choices=SERVICE_TYPES, default=0)
    service_type4 = models.PositiveSmallIntegerField(choices=SERVICE_TYPES, default=0)
    service_type5 = models.PositiveSmallIntegerField(choices=SERVICE_TYPES, default=0)
    service_type6 = models.PositiveSmallIntegerField(choices=SERVICE_TYPES, default=0)
    profile_choice = models.SmallIntegerField(default=0)
    photo_number = models.SmallIntegerField(default=0)


_UNSAVED_IMAGEFIELD = 'unsaved_imagefield'

def upload_path_handler(instance, filename):

    return "images/{id}/{fname}".format(id=instance.hall_id,fname=filename)

class HallImage(models.Model):
    hall = models.ForeignKey(Hall, related_name='images',on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_path_handler,blank=True)
    name = models.CharField(max_length=30,default="")

    def __str__(self):
        return self.name




@receiver(pre_save, sender=HallImage)
def skip_saving_file(sender, instance, **kwargs):
    if not instance.pk and not hasattr(instance, _UNSAVED_IMAGEFIELD):
        setattr(instance, _UNSAVED_IMAGEFIELD, instance.image)
        instance.image = None

@receiver(post_save, sender=HallImage)
def update_file_url(sender, instance, created, **kwargs):
    if created and hasattr(instance, _UNSAVED_IMAGEFIELD):
        instance.image = getattr(instance, _UNSAVED_IMAGEFIELD)
        instance.save()

