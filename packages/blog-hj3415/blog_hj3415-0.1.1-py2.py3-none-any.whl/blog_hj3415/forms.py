from django import forms

class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search',
            'class': 'form-control',
            'onchange': 'submit();'
        })
    )
