from wbcore.contrib.guardian.filters import ObjectPermissionsFilter
from wbcore.viewsets.mixins import FilterMixin


class GuardianFilterMixin(FilterMixin):
    filter_backends = (ObjectPermissionsFilter, *FilterMixin.filter_backends)
