from django import forms
from .models import Event, Task

class EventForm(forms.ModelForm):
    # create meta class
    class Meta:
    # specify model to be used
        model = Event
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
            'class': 'formfield',
            'placeholder': 'Event Title',
            }),
            'description': forms.Textarea(attrs={
            'class': 'formfield',
            'placeholder': 'Event Description',
            'rows' : 25,
            'cols' : 60,
            }),
        }

class TaskForm(forms.ModelForm):
# create meta class
 class Meta:
# specify model to be used
  model = Task
  fields = ['title', 'description', 'complete', 'event']
  widgets = {
  'title': forms.TextInput(attrs={
  'class': 'formfield',
  'placeholder': 'Task Title',
  }),
  'description': forms.Textarea(attrs={
            'class': 'formfield',
            'placeholder': 'Task Description',
            'rows' : 25,
            'cols' : 60,
  }),
  'event': forms.HiddenInput(),
}