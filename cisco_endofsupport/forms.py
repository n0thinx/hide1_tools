# myapp/forms.py
from django import forms

# class SerialNumberForm(forms.Form):
#     serial_number = forms.CharField(label='Serial Number', max_length=100)
#     product_id = forms.CharField(label='Product ID', max_length=100)

class SerialNumberForm(forms.Form):
    SEARCH_CHOICES = [
        ('serial_number', 'Search by Serial Number'),
        ('product_id', 'Search by Product ID'),
    ]

    search_type = forms.ChoiceField(
        label='Search Type',
        choices=SEARCH_CHOICES,
        widget=forms.Select(),
    )

    search_value = forms.CharField(label='Search Value')