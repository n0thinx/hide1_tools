from django import forms

class UploadJSONForm(forms.Form):
    file = forms.FileField(label="Upload JSON file")

class ReorderForm(forms.Form):
    move_key = forms.ChoiceField(label="Key to Move")
    after_key = forms.ChoiceField(label="Move After")
