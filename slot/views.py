from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Slot
from .serializers import SlotSerializer
from hall.models import Hall
from hall.serializers import HallSerializer
from django.db.models import Q
import operator
from functools import reduce

class SlotListAPIView(APIView):

    def get(self,request):
        slots = Slot.objects.all()
        serializer = SlotSerializer(slots,many=True)

        return Response(serializer.data)

class SlotDetailAPIView(APIView):

    def get_slot(self, date):
        try:
            return Slot.objects.get(pk=date)

        except Slot.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, date):
        slot = self.get_slot(date)
        serializer = SlotSerializer(slot)
        halls = Hall.objects.filter(pk__in=serializer.data['halls'])

        available = serializer.data['available']
        hall_serializer = HallSerializer(halls, many=True)
        halls = hall_serializer.data
        data = {
            "available":available,
            "day":serializer.data['day'],
            "halls":halls,
        }

        return Response(data)

class SlotSearchAPIView(APIView):
    def get_slots(self,number,days,district):
        try:
            halls = Hall.objects.filter(city__id=number)
            if halls:
                if district:
                    halls_district = halls.filter(district__contains=district)
                    if halls_district:
                        return Slot.objects.filter(day__in=days).exclude(~Q(reduce(operator.and_, (Q(halls=x) for x in halls_district))))
                    return 
                return Slot.objects.filter(day__in=days).exclude(~Q(reduce(operator.and_, (Q(halls=x) for x in halls))))
        except Hall.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        data = request.data

        slots = self.get_slots(data['number'],data['days'],data['district'])
        serializer = SlotSerializer(slots,many=True)
        return Response(serializer.data)




