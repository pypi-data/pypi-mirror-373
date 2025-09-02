from collections import namedtuple

import pandas as pd
import pytest
from rest_framework.test import APIRequestFactory

from wbcore.contrib.pandas.filters import PandasOrderingFilter
from wbcore.viewsets import ViewSet


class TestPandasOrderingFilter:
    @pytest.fixture
    def ordering_filter(self):
        return PandasOrderingFilter()

    @pytest.fixture
    def view(self, base_ordering_fields, ordering_fields):
        class BaseView(ViewSet):
            def get_ordering_fields(self):
                return base_ordering_fields

            ordering = ordering_fields

        return BaseView()

    @pytest.fixture
    def df(self, ordering_fields):
        return pd.DataFrame(
            [[1] * len(ordering_fields), [2] * len(ordering_fields)],
            columns=map(lambda x: x.replace("-", ""), ordering_fields),
        )

    @pytest.fixture
    def queryset(self):
        # dummy iterable to assert that the filter queryset method doesn't touch the queryset
        return [namedtuple("Point", "x y")]

    @pytest.fixture
    def filter_request(self, ordering_fields):
        factory = APIRequestFactory()
        request = factory.get(f'/?ordering={",".join(ordering_fields)}')
        request.query_params = request.GET
        return request

    @pytest.mark.parametrize(
        "base_ordering_fields, ordering_fields, expected_ordering_fields, expected_ascending",
        [
            (["a", "b"], ["a"], ["a"], [True]),
            (["a", "b"], ["c"], [], []),
            (["a", "b"], ["-a"], ["a"], [False]),
            (["a", "b"], ["-a", "b"], ["a", "b"], [False, True]),
        ],
    )
    def test_get_ordering(
        self,
        base_ordering_fields,
        ordering_fields,
        expected_ordering_fields,
        expected_ascending,
        ordering_filter,
        filter_request,
        df,
        view,
    ):
        res_ordering_fields, res_ascending = ordering_filter.get_ordering(filter_request, df, view)
        assert list(res_ordering_fields) == expected_ordering_fields
        assert list(res_ascending) == expected_ascending

    @pytest.mark.parametrize(
        "base_ordering_fields, ordering_fields, expected_ordering_fields, expected_ascending",
        [
            (["a", "b"], ["a"], ["a"], [True]),
            (["a", "b"], ["c"], [], []),
            (["a", "b"], ["-a"], ["a"], [False]),
            (["a", "b"], ["-a", "b"], ["a", "b"], [False, True]),
        ],
    )
    def test_get_ordering_without_query_params(
        self,
        base_ordering_fields,
        ordering_fields,
        expected_ordering_fields,
        ordering_filter,
        expected_ascending,
        df,
        rf,
        view,
    ):
        rf.query_params = {}
        res_ordering_fields, res_ascending = ordering_filter.get_ordering(rf, df, view)
        assert list(res_ordering_fields) == expected_ordering_fields
        assert list(res_ascending) == expected_ascending

    @pytest.mark.parametrize(
        "base_ordering_fields, ordering_fields",
        [
            (["a", "b"], ["a"]),
        ],
    )
    def test_filter_queryset(
        self, base_ordering_fields, ordering_fields, ordering_filter, filter_request, queryset, view
    ):
        assert ordering_filter.filter_queryset(filter_request, queryset, view) == queryset

    @pytest.mark.parametrize(
        "base_ordering_fields, ordering_fields",
        [
            (["a", "b"], ["-a"]),
        ],
    )
    def test_filter_dataframe(self, base_ordering_fields, ordering_fields, ordering_filter, filter_request, df, view):
        assert list(ordering_filter.filter_dataframe(filter_request, df, view)["a"].values) == [
            2,
            1,
        ]  # we just check that ordering is applied
