# myapp/views.py
from django.shortcuts import render
from .forms import SerialNumberForm
from .eox import get_apikey, get_eox_data, get_eox_data_2

def get_eox(request):
    api_key = None
    eox_data = None
    error_message_apikey = None
    error_message_eox_data = None

    if request.method == 'POST':
        form = SerialNumberForm(request.POST)
        if form.is_valid():
            search_type = form.cleaned_data['search_type']
            query_value = form.cleaned_data['search_value']
            api_key, error_message_apikey = get_apikey()
            if api_key:
                if search_type == 'serial_number':
                    eox_data, error_message_eox_data = get_eox_data(api_key, query_value)
                elif search_type == 'product_id':
                    eox_data, error_message_eox_data = get_eox_data_2(api_key, query_value)
    else:
        form = SerialNumberForm()

    return render(request, 'get_eox.html', {'form': form, 'api_key': api_key, 'eox_data': eox_data,
                                            'error_message_apikey': error_message_apikey,
                                            'error_message_eox_data': error_message_eox_data})