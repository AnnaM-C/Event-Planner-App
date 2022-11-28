from django.db import models
from datetime import datetime
from .validators import *

#Event
class Event(models.Model):
 title = models.CharField(max_length = 128, unique=True)
 description = models.TextField(blank=False)
 date = models.DateTimeField(default=datetime.now, blank=False, validators=[present_or_future_date])
 updated_at = models.DateTimeField(auto_now=True)

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
 title = models.CharField(max_length = 128)
 description = models.TextField()
 complete = models.BooleanField(default=False)
 deadline = models.DateTimeField(default=datetime.now, null=True, blank=True)
 event = models.ForeignKey(Event, on_delete=models.CASCADE)
 person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True)
 def __str__(self): 
    return self.title



# Intermediate relationship Task -> Person line item
# A task can have 0 or more line items
# A person can be in 0 or more line items
class LineItem(models.Model):
 person = models.ForeignKey(Person, on_delete=models.CASCADE)
 task = models.ForeignKey(Task, on_delete=models.CASCADE)

 def __str__(self):
    return str(self.person)