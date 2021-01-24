
from rest_framework.views import APIView
from portion.models import Portion
from rest_framework.response import Response
from rest_framework import status

class PortionDetailAPIView(APIView):

    def get_portion(self,hall,slot):

        try:
            return Portion.objects.filter(hall=hall,slot=slot)

        except Portion.DoesNotExist:
            return 1

    def get(self,request):

        response = request.GET.getlist('portion[]')

        portions = self.get_portion(request.GET.get('hall'), request.GET.get('slot'))
        x =  [[0 for y in range(len(request.GET.getlist('wedding_count[]')))] for x in range(24)]
        for i in range(24):
            for j in range(len(request.GET.getlist('wedding_count[]'))):
                if int(response[i]) == 0:
                    x[i][j] = 0
                elif int(response[i]) == 1:
                    x[i][j] = 1
                else:
                    x[i][j] = -1

        if portions != 1:
            for idx,portion in enumerate(portions):
                x[portion.spot][portion.wedding_count] = -1
            return Response(x,status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)




