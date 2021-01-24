
from rest_framework.views import APIView
from portion.models import Portion
from rest_framework.response import Response
from rest_framework import status
from braces.views import CsrfExemptMixin

class PortionDetailAPIView(CsrfExemptMixin, APIView):
    authentication_classes = []
    def get_portion(self,hall,slot):

        try:
            return Portion.objects.filter(hall=hall,slot=slot)

        except Portion.DoesNotExist:
            return 1

    def put(self,request):
        response = request.data['portion']
        portions = self.get_portion(request.data['hall'], request.data['slot'])
        x =  [[0 for y in range(len(request.data['wedding_count']))] for x in range(24)]
        for i in range(24):
            for j in range(len(request.data['wedding_count'])):
                if response[i] == 0:
                    x[i][j] = 0
                elif response[i] == 1:
                    x[i][j] = 1
                else:
                    x[i][j] = -1

        if portions != 1:
            for idx,portion in enumerate(portions):
                x[portion.spot][portion.wedding_count] = -1
            return Response(x,status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)




