from wbcore import viewsets

from wbaccounting.models import InvoiceType
from wbaccounting.serializers import (
    InvoiceTypeModelSerializer,
    InvoiceTypeRepresentationSerializer,
)
from wbaccounting.viewsets.display import InvoiceTypeDisplayConfig
from wbaccounting.viewsets.titles import InvoiceTypeTitleConfig


class InvoiceTypeModelViewSet(viewsets.ModelViewSet):
    queryset = InvoiceType.objects.all()
    serializer_class = InvoiceTypeModelSerializer
    search_fields = ordering_fields = ("name", "processor")
    ordering = ("name", "id")
    display_config_class = InvoiceTypeDisplayConfig
    filterset_fields = {"name": ["exact", "icontains"], "processor": ["exact", "icontains"]}
    title_config_class = InvoiceTypeTitleConfig


class InvoiceTypeRepresentationViewSet(viewsets.RepresentationViewSet):
    serializer_class = InvoiceTypeRepresentationSerializer
    queryset = InvoiceType.objects.all()
    search_fields = ordering_fields = ("name",)
    ordering = ("name", "id")
