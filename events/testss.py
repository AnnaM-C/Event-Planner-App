from django.test import TestCase
from .models import Event, Task, User
from datetime import datetime, date, timedelta
from django.db import transaction, IntegrityError
from django.urls import reverse
from .forms import *
from django.core.exceptions import ValidationError

class EventsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # User objects for testing
        user1 = User(username='annacarter', email='anna@surrey.ac.uk') 
        user1.set_password('MyPassword123')
        user1.full_clean
        user1.save()
        user2 = User(username='testadminuser', email='testadminuser@surrey.ac.uk') 
        user2.set_password('MyPassword123')
        user2.full_clean
        user2.save()
        user3 = User(username='testuser', email='testuser@surrey.ac.uk') 
        user3.set_password('MyPassword123')
        user3.full_clean
        user3.save()

        # Event objects for testing
        e1 = Event(title='Rugby Party', description="Location tbc", date = "2024-11-21", publish = False, author=user1) 
        e1.full_clean
        e1.save()
        e2 = Event(title='Alfies 1st Birthday', description="Location tbc", date = "2024-11-21", publish = False, author=user1) 
        e2.full_clean
        e2.save()
        # A Past event, pk=3
        e3 = Event(title='Charlies 1st Birthday', description="Location tbc", date = "2022-11-30", publish = False, author=user1) 
        e3.full_clean
        e3.save()

        # An event less than 7 days away from today, pk=5
        datetest = date.today()+timedelta(days=3)
        e5 = Event(title='Winterwonderland', description="Location", date = datetest, publish = False, author=user1) 
        e5.full_clean
        e5.save()

        # Person object for testing
        p1 = Person(name="Tony")
        p1.full_clean
        p1.save()

        # Task object for testing
        t1 = Task(title='Title task', description='task description', complete=True, deadline="2024-11-10", event=e1, person=p1)
        t1.full_clean
        t1.save()
        t2 = Task(title='Second task title', description='description 2', complete=False, deadline="2024-11-10", event=e1, person=p1)
        t2.full_clean
        t2.save()

        # RegisteredEvent object for testing
        re1 = RegisteredEvent(event=e1, member=user1)
        re1.full_clean
        re1.save()




    #----------- TEST TASK TEMPLATE VIEWS -----------#

#----------- TEST REGISTERED EVENT MODEL -----------#

