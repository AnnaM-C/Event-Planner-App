from django.test import TestCase
from .models import Event, Task, User 
from datetime import datetime, date
from django.db import transaction, IntegrityError
from django.urls import reverse
from .forms import *


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

## Test if date is less than today -> does not create event
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

## Test - event can be deleted if user is logged in
    def test_delete_event_logged_in(self):
        db_count = Event.objects.all().count()
        event1=Event.objects.get(pk=1)
        login = self.client.login(username='annacarter', password='MyPassword123') 
        response = self.client.delete(reverse('events_delete', kwargs={'nid': event1.pk}))
        self.assertEqual(Event.objects.count(), db_count-1)

## Test - event cannot be deleted if user isnt logged in
    def test_delete_event_not_logged_in(self):
        db_count = Event.objects.all().count()
        event1=Event.objects.get(pk=1)
        response = self.client.delete(reverse('events_delete', kwargs={'nid': event1.pk}))
        self.assertEqual(Event.objects.count(), db_count)

## Test - allow logged in user to edited the form
    def test_update_event_form(self):
        user1=User.objects.get(pk=1)
        login = self.client.login(username='annacarter', password='MyPassword123') 
        e1 = Event(title='Rugby Party', description="Location tbc", date = date.today(), publish = False, author=user1)
        form_data={'title':'Hockey Social Event', 'description':'test', 'date':date.today(), 'publish': False, 'author':user1}
        add_form=EventForm(data=form_data, instance=e1)
        add_form.save()
        self.assertEqual(e1.title, 'Hockey Social Event')

# Test for the edit event view when logged in
    def test_update_event_view_logged_in(self):
        user1=User.objects.get(pk=1)
        data = {
            "title": "edited_title", 
            "description": "test", 
            "date":date.today(), 
            "publish": False, 
            "author": user1.pk
        }

        # self.valid_data={'title':'Rugby Social Event', 'description':'test', 'date':date.today(), 'author':user1}
        # self.obj = Event.objects.create(title='Hockey Social Event', description='test', date=date.today(), author=user1)
        # valid_data = model_to_dict(self.obj)
        # valid_data['title'] = 'Hocky Social'
        # form = EventForm(instance=self.obj)
        # # self.assertTrue(form.isValid())
        # case=form.save()
        # self.assertEqual(case.title, self.valid_data['title'])

        new_event = Event.objects.create(
            title="Hockey Social Event", 
            description="test", 
            date=date.today(), 
            publish=False, 
            author=user1
            )

        login = self.client.login(username='annacarter', password='MyPassword123') 
        response = self.client.post(reverse('events_update', kwargs={'nid': new_event.pk}), data=data)        
        new_event.refresh_from_db()
        # # self.assertEqual(getattr(Event.objects.get(pk=1),'title'), "Hockey Social Event")
        self.assertEqual(new_event.title, "edited_title")


# Test for the edit event view when not logged in
    def test_update_event_view_not_logged_in(self):
        user1=User.objects.get(pk=1)
        data = {
            "title": "edited_title", 
            "description": "test", 
            "date":date.today(), 
            "publish": False, 
            "author": user1.pk
        }
        new_event = Event.objects.create(
            title="Hockey Social Event", 
            description="test", 
            date=date.today(), 
            publish=False, 
            author=user1
            )
        response = self.client.post(reverse('events_update', kwargs={'nid': new_event.pk}), data=data)        
        new_event.refresh_from_db()
        self.assertNotEqual(new_event.title, "edited_title")