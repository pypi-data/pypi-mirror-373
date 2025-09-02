from django_filters import Filter

from wbcore.filters.mixins import WBCoreFilterMixin


class MultipleLookupFilter(WBCoreFilterMixin):
    def __init__(self, field_class, lookup_expr, **kwargs):
        self.field_class = field_class
        self.lookup_expr = lookup_expr
        self.kwargs = kwargs

    def get_filters(self, field_name) -> dict[str, Filter]:
        filters = dict()
        for lookup_expr in self.lookup_expr:
            filters[f"{field_name}__{lookup_expr}"] = self.field_class(
                lookup_expr=lookup_expr,
                **self.kwargs,
            )

        return filters
