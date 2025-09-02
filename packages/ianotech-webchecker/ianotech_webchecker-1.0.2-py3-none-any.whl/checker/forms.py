from django import forms

class URLCheckForm(forms.Form):
    url = forms.URLField(
        max_length=255,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter website URL (e.g., https://google.com)',
            'required': True
        })
    )