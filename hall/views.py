from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Hall,HallImage
from city.models import City
from .serializers import HallSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
import json
from unidecode import unidecode
import logging
import uuid
from botocore.exceptions import ClientError
from api import settings


from boto3.session import Session


class HallListAPIView(APIView):

    def get(self,request):
        halls = Hall.objects.all()
        serializer = HallSerializer(halls,many=True)

        return Response(serializer.data)


class HallCreateAPIView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = json.loads(request.data['data'])
        data['name2'] = unidecode(data['name'])
        data['city_name'] = unidecode(City.objects.filter(id=data['city']).first().name)
        if data['phone'] == "":
            data['phone'] = None
        if(len(request.data) == 1):
            return Response("Image Required", status=status.HTTP_400_BAD_REQUEST)
        serializer = HallSerializer(data=data)

        if serializer.is_valid():
            hall = serializer.save()
            hall.user = request.user

            images = iter(request.data)
            next(images)
            i = 0
            session = Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

            s3_client = session.client('s3')

            FILE_PATH = 'images/' + str(hall.id) + '/'
            responses = []

            for image in images:

                try:
                    name = uuid.uuid4()
                    hall_image = HallImage()
                    hall.photo_number = hall.photo_number + 1
                    hall_image.hall = hall
                    hall_image.name = name
                    hall_image.save()
                    s3_object_name = FILE_PATH + str(name) + "/" + "image.jpg"
                    response = s3_client.generate_presigned_post(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=s3_object_name,
                        ExpiresIn=3600
                    )
                    responses.append(response)
                except ClientError as e:
                    logging.error(e)
                    return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)

            hall.save()
            return Response(responses, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HallDetailAPIView(APIView):
    def get_hall(self,id):
        try:
            return Hall.objects.get(id=id)

        except Hall.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self,request,id):
        hall = self.get_hall(id)
        serializer = HallSerializer(hall)
        return Response(serializer.data)


class HallSearchAPIView(APIView):
    def get_hall(self,number,date,district):
        try:
            if number == -1:
                halls = Hall.objects.all().exclude(slots__day=date)
            else:
                if district == "":
                    halls = Hall.objects.filter(city_id=number).exclude(slots__day=date)
                else:
                    halls =  Hall.objects.filter(city_id=number).exclude(slots__day=date).filter(district__contains=district)
            return halls
        except Hall.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        data = request.data
        halls = self.get_hall(data['number'],data['date'],data['district'])
        serializer = HallSerializer(halls,many=True)
        return Response(serializer.data)


class HallNameSearchAPIView(APIView):
    def get_hall(self,name):
        try:
            name = unidecode(name)
            halls =  Hall.objects.filter(Q(name2__icontains=name) | Q(city_name__icontains=name))
            return halls
        except Hall.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        name = request.data['name']
        halls = self.get_hall(name)
        serializer = HallSerializer(halls,many=True)
        return Response(serializer.data)