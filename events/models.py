from django.db import models

#Event
class Event(models.Model):
 title = models.CharField(max_length = 128)
 description = models.TextField()
 created_at = models.DateTimeField(auto_now_add=True)
 updated_at = models.DateTimeField(auto_now=True)

 def __str__(self): 
    return self.title

 class Meta:
  indexes = [models.Index(fields=['title']), ]

# Task
class Task(models.Model):
 title = models.CharField(max_length = 128)
 description = models.TextField()
 complete = models.BooleanField(default=False)
 event = models.ForeignKey(Event, on_delete=models.CASCADE)

 def __str__(self): 
    return self.title

# Person
class Person(models.Model):
 name = models.CharField(max_length = 128)
 job = models.CharField(max_length = 128)
 task = models.ForeignKey(Task, on_delete=models.CASCADE)

 def __str__(self): 
    return self.name