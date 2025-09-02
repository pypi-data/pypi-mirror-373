from wbcore import viewsets

from wbportfolio.models import PortfolioCashTarget
from wbportfolio.serializers import PortfolioCashTargetModelSerializer


class PortfolioCashTargetModelViewSet(viewsets.ModelViewSet):
    queryset = PortfolioCashTarget.objects.all()
    serializer_class = PortfolioCashTargetModelSerializer
