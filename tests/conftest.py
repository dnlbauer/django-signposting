import pytest
from django.conf import settings


def pytest_sessionstart(session):
    print("test")
    settings.configure()
