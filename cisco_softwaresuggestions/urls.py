# myapp/urls.py
from django.urls import path
from .views import get_ss

urlpatterns = [
    path('', get_ss, name='get_ss'),
]