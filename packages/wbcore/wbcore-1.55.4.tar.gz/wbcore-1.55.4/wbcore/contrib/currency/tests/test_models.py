from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from pytest_mock import MockerFixture

from wbcore.contrib.currency.models import Currency, CurrencyFXRates


@pytest.mark.model_tests
@pytest.mark.with_db
@pytest.mark.django_db
class TestSpecificModels:
    @pytest.fixture
    def base_currency(self, mocker: MockerFixture):
        base_currency = Currency()
        mocker.patch.object(base_currency, "key", "ABC")
        return base_currency

    @pytest.fixture
    def other_currency(self, mocker: MockerFixture):
        base_currency = Currency()
        mocker.patch.object(base_currency, "key", "XYZ")
        return base_currency

    @pytest.fixture
    def base_fx_rate(self, mocker: MockerFixture):
        base_fx_rate = CurrencyFXRates()
        mocker.patch.object(base_fx_rate, "value", 0.85)
        return base_fx_rate

    @pytest.fixture
    def other_fx_rate(self, mocker: MockerFixture):
        other_fx_rate = CurrencyFXRates()
        mocker.patch.object(other_fx_rate, "value", 1.15)
        return other_fx_rate

    @pytest.mark.parametrize("exact_lookup", [True, False])
    def test_convert(
        self,
        exact_lookup,
        mocker: MockerFixture,
        base_currency,
        other_currency,
        base_fx_rate,
        other_fx_rate,
    ):
        # Arrange
        today = timezone.now().date()
        if exact_lookup:
            mocker.patch(
                "wbcore.contrib.currency.models.CurrencyFXRates.objects.get",
                side_effect=[base_fx_rate, other_fx_rate],
            )
        else:
            mock_filter = mocker.patch("wbcore.contrib.currency.models.CurrencyFXRates.objects.filter")
            mock_filter.return_value.order_by.return_value.first.side_effect = [
                base_fx_rate,
                other_fx_rate,
            ]

        # Act
        new_fx_rates = base_currency.convert(today, other_currency, exact_lookup)

        # Assert
        assert new_fx_rates == (1 / base_fx_rate.value) * other_fx_rate.value

    def test_convert_with_date_today_exists(self, currency_factory, currency_fx_rates_factory):
        currency = currency_factory(key="EUR")
        other_currency = currency_factory(key="CHF")
        today = timezone.now().date()
        fx_rates = currency_fx_rates_factory(date=today, currency=currency)
        other_fx_rates = currency_fx_rates_factory(date=today, currency=other_currency)
        new_fx_rates = currency.convert(fx_rates.date, other_currency)
        assert new_fx_rates == (1 / fx_rates.value) * other_fx_rates.value

    def test_convert_with_date_lte(self, currency_factory, currency_fx_rates_factory):
        date_test = timezone.now().date() - timedelta(days=1)
        currency = currency_factory(key="EUR")
        other_currency = currency_factory(key="CHF")
        today = timezone.now().date()
        fx_rates = currency_fx_rates_factory(date=date_test, currency=currency)
        other_fx_rates = currency_fx_rates_factory(date=date_test, currency=other_currency)
        new_fx_rates = currency.convert(today, other_currency)
        assert new_fx_rates == (1 / fx_rates.value) * other_fx_rates.value

    def test_get_fx_rates_subquery_normal_date(self, currency_fx_rates_factory):
        today = timezone.now().date()
        fx_rates = currency_fx_rates_factory(date=today)

        qs = CurrencyFXRates.objects.annotate(fx_rate=fx_rates.get_fx_rates_subquery(today, currency="currency"))

        fx_rate = [fx_r.get("fx_rate") for fx_r in qs.filter(id=fx_rates.id).values("fx_rate")]
        assert len(fx_rate) == 1
        assert isinstance(fx_rate[0], Decimal)

    def test_get_fx_rates_subquery_outerref_date(self, currency_fx_rates_factory):
        today = timezone.now().date()
        fx_rates = currency_fx_rates_factory(date=today)
        qs = CurrencyFXRates.objects.annotate(fx_rate=fx_rates.get_fx_rates_subquery("date", currency="currency"))
        fx_rate = [fx_r.get("fx_rate") for fx_r in qs.filter(id=fx_rates.id).values("fx_rate")]
        assert len(fx_rate) == 1
        assert isinstance(fx_rate[0], Decimal)

    def test_get_fx_rates_subquery_for_two_currencies(self, currency_fx_rates_factory):
        today = timezone.now().date()
        fx_rates = currency_fx_rates_factory(date=today)
        qs = CurrencyFXRates.objects.annotate(
            fx_rate=fx_rates.get_fx_rates_subquery_for_two_currencies("date", "currency", "currency")
        )
        fx_rate = [fx_r.get("fx_rate") for fx_r in qs.filter(id=fx_rates.id).values("fx_rate")]
        assert len(fx_rate) == 1
        assert isinstance(fx_rate[0], Decimal)
        assert fx_rate[0] == Decimal("1.0")
