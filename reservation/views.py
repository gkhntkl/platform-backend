from rest_framework.views import APIView
from .models import Reservation
from .serializers import ReservationSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.http import Http404
from hall.models import Hall

class ReservationDetailAPIView(APIView):

    def get_reservation(self,id):
        try:
            return Reservation.objects.get(id=id)
        except Reservation.DoesNotExist:
            raise Http404

    def get(self,request,id):
        reservation = self.get_reservation(id)
        if isinstance(reservation,Reservation):
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

class ReservationAPIView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            reservation = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ReservationHallDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_hall_reservation(self,id,user):
        try:
            return Reservation.objects.filter(hall_id=id,hall__user=user).order_by('date')
        except Reservation.DoesNotExist:
            raise Http404

    def get(self,request,id):
        reservation = self.get_hall_reservation(id,request.user)
        serializer = ReservationSerializer(reservation,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
