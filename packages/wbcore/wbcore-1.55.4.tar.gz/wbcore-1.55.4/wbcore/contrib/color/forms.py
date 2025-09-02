from django_better_admin_arrayfield.forms.widgets import DynamicArrayWidget


class DynamicArrayColorWidget(DynamicArrayWidget):
    template_name = "wbcore/dynamic_color_array.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["default"] = "#ffffff"
        return context

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
