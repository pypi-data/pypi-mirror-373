"""Minimal urlconf for testing purposes."""

from django.http import HttpResponse
from django.urls import path


def hello_world(request):
    return HttpResponse("Hello, world!")


urlpatterns = [
    path("", hello_world, name="home"),
]
