from pytest_factoryboy import register
from wbcore.tests.conftest import *

from ..factories import CurrencyFactory, CurrencyFXRatesFactory

register(CurrencyFactory)
register(CurrencyFXRatesFactory)
