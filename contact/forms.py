from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    subject = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=True)
    