from django.db.models import CharField


class IconField(CharField):
    description = "A field storing an icon"

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if "choices" in kwargs:
            del kwargs["choices"]
        return name, path, args, kwargs
