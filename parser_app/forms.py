from django import forms

class MultiFileUploadForm(forms.Form):
    files = forms.FileField(required=True)