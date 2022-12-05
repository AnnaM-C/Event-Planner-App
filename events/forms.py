from django import forms 
from .models import *

class EventForm(forms.ModelForm):
    # create meta class
    class Meta:
    # specify model to be used
        model = Event
        fields = ['title', 'description', 'date', 'author']
        widgets = {
            'title': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Event Title',
            }),
            'description': forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Event Description',
            'rows' : 25,
            'cols' : 60,
            }),
            'date': forms.DateInput(attrs={
            'class': 'form-control',
            'placeholder': 'yyyy-mm-dd',
            }),
            'author': forms.HiddenInput(),
        }

class TaskForm(forms.ModelForm):
# create meta class
 class Meta:
# specify model to be used
  model = Task
  fields = ['title', 'description', 'deadline', 'complete', 'event', 'person']
  widgets = {
  'title': forms.TextInput(attrs={
    'class': 'form-control',
    'placeholder': 'Task Title',
    }),
  'description': forms.Textarea(attrs={
    'class': 'form-control',
    'placeholder': 'Task Description',
    'rows' : 5,
    'cols' : 40,
    }),
  'deadline': forms.DateInput(attrs={
            'class': 'form-control',
            'placeholder': 'yyyy-mm-dd',
            }),
  'event': forms.HiddenInput(),
  'person': forms.Select(
               choices=Person.objects.all()
            )
  }

  
  