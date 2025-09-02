from collections import namedtuple

import pytest

from wbcore.serializers import Serializer
from wbcore.serializers.fields.number import IntegerField


class TestWBCoreSerializerFieldMixin:
    @pytest.fixture()
    def parent(self, context=None):
        if not context:
            context = {"view": object()}
        return Serializer(context=context)

    def test_read_only_callable(self):
        # check default readonly handling
        field = IntegerField(read_only=True)
        assert field.read_only is True

        field = IntegerField(read_only=False)
        assert field.read_only is False

        field = IntegerField(read_only=lambda x: True)
        assert field.read_only is True
        assert hasattr(field, "_callable_read_only")

    def test_bind_read_only_callable(self, parent):
        field = IntegerField(read_only=lambda view: False)
        field.bind("field", parent)
        assert field.read_only is False

    def test_view(self):
        view = object()
        Request = namedtuple("Request", ["parser_context"])
        request = Request({"view": view})

        c1 = {"view": view}
        c2 = {"request": request}

        field = IntegerField()
        p1 = Serializer(context=c1)
        field.bind("field", p1)
        assert field.view == view

        field = IntegerField()
        p1 = Serializer(context=c2)
        field.bind("field", p1)
        assert field.view == view

        field = IntegerField()
        p1 = Serializer()
        field.bind("field", p1)
        assert field.view is None
