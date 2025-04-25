from django.urls import path
from .views import upload_file, download_json

urlpatterns = [
    path("", upload_file, name="upload_file"),
    path('download-json/', download_json, name='download_as_json'),
]
