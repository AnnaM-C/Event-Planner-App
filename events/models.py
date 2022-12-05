from django.db import models
from django.contrib.auth.models import User
from datetime import date, datetime
from django.core.validators import MinValueValidator, MaxLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

# def get_event_date(self) -> date:
#    date_found = Event.objects.filter(date=self.date)

#Event
class Event(models.Model):
 title = models.CharField(blank=False, max_length = 128, unique=True)
 description = models.TextField(blank=False)
 date = models.DateField(default=date.today, blank=False, validators=[MinValueValidator(limit_value=date.today)])
 publish = models.BooleanField(default=False, null=False)
 author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)

 def __str__(self): 
    return self.title

 class Meta:
  indexes = [models.Index(fields=['title']), ]

# Person
class Person(models.Model):
 name = models.CharField(max_length = 128)

 def __str__(self): 
    return self.name

# Task
class Task(models.Model):
 title = models.CharField(blank=False, max_length = 128)
 description = models.TextField(blank=False)
 complete = models.BooleanField(default=False)
 event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=False)
 deadline = models.DateField(default=date.today, blank=False, validators=[MinValueValidator(limit_value=date.today)])
 person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True)

 def clean(self):
   event_date= self.event.date
   deadline= self.deadline
   if(str(deadline) > str(event_date)):
      raise ValidationError("Deadline date cannot be greater than event date - " + str(event_date) + "!")
   if(str(deadline) == ''):
      raise ValidationError("Deadline date cannot be empty!")
   return deadline

 def __str__(self): 
    return self.title

class RegisteredEvent(models.Model):
   member = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)
   event = models.ForeignKey(Event, on_delete=models.CASCADE)


