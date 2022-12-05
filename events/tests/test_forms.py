from django.test import TestCase
from events.models import Event, Task, User 
from datetime import datetime, date, timedelta
from django.db import transaction, IntegrityError
from django.urls import reverse
from events.forms import *
from django.core.exceptions import ValidationError

class FormTests(TestCase):
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

#----------- FORM AND TEMPLATE ERROR MESSAGE TESTS -----------#

    #----------- EVENTS -----------#

    ## Test - successfully save event form for non-empty title, description, date, publish and autor 
    def test_post_create_event(self): 
        db_count = Event.objects.all().count()   
        login = self.client.login(username='annacarter', password='MyPassword123') 
        user1=User.objects.get(pk=1)
        data = {
            "title": "new task",
            "description": "new description",
            "date": date.today(),
            "publish": False,
            "author": user1.pk
        }
        form = EventForm(data) 
        self.assertTrue(form.is_valid())
        response = self.client.post(reverse('events_new'), data=data) 
        self.assertEqual(Event.objects.count(), db_count+1)

    ## Test - empty event title cannot be saved
    def test_post_not_create_event_no_title(self):   
        db_count = Event.objects.all().count()   
        login = self.client.login(username='annacarter', password='MyPassword123') 
        user1=User.objects.get(pk=1)
        data = {
            "title": "",
            "description": "new task",
            "date": date.today(),
            "publish": False,
            "author": user1.pk
        }
        form = EventForm(data) 
        self.assertFalse(form.is_valid())
        response = self.client.post(reverse('events_new'), data=data) 
        self.assertEqual(Event.objects.count(), db_count)

    ## Test - event title greater than 128 cannot be saved
    def test_post_not_create_event_long_title(self):   
        db_count = Event.objects.all().count()   
        login = self.client.login(username='annacarter', password='MyPassword123') 
        user1=User.objects.get(pk=1)
        data = {
            "title": "Winter Wedding Sophie and Charlie. Winter Wedding Sophie and Charlie. Winter Wedding Sophie and Charlie. Winter Wedding Sophie and Charlie. Winter Wedding Sophie and Charlie. Winter Wedding Sophie and Charlie. Winter Wedding Sophie and Charlie. Winter Wedding Sophie and Charlie.",
            "description": "new task",
            "date": date.today(),
            "publish": False,
            "author": user1.pk
        }
        form = EventForm(data) 
        self.assertFalse(form.is_valid())
        response = self.client.post(reverse('events_new'), data=data) 
        self.assertEqual(Event.objects.count(), db_count)

    ## Test - empty event description cannot be saved
    def test_post_not_create_event_no_description(self):  
        db_count = Event.objects.all().count()   
        login = self.client.login(username='annacarter', password='MyPassword123')    
        user1=User.objects.get(pk=1)
        data = {
            "title": "new task",
            "description": "",
            "date": date.today(),
            "publish": False,
            "author": user1.pk
        }
        form = EventForm(data) 
        self.assertFalse(form.is_valid())
        response = self.client.post(reverse('events_new'), data=data) 
        self.assertEqual(Event.objects.count(), db_count)

    ## Test - empty event date cannot be saved
    def test_post_not_create_event_no_date(self):
        db_count = Event.objects.all().count()   
        login = self.client.login(username='annacarter', password='MyPassword123') 
        user1=User.objects.get(pk=1)
        data = {
            "title": "new task",
            "description": "new description",
            "date": "",
            "publish": False,
            "author": user1.pk
        }
        form = EventForm(data) 
        self.assertFalse(form.is_valid())
        response = self.client.post(reverse('events_new'), data=data) 
        self.assertEqual(Event.objects.count(), db_count)

    ## Test - empty publish can be saved, default is set to False
    def test_post_create_event_no_publish(self): 
        db_count = Event.objects.all().count()     
        user1=User.objects.get(pk=1)
        login = self.client.login(username='annacarter', password='MyPassword123') 
        data = {
            "title": "Alice's Charity Event",
            "description": "new description",
            "date": date.today(),
            "author": user1.id
        }
        form = EventForm(data) 
        self.assertTrue(form.is_valid())
        response = self.client.post(reverse('events_new'), data=data) 
        self.assertEqual(Event.objects.count(), db_count+1)

    ## Test - if date is less than today do not create event
    def test_post_create_event_date_before_today(self):
        db_count = Event.objects.all().count()
        user1=User.objects.get(pk=1)
        login = self.client.login(username='annacarter', password='MyPassword123') 
        data={
            "title": "new event", 
            "description": " new description",
            "date": "2022-11-26",
            "publish": False, 
            "author": user1.id
        }
        form = EventForm(data) 
        self.assertFalse(form.is_valid())
        response = self.client.post(reverse('events_new'), data=data) 
        self.assertEqual(Event.objects.count(), db_count)

    #----------- EDIT EVENT TESTS -----------#

    ## Test - allow logged in user to edited the form
    def test_update_event_form(self):
        user1=User.objects.get(pk=1)
        login = self.client.login(username='annacarter', password='MyPassword123') 
        e1 = Event(title='Rugby Party', description="Location tbc", date = date.today(), publish = False, author=user1)
        form_data={'title':'Hockey Social Event', 'description':'test', 'date':date.today(), 'publish': False, 'author':user1}
        add_form=EventForm(data=form_data, instance=e1)
        add_form.save()
        self.assertEqual(e1.title, 'Hockey Social Event')

    ## Test - the edit event form. Event title can be edited when logged in
    def test_update_event_view_logged_in(self):
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
        login = self.client.login(username='annacarter', password='MyPassword123') 
        response = self.client.post(reverse('events_update', kwargs={'nid': new_event.pk}), data=data)        
        new_event.refresh_from_db()
        self.assertEqual(new_event.title, "edited_title")
        self.assertEqual(response.status_code, 302)


    ## Test - the edit event form. Event title cannot be edited when not logged in
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
        self.assertEqual(response.status_code, 302)


    #----------- TASKS -----------#

    ## Test - task with empty title cannot be saved to event in database
    def test_post_create_task_no_title(self): 
        db_count = Task.objects.all().count()
        event = Event.objects.get(pk=1) 
        person = Person.objects.get(pk=1)
        login = self.client.login(username='annacarter', password='MyPassword123') 
        data = {
            "title": "",
            "description": "new description",
            "deadline": date.today(),
            "complete": True, 
            "event": event.pk,
            "person": person.pk,
        }
        form = TaskForm(data) 
        self.assertFalse(form.is_valid())
        response = self.client.post(reverse('create_task', kwargs={'nid': event.pk}), data=data)
        self.assertEqual(Task.objects.count(), db_count)

    # Test - task object creation no login, does not create another task in database
    def test_post_create_task_no_login(self):
        db_count = Task.objects.all().count()
        event = Event.objects.get(pk=1) 
        person = Person.objects.get(pk=1)
        data = {
            "title": "Task title",
            "description": "new description",
            "complete": True, 
            "deadline": date.today(),
            "event": event.pk,
            "person": person.pk,
        }
        response = self.client.post(reverse('create_task', kwargs={'nid': event.pk}), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), db_count)

    # Test - task object creation with login, creates another task
    def test_post_create_task_with_login(self):
        db_count = Task.objects.all().count()
        login = self.client.login(username='annacarter', password='MyPassword123') 
        event = Event.objects.get(pk=1) 
        person = Person.objects.get(pk=1)
        data = {
            "title": "Task title",
            "description": "new description",
            "complete": True,
            "deadline": date.today(),
            "event": event.pk, 
            "person": person.pk,
        }
        response = self.client.post(reverse('create_task', kwargs={'nid': event.pk}), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), db_count+1)

    ## Test - task deadline date cannot be before todays date
    def test_post_create_task_deadline_before_today(self):
        db_count = Task.objects.all().count()
        login = self.client.login(username='annacarter', password='MyPassword123') 
        event = Event.objects.get(pk=1) 
        person = Person.objects.get(pk=1)
        data={
            "title": "Task title",
            "description": "new description",
            "complete": True,
            "deadline": "2019-11-26",
            "event": event.pk, 
            "person": person.pk,
        }
        form = TaskForm(data) 
        self.assertFalse(form.is_valid())
        response = self.client.post(reverse('create_task', kwargs={'nid': event.pk}), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), db_count)

    ## Test - task deadline cannot be set after event date
    def test_post_create_task_deadline_after_event_date(self):
        db_count = Task.objects.all().count()
        login = self.client.login(username='annacarter', password='MyPassword123') 
        # event date is 2024-11-21
        event = Event.objects.get(pk=1) 
        person = Person.objects.get(pk=1)
        data={
            "title": "Task title",
            "description": "new description",
            "complete": True,
            "deadline": "2025-11-26",
            "event": event.pk, 
            "person": person.pk,
        }
        form = TaskForm(data) 
        self.assertFalse(form.is_valid())
        response = self.client.post(reverse('create_task', kwargs={'nid': event.pk}), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), db_count)