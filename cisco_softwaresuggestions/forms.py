# myapp/forms.py
from django import forms

class SerialNumberForm(forms.Form):
    product_id = forms.CharField(label='Product ID', max_length=100)
