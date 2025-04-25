# myapp/urls.py
from django.urls import path
from .views import get_sni

urlpatterns = [
    path('', get_sni, name='get_sni'),
]