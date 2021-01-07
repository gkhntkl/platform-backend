from rest_framework import serializers
from .models import Hall


class HallSerializer(serializers.ModelSerializer):


    slots = serializers.PrimaryKeyRelatedField(read_only=True,many=True)
    images = serializers.StringRelatedField(read_only=True,many=True)

    class Meta:
        model = Hall
        exclude = ['user']


    def update(self, instance, validated_data):

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance






