from django import forms
class ContactForm(forms.Form):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'formfield'}))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class': 'formfield'}))
    subject = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'formfield'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'formfield'}), required=True)
    