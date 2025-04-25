from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import ActivityLog

@staff_member_required
def activity_log_view(request):
    logs = ActivityLog.objects.select_related('user').order_by('-timestamp')
    return render(request, 'log_list.html', {'logs': logs})
