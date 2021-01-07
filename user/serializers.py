from rest_framework import serializers
from .models import User
from hall.serializers import HallSerializer

class UserSerializer(serializers.ModelSerializer):

    halls = HallSerializer(many=True,read_only=True)

    class Meta:
        model = User

        fields = ['email','first_name','last_name','password','halls','company_name']
        extra_kwargs = {
            'password':{'write_only':True}
        }

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):

        if 'newpassword' in validated_data:
            if instance.check_password(validated_data['password']):
                instance.set_password(validated_data['newpassword'])
                instance.save()
                return instance
            return "Unauthorized"

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance
