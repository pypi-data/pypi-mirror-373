from wbcore import viewsets

from wbcommission.models import CommissionType

from ..serializers import (
    CommissionTypeModelSerializer,
    CommissionTypeRepresentationSerializer,
)
from .display import CommissionTypeDisplayConfigClass


class CommissionTypeRepresentationModelViewSet(viewsets.RepresentationViewSet):
    serializer_class = CommissionTypeRepresentationSerializer
    queryset = CommissionType.objects.all()
    ordering_fields = search_fields = ordering = ["name"]


class CommissionTypeModelViewSet(viewsets.ModelViewSet):
    serializer_class = CommissionTypeModelSerializer
    queryset = CommissionType.objects.all()
    ordering_fields = search_fields = ordering = ["name"]
    display_config_class = CommissionTypeDisplayConfigClass
