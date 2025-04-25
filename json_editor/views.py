import json
from collections import OrderedDict
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from .forms import UploadJSONForm, ReorderForm
from django.http import JsonResponse

# Function to download the JSON file
def download_json(request):
    if request.method == 'POST':
        # Fetch the JSON data from the session or form
        json_data = request.session.get('json_data')  # This assumes data is stored in session
        if json_data:
            response = JsonResponse(json.loads(json_data), safe=False)  # Decode JSON
            response['Content-Disposition'] = 'attachment; filename="reordered_data.json"'
            return response
    return HttpResponseBadRequest('Invalid request')

# Function to move a key in the JSON object
def move_key_after(obj, move_key, after_key):
    new_obj = OrderedDict()
    for key in obj:
        if key == after_key:
            new_obj[key] = obj[key]
            if move_key in obj:
                new_obj[move_key] = obj[move_key]
        elif key != move_key:
            new_obj[key] = obj[key]
    return new_obj

# View to handle JSON upload, reorder, and display
def json_editor_view(request):
    uploaded_data = None
    updated_keys = None
    json_obj = None

    if request.method == 'POST':
        if 'upload' in request.POST:
            upload_form = UploadJSONForm(request.POST, request.FILES)
            if upload_form.is_valid():
                json_file = upload_form.cleaned_data['file']
                try:
                    # Load the uploaded JSON data as an OrderedDict
                    json_data = json.load(json_file, object_pairs_hook=OrderedDict)
                except json.JSONDecodeError as e:
                    return HttpResponseBadRequest(f"Invalid JSON format: {str(e)}")

                # Store the loaded JSON in the session
                request.session['json_data'] = json.dumps(json_data)

                reorder_form = ReorderForm()
                keys = list(json_data.keys())
                reorder_form.fields['move_key'].choices = [(k, k) for k in keys]
                reorder_form.fields['after_key'].choices = [(k, k) for k in keys]

                return render(request, 'reorder.html', {
                    'upload_form': upload_form,
                    'reorder_form': reorder_form,
                    'keys': keys,
                    'json_data': json_data  # Pass the JSON data to the template
                })

        elif 'reorder' in request.POST:
            # Retrieve the stored JSON from the session
            json_data = json.loads(request.session.get('json_data'), object_pairs_hook=OrderedDict)
            keys = list(json_data.keys())

            reorder_form = ReorderForm(request.POST)
            reorder_form.fields['move_key'].choices = [(k, k) for k in keys]
            reorder_form.fields['after_key'].choices = [(k, k) for k in keys]

            if reorder_form.is_valid():
                move_key = reorder_form.cleaned_data['move_key']
                after_key = reorder_form.cleaned_data['after_key']

                if move_key != after_key:
                    updated_data = move_key_after(json_data, move_key, after_key)
                    request.session['json_data'] = json.dumps(updated_data)
                    updated_keys = list(updated_data.keys())

                return render(request, 'reorder.html', {
                    'upload_form': UploadJSONForm(),
                    'reorder_form': reorder_form,
                    'keys': updated_keys,
                    'json_data': updated_data,
                    'updated_json_data': json.dumps(updated_data, indent=4)  # Pretty print the JSON
                })

    else:
        upload_form = UploadJSONForm()
        reorder_form = None

    return render(request, 'reorder.html', {
        'upload_form': upload_form,
        'json_data': {}  # Pass an empty dictionary if no data exists
    })
