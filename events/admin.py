from django.contrib import admin 
from .models import Event, Task, Person, RegisteredEvent

admin.site.register(Event) 
admin.site.register(Task)
admin.site.register(Person)
admin.site.register(RegisteredEvent)
