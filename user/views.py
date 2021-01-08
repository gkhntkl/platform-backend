from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.contrib.auth import authenticate

from .models import User
from hall.models import Hall,HallImage
from slot.models import Slot
from city.models import City
from hall.serializers import HallSerializer
from .serializers import UserSerializer

from unidecode import unidecode
from api import settings
import json

from boto3.session import Session
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile

import boto3
from boto3.s3.transfer import TransferConfig

from multiprocessing import Process

class UserListAPIView(APIView):

    def get(self,request):
        customers = User.objects.all()
        serializer = UserSerializer(customers,many=True)

        return Response(serializer.data)

    def post(self,request):

        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            user.set_password(serializer.data['password'])
            user.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class UserProfileAPIView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_user(self,id):

        try:
            return User.objects.get(id=id)

        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self,request):
        user = self.get_user(request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data,status.HTTP_200_OK)

    def put(self,request):
        user = self.get_user(request.user.id)

        serializer = UserSerializer(user,data=request.data,partial=True)
        if serializer.is_valid():
            if 'email' in serializer.validated_data :
                response = {"message":"cannot be updated"}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            validated_data = serializer.validated_data
            if 'newpassword' in request.data:
                validated_data['newpassword'] = request.data['newpassword']
            message = serializer.update(user,validated_data)
            if message == "Unauthorized":
                response = {"message": "Unauthorized"}
                return Response(response, status.HTTP_401_UNAUTHORIZED)
            response = {"message": "Success Update "}
            return Response(response,status.HTTP_200_OK)
        response = {"message": "Inputs wrong"}
        return Response(response,status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request):
        user = self.get_user(request.user.id)
        user.delete()
        response = {"message": "User deleted succesfully"}
        return Response(response, status=status.HTTP_204_NO_CONTENT)

class UserLoginAPIView(APIView):

    def post(self, request):

        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            if 'email' in serializer.validated_data:

                user = authenticate(username=serializer.validated_data['email'], password=serializer.validated_data['password'])

                if user :
                    user.last_login = timezone.now()
                    token,created = Token.objects.get_or_create(user=user)
                    response = {
                        "user_id":user.id,
                        "email":user.email,
                        "token":token.key
                    }

                    return Response(response, status=status.HTTP_200_OK)

                response = {"message": "Wrong credentials"}
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)

        response = {"message": "Required field(s) missing"}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class UserSignupAPIView(APIView):

    def post(self, request):

        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            if 'email' in serializer.validated_data:

                user = User.objects.filter(email=serializer.validated_data['email'])

                if user:
                    response = {"message":"Email already exists"}
                    return Response(response, status=status.HTTP_409_CONFLICT)

                serializer.save(username=serializer.validated_data['email'],company_name=serializer.validated_data['company_name'])
                response = {"message": "Successfully Signed up"}
                return Response(response, status=status.HTTP_201_CREATED)

        response = {"message": "Required field(s) missing"}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)



class UserHallAPIView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_hall(self, id):
        try:
            return Hall.objects.get(id=id)

        except Hall.DoesNotExist:
            response = {"message": "Hall with that id  doesn't exist"}
            return Response(response, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, id):
        hall = self.get_hall(id)
        if isinstance(hall, Hall):
            if hall.user.id == request.user.id:
                serializer = HallSerializer(hall)
                return Response(serializer.data, status.HTTP_200_OK)
            response = {"message": "Unauthorized"}
            return Response(response, status.HTTP_401_UNAUTHORIZED)
        return hall



    def put(self,request,id):
        data = json.loads(request.data['data'])
        data['name2'] = unidecode(data['name'])
        data['city_name'] = unidecode(City.objects.filter(id=data['city']).first().name)

        if data['phone'] == "":
            data['phone'] = None
        hall = self.get_hall(id)
        if isinstance(hall, Hall):
            if hall.user.id == request.user.id:
                serializer = HallSerializer(hall, data=data, partial=True)
                if serializer.is_valid():
                    serializer.update(hall, serializer.validated_data)
                    if 'greenToRed' in data:
                        for slot in data['greenToRed']:

                            s = Slot.objects.filter(pk=slot).first()
                            if s:
                                s.halls.add(hall)
                    if 'redToGreen' in data:
                        for slot in data['redToGreen']:
                            s = Slot.objects.filter(pk=slot).first()
                            if s:
                                s.halls.remove(hall)

                    session = Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)


                    s3_resource = session.resource('s3')
                    my_bucket = s3_resource.Bucket("my-wedding-hall-project")

                    obj = []
                    if data['deletedImages'] != []:
                        for image in data['deletedImages']:
                            obj.append({'Key':'images/'+str(hall.id)+'/'+image})

                        response = my_bucket.delete_objects(
                            Delete={
                                'Objects': obj,
                            }
                        )
                        images_to_delete = HallImage.objects.filter(hall=hall).filter(name__in=data['deletedImages'])
                        images_to_delete.delete()

                    images = iter(request.data)
                    next(images)
                    i = data['photo_number'] + 1

                    s3_client = session.client('s3')

                    S3_BUCKET = settings.AWS_STORAGE_BUCKET_NAME
                    FILE_PATH = 'images/'+str(hall.id)+'/'

                    print("entered")
                    for image in images:
                        print("before read")
                        hall_image = HallImage()
                        new_image = request.FILES[image]
                        pil_image_obj = Image.open(new_image)
                        (width, height) = pil_image_obj.size
                        factor = 0
                        factor1 = 0
                        factor2 = 0
                        if width > 1500:
                            factor1 = width/1500
                        if height > 1000:
                            factor2 = width/1000

                        factor = max(factor1,factor2,factor)
                        print("before resize")
                        if not (factor == 0):
                            size = (int(width / factor), int(height / factor))
                            pil_image_obj = pil_image_obj.resize(size, Image.ANTIALIAS)

                        new_image_io = BytesIO()
                        hall_image.hall = hall

                        pil_image_obj.save(new_image_io, "JPEG")


                        key = FILE_PATH + "image" + str(i)
                        new_image_io.seek(0)

                        config = TransferConfig( max_concurrency=20,
                                                use_threads=True)
                        print("before upload")
                        s3_client.upload_fileobj(new_image_io, S3_BUCKET, key,
                                                 ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'},
                                                 Config=config,
                                                 )

                        hall_image.name = "image"+str(i)
                        hall_image.save()
                        i = i + 1
                    return Response(serializer.data, status.HTTP_200_OK)

                response = {"message": "Inputs wrong"}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            response = {"message": "Unauthorized"}
            return Response(response, status.HTTP_401_UNAUTHORIZED)
        return hall


    def delete(self,request,id):
        hall = self.get_hall(id)
        if isinstance(hall, Hall):
            if hall.user.id == request.user.id:
                hall.delete()
                response = {"message": "Hall deleted succesfully"}
                return Response(response, status=status.HTTP_204_NO_CONTENT)
            response = {"message": "Unauthorized"}
            return Response(response, status.HTTP_401_UNAUTHORIZED)
        return hall


