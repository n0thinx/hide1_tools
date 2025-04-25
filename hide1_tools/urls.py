from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path
from django.conf.urls import handler500, handler404
from django.shortcuts import render
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('tools-pm/', include('parser_app.urls')),
    path('tools-json/', include('json_editor.urls')),
    path('topology-drawer/', include('topology_drawer.urls')),
    path('tools-cisco/end-of-support/', include('cisco_endofsupport.urls')),
    path('tools-cisco/serial-number-information/', include('cisco_serialnumberinformation.urls')),
    path('register/', views.register_user, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('activity-log/', include('activity_log.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]

def custom_error_500(request):
    return render(request, '500.html', status=500)

handler500 = custom_error_500

def custom_error_404(request, exception):
    return render(request, '404.html', status=404)

handler404 = custom_error_404