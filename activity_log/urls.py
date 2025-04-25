from django.urls import path
from .views import activity_log_view

urlpatterns = [
    path('', activity_log_view, name='activity_log_view'),
]
