from django.test import TestCase
from .models import Event, Task, User 
from datetime import datetime, date
from django.db import transaction, IntegrityError
from django.urls import reverse

class EventsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user1 = User(username='annacarter', email='anna@surrey.ac.uk') 
        user1.set_password('MyPassword123')
        user1.save()
        user2 = User(username='testadminuser', email='testadminuser@surrey.ac.uk') 
        user2.set_password('MyPassword123')
        user2.save()
        user3 = User(username='testuser', email='testuser@surrey.ac.uk') 
        user2.set_password('MyPassword123')
        user3.save()

        e1 = Event(title='Rugby Party', description="Location tbc", date = date.today(), publish = False, author=user1) 
        e1.save()
        e2 = Event(title='Alfies 1st Birthday', description="Location tbc", author=user1) 
        e2.save()

## Add users to events
    def test_login(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        self.assertTrue(login)

## Save an event
    def test_save_event(self):
        db_count = Event.objects.all().count() 
        user1=User.objects.get(pk=1)

        event = Event(title='Christmas Brunch', description='At the ned', author=user1) 
        event.save()
        self.assertEqual(db_count+1, Event.objects.all().count())

## Test duplicate event title
    def test_duplicate_title(self):
        db_count = Event.objects.all().count()
        user1=User.objects.get(pk=1)
        event = Event(title='Rugby Party', description="Social event", author=user1) 
        #with self.assertRaises(IntegrityError):
        try:
            with transaction.atomic(): 
                event.save()
        except IntegrityError: 
            pass
        self.assertNotEqual(db_count+1, Event.objects.all().count())

# ## Test protected URL's
    def test_post_create_event_no_login(self): 
        db_count = Event.objects.all().count() 
        user1=User.objects.get(pk=1)
        data={
            "title": "new Event", 
            "description": " new description", 
            "date": date.today(),
            "author": user1
        }
        response = self.client.post(reverse('events_new'), data=data) 
        self.assertEqual(Event.objects.count(), db_count)

    def test_post_create_event_with_login(self):
        db_count = Event.objects.all().count()
        user1=User.objects.get(pk=1)
        login = self.client.login(username='annacarter', password='MyPassword123') 
        data={
            "title": "new event", 
            "description": " new description",
            "date": date.today(), 
            "author": user1.id
        }
        response = self.client.post(reverse('events_new'), data=data) 
        self.assertEqual(Event.objects.count(), db_count+1)

## Test if date is less than today
    def test_post_create_event_date_before_today(self):
        db_count = Event.objects.all().count()
        user1=User.objects.get(pk=1)
        login = self.client.login(username='annacarter', password='MyPassword123') 
        data={
            "title": "new event", 
            "description": " new description",
            "date": "2022-11-26", 
            "author": user1.id
        }
        response = self.client.post(reverse('events_new'), data=data) 
        self.assertEqual(Event.objects.count(), db_count)