from django.db import models

class Person(models.Model):
 name = models.CharField(max_length = 128)
 job = models.CharField(max_length = 128)
 
 class Meta:
   ordering = ['name']
   verbose_name_plural = "people"
   indexes = [models.Index(fields=['name']), ]

 def __str__(self): 
    return self.name

# Create your models here.
class Task(models.Model):
 title = models.CharField(max_length = 128)
 description = models.TextField()
 created_at = models.DateTimeField(auto_now_add=True)
 updated_at = models.DateTimeField(auto_now=True)
 persons = models.ManyToManyField(Person)

 class Meta:
   ordering = ['title']
   verbose_name_plural = "tasks"
   indexes = [models.Index(fields=['title']), ]

 def __str__(self): 
    return self.title

class Event(models.Model):
 title = models.CharField(max_length = 128)
 created_at = models.DateTimeField(auto_now_add=True)
 updated_at = models.DateTimeField(auto_now=True)
 tasks = models.ManyToManyField(Task)

 class Meta:
   ordering = ['title']
   verbose_name_plural = "events"
   indexes = [models.Index(fields=['title']), ]

 def __str__(self): 
    return self.title