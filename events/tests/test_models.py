from django.test import TestCase
from events.models import Event, Task, User 
from datetime import date, timedelta
from django.db import transaction, IntegrityError
from django.urls import reverse
from events.forms import *
from django.core.exceptions import ValidationError




class ModelTests(TestCase):
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

#----------- AUTHENTICATION TESTS -----------#

    #----------- EVENTS -----------#

    ## Test - cannot create event when not logged in
    def test_post_create_event_no_login(self): 
        db_count = Event.objects.all().count() 
        user1=User.objects.get(pk=1)
        data={
            "title": "new Event", 
            "description": " new description", 
            "date": date.today(),
            "publish": False,
            "author": user1
        }
        response = self.client.post(reverse('events_new'), data=data, follow=True)
        self.assertEqual(Event.objects.count(), db_count)
        self.assertEqual(response.status_code, 200)

    ## Test - can create event when logged in
    def test_post_create_event_with_login(self):
        db_count = Event.objects.all().count()
        user1=User.objects.get(pk=1)
        login = self.client.login(username='annacarter', password='MyPassword123') 
        data={
            "title": "new event", 
            "description": " new description",
            "date": date.today(),
            "publish": True, 
            "author": user1.pk
        }
        response = self.client.post(reverse('events_new'), data=data, follow=True) 
        self.assertEqual(Event.objects.count(), db_count+1)
        self.assertEqual(response.status_code, 200)


    #----------- TASK AUTHENTICATION -----------#

    ## Test - non-empty title, description, deadline and logged in user successfully save task to event
    def test_post_create_task_logged_in(self): 
        db_count = Task.objects.all().count()
        event = Event.objects.get(pk=1) 
        person = Person.objects.get(pk=1)
        login = self.client.login(username='annacarter', password='MyPassword123') 
        data = {
            "title": "new task",
            "description": "new description",
            "deadline": date.today(),
            "complete": True, 
            "event": event.pk,
            "person": person.pk,
        }
        response = self.client.post(reverse('create_task', kwargs={'nid': event.pk}), data=data, follow=True)
        self.assertEqual(Task.objects.count(), db_count+1)
        self.assertEqual(response.status_code, 200)


    ## Test - non-empty title, description, deadline and not logged cannot save task to event
    def test_post_create_task_not_logged_in(self): 
        db_count = Task.objects.all().count()
        event = Event.objects.get(pk=1) 
        person = Person.objects.get(pk=1)
        data = {
            "title": "new task",
            "description": "new description",
            "deadline": date.today(),
            "complete": True, 
            "event": event.pk,
            "person": person.pk,
        }
        response = self.client.post(reverse('create_task', kwargs={'nid': event.pk}), data=data, follow=True)
        self.assertEqual(Task.objects.count(), db_count)
        self.assertEqual(response.status_code, 200)


#----------- MODEL TESTS -----------#

    #----------- EVENTS MODEL -----------#

    ## Test - Save an event with valid inputs to database
    def test_event_save_event(self):
        db_count = Event.objects.all().count() 
        user1=User.objects.get(pk=1)
        event = Event(title='Christmas Brunch', description='At the ned', date='2024-11-26', publish=True, author=user1) 
        event.save()
        self.assertEqual(db_count+1, Event.objects.all().count())
        self.assertTrue(event.clean)

    ## Test - cannot save duplicate event title (event titles are unique)
    def test_event_model_duplicate_title(self):
        db_count = Event.objects.all().count()
        user1=User.objects.get(pk=1)
        event = Event(title='Rugby Party', description="Social event", date='2024-11-26', publish=False, author=user1) 
        try:
            with transaction.atomic(): 
                event.save()
        except IntegrityError: 
            pass
        self.assertEqual(db_count, Event.objects.all().count())
        self.assertRaises(ValidationError, event.full_clean)

    # Test - cannot save title greater than 128 characters (event titles have max-length 128)
    def test_event_model_title_max_length(self):
        user1=User.objects.get(pk=1)
        event = Event(title='Winter Wedding For Sophie and Charlie in the Cotswolds. Winter Wedding For Sophie and Charlie in the Cotswolds. Winter Wedding For Sophie and Charlie in the Cotswolds. Winter Wedding For Sophie and Charlie in the Cotswolds. Winter Wedding For Sophie and Charlie in the Cotswolds. Winter Wedding For Sophie and Charlie in the Cotswolds.', description='At the ned', date='2024-11-26', publish=False, author=user1) 
        self.assertRaises(ValidationError, event.full_clean)      

    ## Test - cannot save empty author field
    def test_event_model_test_author_required(self):
        try:
            event = Event(title="Pottery Class", description="Social event", date='2024-11-26') 
        except TypeError:
            pass
        self.assertTrue(TypeError, event.save())

    ## Test - cannot save empty event title (event titles are required)
    def test_event_model_title_required(self):
        user1=User.objects.get(pk=1)
        event = Event(description="Social event", date='2024-11-26', publish=False, author=user1) 
        self.assertRaises(ValidationError, event.full_clean)

    ## Test - cannot save empty event description (event descriptions are required)
    def test_event_model_description_required(self):
        user1=User.objects.get(pk=1)
        event = Event(title="Pottery Class", date='2024-11-26', publish=False, author=user1) 
        self.assertRaises(ValidationError, event.full_clean)

    ## Test - cannot save empty event date (event dates are required)
    def test_event_model_date_required(self):
        user1=User.objects.get(pk=1)
        event = Event(title="Pottery Class", description="Social event", date="", publish=False, author=user1) 
        self.assertRaises(ValidationError, event.full_clean)

    ## Test - cannot save date before todays date (event dates are to be set in the future)
    def test_event_model_date_less_than_today(self):
        user1=User.objects.get(pk=1)
        event = Event(title="Pottery Class", description="Social event", date='2021-11-26', publish=False, author=user1) 
        self.assertRaises(ValidationError, event.full_clean)

    ## Test - cannot save publish field as null (publish field is either True or False)
    def test_event_model_test_publish_not_null(self):
        user1=User.objects.get(pk=1)
        event = Event(title="Pottery Class", description="Social event", date='2024-11-26', publish="Null", author=user1) 
        self.assertRaises(ValidationError, event.full_clean)

    ## Test - can save empty publish field (publish field is false by default)
    def test_event_model_test_publish_not_required(self):
        user1=User.objects.get(pk=1)
        event = Event(title="Pottery Class", description="Social event", date='2024-11-26', author=user1) 
        self.assertTrue(event.full_clean)

    ## Test - cannot create a published event with date in the past
    def test_cannot_create_publish_event_with_date_in_past(self):
        user1=User.objects.get(pk=1)
        event = Event(title="Pottery Class", description="Social event", date='2021-11-26', publish=True, author=user1) 
        self.assertRaises(ValidationError, event.full_clean)


    #----------- PERSON MODEL -----------#

    ## Test - a new person can be saved in a model
    def test_model_save_person(self):
        db_count = Person.objects.all().count()
        person = Person(name="Charlie")
        person.save() 
        self.assertEqual(db_count+1, Person.objects.all().count())
        self.assertTrue(person.clean)

    # Test - cannot save name greater than 128 characters (names have max-length 128)
    def test_person_model_name_max_length(self):
        person = Person(name="CharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlieCharlie")
        self.assertRaises(ValidationError, person.full_clean)  

    # Test - cannot person without a name (event titles have max-length 128)
    def test_model_person_name_required(self):
        person = Person(name="")
        self.assertRaises(ValidationError, person.full_clean) 

    #----------- REGISTERED EVENTS MODEL -----------#

    ## Test - Save a registered event with valid inputs to database
    def test_registered_event_save(self):
        db_count = RegisteredEvent.objects.all().count() 
        user=User.objects.get(pk=1)
        event=Event.objects.get(pk=1)
        re = RegisteredEvent(event=event, member=user) 
        re.save()
        self.assertEqual(db_count+1, RegisteredEvent.objects.all().count())
        self.assertTrue(re.clean)

    ## Test - cannot save with empty member (member field is required)
    def test_registered_event_model_member_required(self):
        event=Event.objects.get(pk=1)
        try:
            re = RegisteredEvent(event=event) 
        except TypeError:
            pass
        self.assertRaises(TypeError, re.save())

    ## Test - cannot save with empty event (event field is required)
    def test_registered_event_model_event_required(self):
        user=User.objects.get(pk=1)
        try:
            re = RegisteredEvent(member=user) 
        except TypeError:
            pass
        self.assertRaises(TypeError, re.save())

    # Test - cannot register for an event in the past
    def test_registered_to_event_in_past(self):
        user=User.objects.get(pk=2)
        event1 = Event(title='Winter Wedding For Sophie and Charlie.', description='Time tbc', date='2021-11-26', publish=False, author=user) 
        re = RegisteredEvent(event=event1, member=user) 
        self.assertRaises(ValidationError, re.full_clean)

    #----------- TASK MODEL -----------#

    ## Test - Save an event with valid inputs to database
    def test_task_save_event(self):
        db_count = Task.objects.all().count() 
        person=Person.objects.get(pk=1)
        event=Event.objects.get(pk=1)
        task = Task(title='Create guest list', description='numbers tbc', complete=False, deadline="2024-11-10", event=event, person=person) 
        task.save()
        self.assertEqual(db_count+1, Task.objects.all().count())
        self.assertTrue(task.clean)

    ## Test - cannot save empty task title (event titles are required)
    def test_task_model_title_required(self):
        person=Person.objects.get(pk=1)
        event=Event.objects.get(pk=1)
        task = Task(description='numbers tbc', complete=False, deadline="2024-11-10", event=event, person=person) 
        self.assertRaises(ValidationError, task.full_clean)

    ## Test - cannot save empty event description (event descriptions are required)
    def test_task_model_description_required(self):
        person=Person.objects.get(pk=1)
        event=Event.objects.get(pk=1)
        task = Task(title='Create guest list', complete=False, deadline="2024-11-10", event=event, person=person) 
        self.assertRaises(ValidationError, task.full_clean)

    ## Test - cannot save empty event date (event dates are required)
    def test_task_model_deadline_required(self):
        person=Person.objects.get(pk=1)
        event=Event.objects.get(pk=1)
        task = Task(title='Create guest list', description='numbers tbc', deadline="", complete=False, event=event, person=person) 
        self.assertRaises(ValidationError, task.full_clean)

    ## Test - cannot save deadline before todays date (event dates are to be set in the future)
    def test_task_model_deadline_less_than_today(self):
        person=Person.objects.get(pk=1)
        event=Event.objects.get(pk=1)
        task = Task(title='Create guest list', description='numbers tbc', complete=False, event=event, deadline="2021-11-26", person=person) 
        self.assertRaises(ValidationError, task.full_clean)

    ## Test - cannot save deadline after event date
    def test_task_model_deadline_greater_than_event_date(self):
        person=Person.objects.get(pk=1)
        event=Event.objects.get(pk=1)
        task = Task(title='Create guest list', description='numbers tbc', complete=False, event=event, deadline="2027-11-26", person=person) 
        self.assertRaises(ValidationError, task.full_clean)

    ## Test - cannot save empty event (event field is required)
    def test_task_model_event_required(self):
        person=Person.objects.get(pk=1)
        try:
            task = Task(title='Create guest list', description='numbers tbc', complete=False, deadline="2024-11-10", person=person) 
        except TypeError:
            pass
        self.assertRaises(TypeError, task.save())

    ## Test - can save empty event (person field is required)
    def test_task_model_person_required(self):
        event=Event.objects.get(pk=1)
        try:
            task = Task(title='Create guest list', description='numbers tbc', complete=False, deadline="2024-11-10", event=event) 
        except TypeError:
            pass
        self.assertRaises(TypeError, task.save())

    ## Test - can save empty complete field (complete field is false by default)
    def test_task_model_test_complete_field_not_required(self):
        person=Person.objects.get(pk=1)
        event=Event.objects.get(pk=1)
        task = Task(title='Create guest list', description='numbers tbc', event=event, deadline="2024-11-10", person=person) 
        self.assertTrue(task.full_clean)