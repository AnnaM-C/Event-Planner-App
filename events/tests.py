from django.test import TestCase
from .models import Event, Task, User 
from datetime import datetime, date
from django.db import transaction, IntegrityError
from django.urls import reverse
from .forms import *


class EventsTests(TestCase):
    @classmethod
    def setUpTestData(cls):

        # User objects for testing
        user1 = User(username='annacarter', email='anna@surrey.ac.uk') 
        user1.set_password('MyPassword123')
        user1.save()
        user2 = User(username='testadminuser', email='testadminuser@surrey.ac.uk') 
        user2.set_password('MyPassword123')
        user2.save()
        user3 = User(username='testuser', email='testuser@surrey.ac.uk') 
        user2.set_password('MyPassword123')
        user3.save()

        # Event objects for testing
        e1 = Event(title='Rugby Party', description="Location tbc", date = date.today(), publish = False, author=user1) 
        e1.save()
        e2 = Event(title='Alfies 1st Birthday', description="Location tbc", author=user1) 
        e2.save()

        # Person object for testing
        p1 = Person(name="Tony")
        p1.save()

        # Task object for testing
        t1 = Task(title='Title task', description='task description', complete=True, deadline=date.today(), event=e1, person=p1)
        t1.save()
        t2 = Task(title='Second task title', description='description 2', complete=False, deadline=date.today(), event=e1, person=p1)
        t2.save()


#----------- EVENT TESTS for forms, views, models and authentication -----------#

## Test - Login user
    def test_login(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        self.assertTrue(login)

## Test - Save an event to database
    def test_save_event(self):
        db_count = Event.objects.all().count() 
        user1=User.objects.get(pk=1)
        event = Event(title='Christmas Brunch', description='At the ned', author=user1) 
        event.save()
        self.assertEqual(db_count+1, Event.objects.all().count())

## Test - successfully save event form for non-empty title, description and deadline 
    def test_post_create_event(self): 
        data = {
            "title": "new task",
            "description": "new description",
            "date": date.today(),
        }
        form = EventForm(data) 
        self.assertTrue(form.is_valid())

## Test - empty event title cannot be saved
    def test_post_create_task_no_title(self):     
        data = {
            "title": "",
            "description": "new task",
            "date": date.today(),
        }
        form = EventForm(data) 
        self.assertFalse(form.is_valid())

## Test - empty event description cannot be saved
    def test_post_create_task_no_description(self):     
        data = {
            "title": "new task",
            "description": "",
            "date": date.today(),
        }
        form = EventForm(data) 
        self.assertFalse(form.is_valid())

## Test - empty event date cannot be saved
    def test_post_create_task_no_date(self):     
        data = {
            "title": "new task",
            "description": "new description",
            "date": None,
        }
        form = EventForm(data) 
        self.assertFalse(form.is_valid())

## Test - duplicate event title (event titles are unique)
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

## Test - protected URL's
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
        self.assertEqual(response.status_code, 302)

    def test_post_create_event_with_login(self):
        db_count = Event.objects.all().count()
        user1=User.objects.get(pk=1)
        login = self.client.login(username='annacarter', password='MyPassword123') 
        data={
            "title": "new event", 
            "description": " new description",
            "date": date.today(), 
            "author": user1.pk
        }
        response = self.client.post(reverse('events_new'), data=data) 
        self.assertEqual(response.status_code, 302)
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
            "author": user1.id
        }
        response = self.client.post(reverse('events_new'), data=data) 
        self.assertEqual(Event.objects.count(), db_count)

## Test - event deleted if user is logged in
    def test_delete_event_logged_in(self):
        db_count = Event.objects.all().count()
        event1=Event.objects.get(pk=1)
        login = self.client.login(username='annacarter', password='MyPassword123') 
        response = self.client.delete(reverse('events_delete', kwargs={'nid': event1.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Event.objects.count(), db_count-1)

## Test - event cannot be deleted if user isnt logged in
    def test_delete_event_not_logged_in(self):
        db_count = Event.objects.all().count()
        event1=Event.objects.get(pk=1)
        response = self.client.delete(reverse('events_delete', kwargs={'nid': event1.pk}))
        self.assertEqual(response.status_code, 302)
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

## Test - the edit event view. Event title can be edited when logged in
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


## Test - the edit event view. Event title cannot be edited when not logged in
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


#----------- TASK TESTS for forms, views, models and authentication -----------#

# Test - non-empty title, description and deadline successfully save task to event
    def test_post_create_task(self): 
        event = Event.objects.get(pk=1) 
        person = Person.objects.get(pk=1)
        data = {
            "title": "new task",
            "description": "new description",
            "deadline": date.today(),
            "complete": True, 
            "event": event,
            "person": person,
        }
        form = TaskForm(data) 
        self.assertTrue(form.is_valid())

## Test - task with empty title cannot be saved to event in database
    def test_post_create_task_no_title(self): 
        event = Event.objects.get(pk=1) 
        person = Person.objects.get(pk=1)
        data = {
            "title": "",
            "description": "new description",
            "deadline": date.today(),
            "complete": True, 
            "event": event,
            "person": person,
        }
        form = TaskForm(data) 
        self.assertFalse(form.is_valid())

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

## Test - task deleted object if user is logged in. Test view, check the delete_success response is true
    def test_delete_task_logged_in(self):
        db_count = Task.objects.all().count()
        task = Task.objects.get(pk=1)
        login = self.client.login(username='annacarter', password='MyPassword123') 
        data = {
            "task_id": task.pk
        }
        response = self.client.get(reverse('delete_task'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = response.json()
        self.assertEqual(Task.objects.count(), db_count-1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['delete_success'], True)

# Test - task cannot be deleted if user isnt logged in. Test view, check the delete_success response is false
    def test_delete_task_not_logged_in(self):
        db_count = Task.objects.all().count()
        task = Task.objects.get(pk=1)
        data = {
            "task_id": task.pk
        }
        response = self.client.get(reverse('delete_task'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), db_count)

# Test - task can be complete with ajax function when user is logged in.
    def test_complete_task_logged_in(self):
        login = self.client.login(username='annacarter', 
        password='MyPassword123') 
        # The task.pk=2 attribute complete set up as false
        task = Task.objects.get(pk=2)
        data = {
            "task_id": task.pk
        }
        response = self.client.get(reverse('complete_task'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['complete'], True)

# Test - task can be set to uncomplete with ajax function when user is logged in.
    def test_set_to_not_complete_task_logged_in(self):
        login = self.client.login(username='annacarter', 
        password='MyPassword123') 
        # The task.pk=1 attribute complete set up as true
        task = Task.objects.get(pk=1)
        data = {
            "task_id": task.pk
        }
        response = self.client.get(reverse('complete_task'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['complete'], False)


# Test - task can be edited with ajax function when user is logged in.
    def test_edit_task_logged_in(self):
        login = self.client.login(username='annacarter', 
        password='MyPassword123') 
        event=Event.objects.get(pk=1)
        person=Person.objects.get(pk=1)
        # The task.pk=1 attribute complete set up as true
        new_task = Task.objects.create(
            title="Create guest list",
            description="Number of people 4",
            complete=True,
            deadline=date.today(),
            event = event,
            person=person,
        )
        data = {
            "taskId": new_task.pk,
            "taskTitle": "New_Title",
            "taskDescription": "New description",
            "eventId": event.pk,
        }
        response = self.client.post(reverse('task_ajax_update'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        new_task.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(new_task.title, "New_Title")

