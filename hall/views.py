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
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from api import settings


from boto3.session import Session
from boto3.s3.transfer import TransferConfig


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

            S3_BUCKET = settings.AWS_STORAGE_BUCKET_NAME
            FILE_PATH = 'images/' + str(hall.id) + '/'

            for image in images:
                hall_image = HallImage()
                hall.photo_number = hall.photo_number + 1
                new_image = request.FILES[image]
                pil_image_obj = Image.open(new_image)
                (width, height) = pil_image_obj.size
                factor = 0
                factor1 = 0
                factor2 = 0
                if width > 1500:
                    factor1 = width / 1500
                if height > 1000:
                    factor2 = width / 1000

                factor = max(factor1, factor2, factor)
                if not (factor == 0):
                    size = (int(width / factor), int(height / factor))
                    pil_image_obj = pil_image_obj.resize(size, Image.ANTIALIAS)

                new_image_io = BytesIO()
                hall_image.hall = hall
                pil_image_obj.save(new_image_io, format='JPEG')
                key = FILE_PATH + "image" + str(i)
                new_image_io.seek(0)

                config = TransferConfig(max_concurrency=20,
                                        use_threads=True,
                                        )

                s3_client.upload_fileobj(new_image_io, S3_BUCKET, key,
                                         ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'},
                                         Config=config,
                                         )

                hall_image.name = "image"+str(i)
                hall_image.save()
                i = i + 1
            hall.photo_number = i
            hall.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

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