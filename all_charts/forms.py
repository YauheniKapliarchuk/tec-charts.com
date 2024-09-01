from django import forms

class DateForm(forms.Form):
    selected_date = forms.DateField(widget=forms.TextInput(attrs={
        'class': 'datepicker',
        'autocomplete': 'off'
    }))