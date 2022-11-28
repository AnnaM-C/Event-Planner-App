from django import forms 
from .models import *

class EventForm(forms.ModelForm):
    # create meta class
    class Meta:
    # specify model to be used
        model = Event
        fields = ['title', 'description', 'date']
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
            'date': forms.DateTimeInput(),
        }

class TaskForm(forms.ModelForm):
# create meta class
 class Meta:
# specify model to be used
  model = Task
  fields = ['title', 'description', 'deadline', 'complete', 'event', 'person']
  widgets = {
  'title': forms.TextInput(attrs={
  'class': 'formfield',
  'placeholder': 'Task Title',
  }),
  'description': forms.Textarea(attrs={
            'class': 'formfield',
            'placeholder': 'Task Description',
            'rows' : 5,
            'cols' : 40,
  }),
  'deadline': forms.DateInput(),
  'event': forms.HiddenInput(),
  'person': forms.Select(
               choices=Person.objects.all()
            )
  }

  
  