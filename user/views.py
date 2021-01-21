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
from portion.models import Portion
from hall.serializers import HallSerializer
from .serializers import UserSerializer
import uuid
from unidecode import unidecode
from api import settings
import json

from boto3.session import Session
from botocore.client import Config

from django.conf import settings
from botocore.exceptions import ClientError

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

                    if 'greenToRed' in data:
                        for slot in data['greenToRed']:

                            s = Slot.objects.filter(pk=slot).first()
                            if s:
                                s.halls.add(hall)
                    if 'redToGreen' in data:

                        for slot in data['redToGreen']:
                            s = Slot.objects.filter(pk=slot).first()
                            if s:
                                numOf_portions = Portion.objects.filter(hall=hall, slot=s).count()
                                if(numOf_portions < hall.wedding_count * sum(hall.portion)):
                                    s.halls.remove(hall)
                                else:
                                    return Response(slot,status=status.HTTP_304_NOT_MODIFIED)

                    session = Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                            region_name="us-east-2")




                    s3_resource = session.resource(service_name='s3',region_name="us-east-2", config=Config(signature_version='s3v4'))

                    my_bucket = s3_resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

                    obj = []
                    if data['deletedImages'] != []:
                        for image in data['deletedImages']:
                            obj.append({'Key':'images/'+str(hall.id)+'/'+image + "/image"})

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
                    responses = []
                    s3_client = session.client('s3',region_name="us-east-2", config=Config(signature_version='s3v4'))
                    FILE_PATH = 'images/' + str(hall.id) + '/'
                    for image in images:

                        try:
                            name = uuid.uuid4()
                            s3_object_name = FILE_PATH + str(name) + "/" + "image.jpg"
                            response = s3_client.generate_presigned_post(
                                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                Key=s3_object_name,
                                ExpiresIn=3600,
                                Fields={"acl": "public-read", "Content-Type": 'multipart/form-data'},
                                Conditions=[
                                    {"acl": "public-read"},
                                    {"Content-Type": 'multipart/form-data'}
                                ]
                            )

                            responses.append(response)
                            hall_image = HallImage()
                            hall_image.hall = hall
                            hall_image.name =  str(name)
                            hall_image.save()
                        except ClientError as e:

                            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
                    serializer.update(hall, serializer.validated_data)
                    return Response(responses, status.HTTP_200_OK)

                response = {"message": "Inputs wrong"}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            response = {"message": "Unauthorized"}
            return Response(response, status.HTTP_401_UNAUTHORIZED)
        return hall


    def delete(self,request,id):
        hall = self.get_hall(id)
        if isinstance(hall, Hall):
            if hall.user.id == request.user.id:
                try:
                    hall.delete()
                    response = {"message": "Hall deleted succesfully"}
                    return Response(response, status=status.HTTP_204_NO_CONTENT)
                except:
                    response = {"message": "Unauthorized"}
                    return Response(response, status.HTTP_401_UNAUTHORIZED)

            response = {"message": "Unauthorized"}
            return Response(response, status.HTTP_401_UNAUTHORIZED)
        return hall

