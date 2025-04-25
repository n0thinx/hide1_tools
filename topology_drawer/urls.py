from django.urls import path
from .views import upload_json_view

urlpatterns = [
    path('', upload_json_view, name="upload_json"),
]
