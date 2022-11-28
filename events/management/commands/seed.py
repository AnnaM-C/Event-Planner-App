from django.core.management.base import BaseCommand 
from events.models import *

class Command(BaseCommand):

    def handle(self, *args, **options): 
        Person.objects.filter(name='Sandy').delete() 
        n=Person(name="Sandy") 
        n.save()
        n=Person(name="Tony") 
        n.save()
        n=Person(name="George") 
        n.save()
        self.stdout.write('done.')
