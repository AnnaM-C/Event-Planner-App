from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

#Event
class Event(models.Model):
 title = models.CharField(blank=False, max_length = 128, unique=True)
 description = models.TextField(blank=False)
 date = models.DateField(default=date.today, blank=False, validators=[MinValueValidator(limit_value=date.today)])
 publish = models.BooleanField(default=False)
 author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

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
 deadline = models.DateField(default=date.today, null=True, blank=False, validators=[MinValueValidator(limit_value=date.today)])
 event = models.ForeignKey(Event, on_delete=models.CASCADE)
 person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True)
 def __str__(self): 
    return self.title

class RegisteredEvent(models.Model):
   member = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)
   event = models.ForeignKey(Event, on_delete=models.CASCADE)


