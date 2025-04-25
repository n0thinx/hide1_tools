from django.urls import path
from .views import json_editor_view, download_json

urlpatterns = [
    path("", json_editor_view, name='json_editor'),
    path("download/", download_json, name='download_json'),
]
