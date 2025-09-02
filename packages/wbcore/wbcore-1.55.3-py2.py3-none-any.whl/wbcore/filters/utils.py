import os

from django_filters.constants import EMPTY_VALUES

from .defaults import RequiredFilterMissing


def check_required_filters(request, view, filter):
    if "PYTEST_CURRENT_TEST" not in os.environ and getattr(view, "action", "list") == "list":
        errors = []
        for required_field in [
            label for label, filter in filter.base_filters.items() if getattr(filter, "required", False)
        ]:
            if filter.form.cleaned_data.get(required_field, None) in EMPTY_VALUES:
                errors.append(required_field)
        if errors:
            raise RequiredFilterMissing(
                detail={
                    "filter_errors": {field: ["This filter is required. Please specify a value"] for field in errors},
                }
            )
