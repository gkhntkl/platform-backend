from rest_framework import serializers
from .models import Reservation

from hall.serializers import HallSerializer


class ReservationSerializer(serializers.ModelSerializer):

    images = serializers.StringRelatedField(read_only=True, many=True)
    class Meta:
        model = Reservation
        fields = '__all__'


    def to_representation(self, instance):
        self.fields['hall'] =  HallSerializer(read_only=True)
        return super(ReservationSerializer, self).to_representation(instance)