# myapp/urls.py
from django.urls import path
from .views import get_eox

urlpatterns = [
    path('', get_eox, name='get_eox'),
]