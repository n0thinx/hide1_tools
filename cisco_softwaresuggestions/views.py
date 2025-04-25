# myapp/views.py
from django.shortcuts import render
from .forms import SerialNumberForm
from .ss import get_apikey, get_ss_data

def get_ss(request):
    api_key = None
    ss_data = None
    error_message_apikey = None
    error_message_ss_data = None

    if request.method == 'POST':
        form = SerialNumberForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data['product_id']

            # Call your existing functions to get API key and SS data
            api_key, error_message_apikey = get_apikey()
            if api_key:
                ss_data, error_message_ss_data = get_ss_data(api_key, product_id)

    else:
        form = SerialNumberForm()

    return render(request, 'get_ss.html', {'form': form, 'api_key': api_key, 'ss_data': ss_data,
                                            'error_message_apikey': error_message_apikey,
                                            'error_message_ss_data': error_message_ss_data})