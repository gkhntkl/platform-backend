from rest_framework.views import APIView
from .models import Reservation,ReservationImage
from .serializers import ReservationSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.http import Http404
import uuid

from django.conf import settings
from boto3.session import Session

import logging
import boto3
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


class ReservationUpdateAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_reservation(self, id):
        try:
            return Reservation.objects.get(id=id)
        except Reservation.DoesNotExist:
            raise Http404

    def put(self, request, id):
        reservation = self.get_reservation(id)
        serializer = ReservationSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            if (request.user.id == reservation.hall.user.id):
                reservation = serializer.update(reservation, serializer.validated_data)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        reservation = self.get_reservation(id)
        if (request.user.id == reservation.hall.user.id):
            reservation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class ReservationCreateAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print(2)
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            reservation = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReservationHallDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_hall_reservation(self, id, user):
        try:
            return Reservation.objects.filter(hall_id=id, hall__user=user).order_by('date')
        except Reservation.DoesNotExist:
            raise Http404

    def get(self, request, id):

        reservation = self.get_hall_reservation(id, request.user)
        serializer = ReservationSerializer(reservation, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

        if (request.user.id == reservation.hall.user.id):

            session = Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

            s3_client = session.client('s3')

            images = request.data

            responses = []
            for image in images:

                try:
                    name = uuid.uuid4()
                    s3_object_name = "photos" + "/"  + str(id) + "/" + str(name)
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
                    logging.error(e)
                    return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)

            return Response(responses, status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, id):
        reservation = self.get_reservation(id)
        if (request.user.id == reservation.hall.user.id):
            reservation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
