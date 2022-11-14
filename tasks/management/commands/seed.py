from django.core.management.base import BaseCommand 
from tasks.models import *

class Command(BaseCommand):
    def handle(self, *args, **options): 
        Person.objects.all().delete()
        p=Person(name="Sandy", job="Event Manager") 
        p.save()
        p=Person(name="John", job="Event Manager") 
        p.save()
        p=Person(name="Ralph", job="Event Manager") 
        p.save()
        self.stdout.write('done.')