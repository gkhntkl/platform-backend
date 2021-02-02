from rest_framework.views import APIView
from .models import Reservation,ReservationImage
from portion.models import Portion
from slot.models import Slot
from hall.models import Hall
from .serializers import ReservationSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.http import Http404
import uuid
import json
from django.conf import settings
from boto3.session import Session
from django.db import transaction
from botocore.client import Config
import maya
from datetime import datetime,timedelta
from django.utils.dateparse import parse_datetime
from django.utils import timezone
import boto3

session = Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

s3_client = session.client('sns','us-east-2')


from datetime import date,datetime,timedelta


from botocore.exceptions import ClientError


class ReservationDetailAPIView(APIView):

    def get_reservation(self, id):
        try:
            return Reservation.objects.get(id=id)
        except Reservation.DoesNotExist:
            raise Http404

    def get(self, request, id):

        reservation = self.get_reservation(id)
        if isinstance(reservation, Reservation):
                serializer = ReservationSerializer(reservation)
                return Response(serializer.data)

        return Response(status=status.HTTP_404_NOT_FOUND)

class ReservationSavePhotosAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_reservation(self, id):
        try:
            return Reservation.objects.get(id=id)
        except Reservation.DoesNotExist:
            raise Http404

    def get(self, request, id):

        reservation = self.get_reservation(id)
        if isinstance(reservation, Reservation):

            if reservation.hall.user.id == request.user.id:
                serializer = ReservationSerializer(reservation)

                urls = []

                s3_client = session.client('s3', region_name="us-east-2",
                                           config=Config(signature_version='s3v4'))
                for image in serializer.data['images']:
                    s3_object_name = "resized-photos" + "/" + str(reservation.id) + "/" + str(image) + "/" + "image.jpg"
                    url = s3_client.generate_presigned_url(
                        "get_object",
                        Params={
                            "Bucket": settings.AWS_STORAGE_BUCKET_NAME_RESIZED,
                            "Key": s3_object_name
                        },
                        ExpiresIn=3600
                    )
                    urls.append(url)
                response = {
                    "data":serializer.data,
                    "images":urls
                }
                return Response(response,status=status.HTTP_200_OK)
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return Response(status=status.HTTP_404_NOT_FOUND)

class ReservationUpdateAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_reservation(self, id):
        try:
            return Reservation.objects.get(id=id)
        except Reservation.DoesNotExist:
            raise Http404

    @transaction.atomic
    def createPortion(self,portion,hall,slot):
        dt = maya.parse(slot).datetime()
        if dt.hour > 21:
            dt = dt + timedelta(days=1)
            dt = dt.strftime("%Y-%m-%d")
        else:
            dt = dt.strftime("%Y-%m-%d")
        for portion in portion:
            Portion.objects.create(hall_id=hall, slot_id=dt, spot=portion[0], wedding_count=portion[1])


    def deletePortion(self,portion,hall,slot):

        if slot.hour > 21:
            slot = slot + timedelta(days=1)
        dt = slot.strftime("%Y-%m-%d")
        for portion in portion:
            Portion.objects.filter(hall_id=hall,slot_id=dt,spot=portion[0],wedding_count=portion[1]).delete()


    def put(self, request, id):
        reservation = self.get_reservation(id)

        if(reservation.date.date() < date.today()):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            if (request.user.id == reservation.hall.user.id):

                if request.data['hall'] != reservation.hall.id:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
                else:

                    if len(request.data['portion']) == 0:
                        if (request.data['close']):
                            s = Slot.objects.filter(pk=request.data['date'][0:10]).first()
                            if s:
                                s.halls.add(request.data['hall'])

                    else:

                        self.deletePortion(request.data['reservedPortion'], request.data['hall'], reservation.date)
                        self.createPortion(request.data['portion'], request.data['hall'], request.data['date'])

                        reservation.portion = request.data['portion']
                        if (not request.data['is_available']):
                            if reservation.date.strftime('%Y-%m-%d') != request.data['date'][0:10]:
                                s = Slot.objects.filter(pk=reservation.date).first()
                                if s:
                                    s.halls.remove(reservation.hall)

                                s = Slot.objects.filter(pk=request.data['date'][0:10]).first()
                                if s:
                                    s.halls.add(request.data['hall'])
                            else:
                                s = Slot.objects.filter(pk=request.data['date'][0:10]).first()
                                if s:
                                    s.halls.add(request.data['hall'])
                        else:
                            s = Slot.objects.filter(pk=reservation.date).first()
                            if s:
                                s.halls.remove(reservation.hall)

                    reservation.service_type = request.data['service_type']
                    reservation.name1 = request.data['name1']
                    reservation.name2 = request.data['name2']
                    reservation.phone = request.data['phone']
                    reservation.date = request.data['date']

                    reservation.save()
                return Response(status=status.HTTP_200_OK)

            return Response(status=status.HTTP_401_UNAUTHORIZED)


    def delete(self, request, id):
        reservation = self.get_reservation(id)
        if (request.user.id == reservation.hall.user.id):
            if (reservation.date.date()  < date.today()):
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            else:
                self.deletePortion(reservation.portion, reservation.hall, reservation.date)
                s = Slot.objects.filter(pk=reservation.date).first()
                if s:
                    s.halls.remove(reservation.hall)
                reservation.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_401_UNAUTHORIZED)


class ReservationCreateAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def createPortion(self,portion,hall,slot):

        for portion in portion:
            if portion[0] < 3:
                dt = maya.parse(slot).datetime()
                dt = dt + timedelta(days=1)
                dt = dt.strftime("%Y-%m-%d")
                Portion.objects.create(hall_id=hall, slot_id=dt, spot=portion[0], wedding_count=portion[1])

            else:
                Portion.objects.create(hall_id=hall,slot_id=slot[0:10],spot=portion[0],wedding_count=portion[1])


    def post(self, request, *args, **kwargs):

        if len(request.data['portion']) == 0:
            if (request.data['close']):
                s = Slot.objects.filter(pk=request.data['date'][0:10]).first()
                if s:
                    s.halls.add(request.data['hall'])
            return Response(status=status.HTTP_201_CREATED)

        else:
            serializer = ReservationSerializer(data=request.data, partial=True)
            if serializer.is_valid():
                hall = Hall.objects.get(id=request.data['hall'])
                if request.user.id == hall.user.id:
                    self.createPortion(request.data['portion'], request.data['hall'], request.data['date'])
                    reservation = serializer.save()
                    if (not request.data['is_available']):
                        s = Slot.objects.filter(pk=request.data['date'][0:10]).first()
                        if s:
                            s.halls.add(request.data['hall'])
                    else:
                        if (request.data['close']):
                            s = Slot.objects.filter(pk=request.data['date'][0:10]).first()
                            if s:
                                s.halls.add(request.data['hall'])
                    if request.data['smsChecked']:
                        phoneNumber = "+90" + request.data['phone']
                        message = "Merhabalar,\nRezervasyon detaylarınıza aşağıdaki linkten ulaşabilirsiniz.\n"+"salonayır.com/reservation/" + str(reservation.id)

                        if  hall.num_of_messages <  hall.quota_of_messages:
                            if phoneNumber != "+90":
                                s3_client.publish(PhoneNumber=phoneNumber,Message=message)
                                hall.num_of_messages = hall.num_of_messages + 1
                                hall.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReservationHallDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_hall_reservation(self, id, user):
        try:
            return Reservation.objects.filter(hall_id=id, hall__user=user,hidden=False).order_by('date')
        except Reservation.DoesNotExist:
            raise Http404

    def get(self, request, id):

        reservation = self.get_hall_reservation(id, request.user)
        serializer = ReservationSerializer(reservation, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReservationHideAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_hall_reservation(self, id):
        try:
            return Reservation.objects.get(id=id)
        except Reservation.DoesNotExist:
            raise Http404

    def get(self, request, id):

        reservation = self.get_hall_reservation(id)
        if request.user.id == reservation.hall.user.id:
            reservation.hidden = True
            reservation.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class ReservationAlbumAPIView(APIView):

    def get_reservation(self, id):
        try:
            return Reservation.objects.get(id=id)
        except Reservation.DoesNotExist:
            raise Http404

    def get(self, request, id):

        reservation = self.get_reservation(id)
        serializer = ReservationSerializer(reservation)
        return Response(serializer.data,status=status.HTTP_200_OK)

class ReservationPhotosAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_reservation(self, id):
        try:
            return Reservation.objects.get(id=id)
        except Reservation.DoesNotExist:
            raise Http404

    def get(self, request, id):

        reservation = self.get_reservation(id)
        serializer = ReservationSerializer(reservation)
        return Response(serializer.data,status=status)

    def post(self, request, id):
        reservation = self.get_reservation(id)
        data = json.loads(request.data['data'])

        if (request.user.id == reservation.hall.user.id):
            if reservation.date.date() + timedelta(days=60) < date.today():
                return Response(status=status.HTTP_304_NOT_MODIFIED)
            else:
                if reservation.hall.num_of_messages < reservation.hall.quota_of_messages:
                    session = Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                      region_name="us-east-2")

                    s3_client = session.client('s3', region_name="us-east-2",
                                               config=Config(signature_version='s3v4'))
                    s3_resource = session.resource('s3', region_name="us-east-2",
                                                   config=Config(signature_version='s3v4'))
                    my_bucket = s3_resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
                    my_bucket_resized = s3_resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME_RESIZED)
                    obj = []
                    obj_resized = []
                    if data['deletedImages'] != []:
                        for image in data['deletedImages']:
                            obj.append({'Key': 'photos/' + str(reservation.id) + '/' + image + "/image.jpg"})
                            obj_resized.append(
                                {'Key': 'resized-photos/' + str(reservation.id) + '/' + image + "/image.jpg"})

                        response = my_bucket.delete_objects(
                            Delete={
                                'Objects': obj,
                            }
                        )
                        response = my_bucket_resized.delete_objects(
                            Delete={
                                'Objects': obj_resized,
                            }
                        )
                        images_to_delete = ReservationImage.objects.filter(reservation=reservation).filter(
                            name__in=data['deletedImages'])
                        images_to_delete.delete()

                    images = iter(request.data)
                    next(images)

                    responses = []
                    num_images = 0
                    for image, idx in enumerate(images):

                        num_images = num_images + 1
                        try:
                            name = uuid.uuid4()
                            s3_object_name = "photos" + "/" + str(id) + "/" + str(name) + "/" + "image.jpg"
                            response = s3_client.generate_presigned_post(
                                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                Key=s3_object_name,
                                ExpiresIn=3600
                            )
                            responses.append(response)
                            reservation_image = ReservationImage()
                            reservation_image.name = name
                            reservation_image.reservation = reservation
                            reservation_image.save()
                        except ClientError as e:
                            reservation.hall.num_of_images = reservation.hall.num_of_images + idx
                            reservation.num_of_unpaid = reservation.num_of_unpaid + idx
                            reservation.save()
                            reservation.hall.save()
                            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)

                    phoneNumber = "+90" + reservation.phone
                    message = "Merhabalar,Linkten Ulaşabileceğiniz Albümünüz Güncellenmiştir.\nBizi Tercih Ettiğiniz için Teşekkür Ederiz.\n" + "Albüm Şifresi:" + str(
                        reservation.code) + "\nsalonayır.com/photos/" + str(
                        reservation.id)
                    if phoneNumber != "+90":
                        s3_client = session.client('sns', 'us-east-2')
                        s3_client.publish(PhoneNumber=phoneNumber, Message=message)

                        reservation.hall.num_of_messages = reservation.hall.num_of_messages + 1

                    if data['duration'] != 0 and data['duration'] < 21:
                        reservation.duration = data['duration']
                        reservation.save()
                    reservation.hall.num_of_images = reservation.hall.num_of_images + num_images
                    reservation.hall.save()
                    reservation.num_of_unpaid += (num_images - len(data['deletedImages']))
                    reservation.save()
                    return Response(responses, status=status.HTTP_200_OK)
                else:
                    return Response([], status.HTTP_417_EXPECTATION_FAILED)

        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, id):
        reservation = self.get_reservation(id)
        if (request.user.id == reservation.hall.user.id):
            if reservation.date.date()+timedelta(days=60) < date.today():
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            else:
                reservation.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

class ReservationCheckAuthAPIView(APIView):

    def get_reservation(self, id):
        try:
            return Reservation.objects.get(id=id)
        except Reservation.DoesNotExist:
            raise Http404

    def post(self, request):

        reservation = self.get_reservation(request.data['id'])

        if str(reservation.code) == request.data['code']:
            if not (reservation.num_of_unpaid > 0):
                s3_client = session.client('s3', region_name="us-east-2",
                                           config=Config(signature_version='s3v4'))
                if (reservation.date + timedelta(weeks=24)) > timezone.now():
                    serializer = ReservationSerializer(reservation)
                    images = ReservationImage.objects.filter(reservation=reservation)
                    responses = []

                    for image in images:
                        s3_object_name = "photos" + "/" + str(reservation.id) + "/" + str(
                            image.name) + "/" + "image.jpg"
                        s3_object_name_resized = "resized-photos" + "/" + str(reservation.id) + "/" + str(
                            image.name) + "/" + "image.jpg"

                        response = s3_client.generate_presigned_url(
                            "get_object",
                            Params={
                                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                                "Key": s3_object_name
                            },
                            ExpiresIn=3600
                        )
                        response_resized = s3_client.generate_presigned_url(
                            "get_object",
                            Params={
                                "Bucket": settings.AWS_STORAGE_BUCKET_NAME_RESIZED,
                                "Key": s3_object_name_resized,
                            },
                            ExpiresIn=3600
                        )
                        image_urls = {
                            "original": response,
                            "thumbnail": response_resized
                        }
                        responses.append(image_urls)
                    res = {
                        "images": responses,
                        "data": serializer.data
                    }
                    return Response(res, status=status.HTTP_200_OK)
                else:
                    if reservation.count_of_visit < 300:
                        serializer = ReservationSerializer(reservation)
                        reservation.count_of_visit += 1
                        reservation.save()
                        images = ReservationImage.objects.filter(reservation=reservation)
                        responses = []
                        for image in images:
                            s3_object_name = "photos" + "/" + str(reservation.id) + "/" + str(
                                image.name) + "/" + "image.jpg"
                            s3_object_name_resized = "resized-photos" + "/" + str(reservation.id) + "/" + str(
                                image.name) + "/" + "image.jpg"
                            response = s3_client.generate_presigned_url(
                                "get_object",
                                Params={
                                    "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                                    "Key": s3_object_name,
                                },
                                ExpiresIn=3600
                            )
                            response_resized = s3_client.generate_presigned_url(
                                "get_object",
                                Params={
                                    "Bucket": settings.AWS_STORAGE_BUCKET_NAME_RESIZED,
                                    "Key": s3_object_name_resized,
                                },
                                ExpiresIn=3600
                            )

                            image_urls = {
                                "original": response,
                                "thumbnail": response_resized
                            }
                            responses.append(image_urls)

                        res = {
                            "images": responses,
                            "data": serializer.data
                        }
                        return Response(res, status=status.HTTP_200_OK)
                    else:
                        return Response(status=status.HTTP_403_FORBIDDEN)
            else:
                return Response(status=status.HTTP_402_PAYMENT_REQUIRED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
