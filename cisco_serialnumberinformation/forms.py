# myapp/forms.py
from django import forms

class SerialNumberForm(forms.Form):
    serial_number = forms.CharField(label='Serial Number', max_length=100)
