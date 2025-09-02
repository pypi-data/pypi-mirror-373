from pytest_factoryboy import register
from wbcore.tests.conftest import *
from wbnews.factories import NewsFactory, NewsSourceFactory

register(NewsSourceFactory)
register(NewsFactory)
