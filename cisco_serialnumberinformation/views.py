# myapp/views.py
from django.shortcuts import render
from .forms import SerialNumberForm
from .sni import get_apikey, get_sni_data

def get_sni(request):
    api_key = None
    sni_data = None
    error_message_apikey = None
    error_message_sni_data = None

    if request.method == 'POST':
        form = SerialNumberForm(request.POST)
        if form.is_valid():
            serial_number = form.cleaned_data['serial_number']

            # Call your existing functions to get API key and EOX data
            api_key, error_message_apikey = get_apikey()
            if api_key:
                sni_data, error_message_sni_data = get_sni_data(api_key, serial_number)

    else:
        form = SerialNumberForm()

    return render(request, 'get_sni.html', {'form': form, 'api_key': api_key, 'sni_data': sni_data,
                                            'error_message_apikey': error_message_apikey,
                                            'error_message_sni_data': error_message_sni_data})