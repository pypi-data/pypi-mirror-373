import json
import types

from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.renderers import JSONRenderer


class PandasDataCustomEncoder(json.JSONEncoder):
    def default(self, obj):
        # We need to handle generator for option request that sometime contains generator as values
        if isinstance(obj, types.GeneratorType):
            return list(obj)
        return DjangoJSONEncoder().default(obj)


class PandasDataCustomRenderer(JSONRenderer):
    encoder_class = PandasDataCustomEncoder
    strict = False
