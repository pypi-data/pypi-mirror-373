from wbcore import viewsets

from ..models import CompanyType, CustomerStatus, Position, Specialization
from ..serializers import (
    CompanyTypeModelSerializer,
    CompanyTypeRepresentationSerializer,
    CustomerStatusModelSerializer,
    CustomerStatusRepresentationSerializer,
    PositionModelSerializer,
    PositionRepresentationSerializer,
    SpecializationModelSerializer,
    SpecializationRepresentationSerializer,
)
from .display import (
    CompanyTypeDisplay,
    CustomerStatusDisplay,
    PositionDisplay,
    SpecializationDisplay,
)
from .titles.utils import (
    CompanyTypeTitleConfig,
    CustomerStatusTitleConfig,
    PositionTitleConfig,
    SpecializationTitleConfig,
)


class CustomerStatusModelViewSet(viewsets.ModelViewSet):
    LIST_DOCUMENTATION = "directory/markdown/documentation/customerstatus.md"
    queryset = CustomerStatus.objects.all()
    serializer_class = CustomerStatusModelSerializer
    display_config_class = CustomerStatusDisplay
    title_config_class = CustomerStatusTitleConfig
    search_fields = ("title",)
    filterset_fields = {
        "title": ["exact", "icontains"],
    }
    ordering_fields = ordering = ("title",)


class CustomerStatusRepresentationViewSet(viewsets.RepresentationViewSet):
    serializer_class = CustomerStatusRepresentationSerializer
    search_fields = ("title",)
    queryset = CustomerStatus.objects.all()


class PositionRepresentationViewSet(viewsets.RepresentationViewSet):
    serializer_class = PositionRepresentationSerializer
    search_fields = ("title",)
    queryset = Position.objects.all()


class PositionModelViewSet(viewsets.ModelViewSet):
    LIST_DOCUMENTATION = "directory/markdown/documentation/position.md"
    queryset = Position.objects.all()
    serializer_class = PositionModelSerializer
    display_config_class = PositionDisplay
    title_config_class = PositionTitleConfig
    search_fields = ("title",)
    filterset_fields = {
        "title": ["exact", "icontains"],
    }
    ordering_fields = ordering = ("title",)


class CompanyTypeModelViewSet(viewsets.ModelViewSet):
    LIST_DOCUMENTATION = "directory/markdown/documentation/companytype.md"
    queryset = CompanyType.objects.all()
    serializer_class = CompanyTypeModelSerializer
    display_config_class = CompanyTypeDisplay
    title_config_class = CompanyTypeTitleConfig
    search_fields = ("title",)
    filterset_fields = {
        "title": ["exact", "icontains"],
    }
    ordering_fields = ordering = ("title",)


class CompanyTypeRepresentationViewSet(viewsets.RepresentationViewSet):
    serializer_class = CompanyTypeRepresentationSerializer
    search_fields = ("title",)
    queryset = CompanyType.objects.all()


class SpecializationModelViewSet(viewsets.ModelViewSet):
    LIST_DOCUMENTATION = "directory/markdown/documentation/specialization.md"
    queryset = Specialization.objects.all()
    serializer_class = SpecializationModelSerializer
    display_config_class = SpecializationDisplay
    title_config_class = SpecializationTitleConfig
    search_fields = ("title",)
    filterset_fields = {
        "title": ["exact", "icontains"],
    }
    ordering_fields = ordering = ("title",)


class SpecializationRepresentationViewSet(viewsets.RepresentationViewSet):
    serializer_class = SpecializationRepresentationSerializer
    search_fields = ("title",)
    queryset = Specialization.objects.all()
