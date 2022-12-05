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


#----------- EVENT TESTS FOR FORMS, VIEWS, MODELS AND AUTHENTICATION -----------#

#----------- EVENTS PROTECTED URLS -----------#

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
        response = self.client.post(reverse('events_new'), data=data) 
        self.assertEqual(Event.objects.count(), db_count)
        self.assertEqual(response.status_code, 302)

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
        response = self.client.post(reverse('events_new'), data=data) 
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Event.objects.count(), db_count+1)

#----------- EVENTS MODELS -----------#

## Test - Save an event with valid inputs to database
    def test_event_save_event(self):
        db_count = Event.objects.all().count() 
        user1=User.objects.get(pk=1)
        event = Event(title='Christmas Brunch', description='At the ned', date='2024-11-26', publish=False, author=user1) 
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

#----------- TEST EVENT FORM AND CORRECT MESSAGE VIEW -----------#

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

#----------- DELETE EVENT TESTS -----------#

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


#----------- EVENT VIEWS -----------#

## Test- Load the past events index.html content in events index view
    def test_events_index_view_logged_in(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        # get event with past date from test data, Charlies 1st Birthday
        # get events with over a week away date from test data, Rugby Party
        # get event with date less than a week away from test data, Winterwonderland
        response = self.client.get(reverse('events_index'))
        # Check template content
        self.assertContains(response, '<h5 class="card-title">Manage Your Events</h5>', status_code=200)
        self.assertContains(response, '<a onclick="location.href=\'/events/nextweek\';" href="#" class="btn btn-primary more-events-btn">More Events</a>', status_code=200)
        self.assertContains(response, '<a onclick="location.href=\'/events/past\';" href="#" class="btn btn-primary more-events-btn">More Events</a>', status_code=200)
        self.assertContains(response, '<a onclick="location.href=\'/events/future\';" href="#" class="btn btn-primary more-events-btn">More Events</a>', status_code=200)
        self.assertContains(response, '<div id="header">REGISTER NOW TO GET A SPOT AT ONE OF OUR EXCLUSIVE EVENTS</div>', status_code=200)
        # Check events have been loaded in the correct places on the page depending on their date
        # Past event - 'Charlies 1st Birthday'
        self.assertContains(response, '<h5 class="card-title">Past Events</h5>\n          <ul class="list-group list-group-flush">\n            \n            <li class="list-group-item">Charlies 1st Birthd', status_code=200)
        # Event < a week away - 'Winterwonderland'
        self.assertContains(response, '<h5 class="card-title">Events < Week Away</h5>\n          <ul class="list-group list-group-flush">\n            \n            <li class="list-group-item">Winterwonderland</li>', status_code=200)
        # Event > a week away - Rugby Party
        self.assertContains(response, '<h5 class="card-title">Events > Week Away</h5>\n          <ul class="list-group list-group-flush">\n            \n            <li class="list-group-item">Rugby Party</li>', status_code=200)
 
# Test events index view logged out redirects to login page
    def test_events_index_view_not_logged_in(self):
        response = self.client.get(reverse('events_index'))
        self.assertEquals(response.status_code, 302)

# Test events create view logged in
    def test_events_create_view(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        response = self.client.get(reverse('events_new'))
        # Check form template loaded correctly
        self.assertContains(response, '<form method="POST" enctype="multipart/form-data">', status_code=200)
        self.assertContains(response, '<input type="text" name="title" class="form-control" placeholder="Event Title" maxlength="128" required id="id_title">', status_code=200)
        self.assertContains(response, '<textarea name="description" cols="60" rows="25" class="form-control" placeholder="Event Description" required id="id_description">\n</textarea>', status_code=200)
        self.assertContains(response, '<input type="text" name="date" value="2022-12-05" required id="id_date">', status_code=200)
        self.assertContains(response, '<input type="hidden" name="initial-date" value="2022-12-05" id="initial-id_date">', status_code=200)
        self.assertContains(response, '<input type="hidden" name="author" value="1" id="id_author">', status_code=200)
        self.assertContains(response, '<input type="submit" value="Submit">', status_code=200)
        self.assertContains(response, '<div id="header">REGISTER NOW TO GET A SPOT AT ONE OF OUR EXCLUSIVE EVENTS</div>', status_code=200)

# Test events create view logged out redirects to login page
    def test_events_create_view_not_logged_in(self):
        response = self.client.get(reverse('events_new'))
        self.assertEquals(response.status_code, 302)

# Test events past view logged in
    def test_events_past_view_logged_in(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        response = self.client.get(reverse('past_events'))
        # Check template content
        self.assertContains(response, '<div class="card text-center" style="margin-bottom: 40px">\n    <div class="card-header">\n      PAST EVENTS \n    </div>', status_code=200)
        # Check correct event has been loaded, ie. Charlies 1st birthday is an event in the past
        self.assertContains(response, '<h5 class="card-title"><a href="/events/3">\n                    Charlies 1st Birthday</a></h5>', status_code=200)

# Test events past view logged out redirects to login page
    def test_events_past_view_not_logged_in(self):
        response = self.client.get(reverse('past_events'))
        self.assertEquals(response.status_code, 302)

# Test events this week view logged in
    def test_events_this_week_view_logged_in(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        response = self.client.get(reverse('thisweek_events'))
        # Check template content
        self.assertContains(response, '<div class="card text-center" style="margin-bottom: 40px">\n    <div class="card-header">\n      EVENTS WITHIN A WEEK \n    </div>', status_code=200)
        # Check correct event has been loaded, ie. Winterwonderland is an event within a weeks time
        self.assertContains(response, '<h5 class="card-title"><a href="/events/4">\n                    Winterwonderland</a></h5>', status_code=200)

# Test events this week view logged out redirects to login page
    def test_events_this_week_view_not_logged_in(self):
        response = self.client.get(reverse('thisweek_events'))
        self.assertEquals(response.status_code, 302)

# Test events over a week away view logged in
    def test_events_over_a_week_away_view_logged_in(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        response = self.client.get(reverse('future_events'))
        # Check template content
        self.assertContains(response, '<div class="card text-center" style="margin-bottom: 40px">\n    <div class="card-header">\n      EVENTS IN OVER A WEEK \n    </div>', status_code=200)
        # Check correct event has been loaded, ie. Rugby Party is an event over a weeks away
        self.assertContains(response, '<h5 class="card-title"><a href="/events/1">\n                    Rugby Party</a>', status_code=200)

# Test events this week view logged out redirects to login page
    def test_events_over_a_week_away_not_logged_in(self):
        response = self.client.get(reverse('future_events'))
        self.assertEquals(response.status_code, 302)

# Test events detail page when logged in
    def test_events_detail_view_logged_in(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        event = Event.objects.get(pk=1)
        response = self.client.get(reverse('events_detail', kwargs={'pk': event.pk}))
        # Check template content
        self.assertContains(response, '<input type="button" onclick="location.href=\'/events/edit/1\';" value="Edit" />', status_code=200)
        self.assertContains(response, '<input type="button" onclick="location.href=\'/events/delete/1\';" value="Delete" />', status_code=200)
        self.assertContains(response, '<h3>Tasks</h3>\n<table id="taskTable"', status_code=200)
        # Check correct event has been loaded, ie. Rugby Party event with pk=1
        self.assertContains(response, '<h2>Rugby Party</h2><hr>\n<p> Location tbc</p>\n<hr>\n<p>Date: Nov. 21, 2024<p>', status_code=200)

# Test events detail view logged out redirects to login page
    def test_events_detail_view_not_logged_in(self):
        event = Event.objects.get(pk=1)
        response = self.client.get(reverse('events_detail', kwargs={'pk': event.pk}))
        self.assertEquals(response.status_code, 302)

# Test events edit page when logged in
    def test_events_edit_view_logged_in(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        event = Event.objects.get(pk=1)
        response = self.client.get(reverse('events_update', kwargs={'nid': event.pk}))
        # Check template content
        self.assertContains(response, '<form method="POST"', status_code=200)
        self.assertContains(response, '<input type="submit" value="Update">', status_code=200)
        # Check correct edit form has been loaded, ie. Rugby Party event with pk=1
        self.assertContains(response, '<input type="text" name="title" value="Rugby Party"', status_code=200)

# Test events detail view logged out redirects to login page
    def test_events_edit_view_not_logged_in(self):
        event = Event.objects.get(pk=1)
        response = self.client.get(reverse('events_update', kwargs={'nid': event.pk}))
        self.assertEquals(response.status_code, 302)

# Test events delete view logged in, upon deletion, redirects user to events index page
    def test_events_delete_view_logged_in(self):
        db_count = Event.objects.count()
        login = self.client.login(username='annacarter', password='MyPassword123') 
        event = Event.objects.get(pk=1)
        response = self.client.get(reverse('events_delete', kwargs={'nid': event.pk}))
        self.assertRedirects(response, reverse('events_index'))
        self.assertEquals(db_count-1, Event.objects.count())

# # Test events delete view logged out redirects to login page
    def test_events_edit_view_not_logged_in(self):
        db_count = Event.objects.count()
        event = Event.objects.get(pk=1)
        response = self.client.get(reverse('events_delete', kwargs={'nid': event.pk}))
        self.assertEquals(response.status_code, 302)
        self.assertEquals(db_count, Event.objects.count())


#----------- PERSON TESTS -----------#

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


#----------- TASK TESTS FOR FORMS, VIEWS, MODELS AND AUTHENTICATION -----------#

#----------- TASK AUTHENTICATION -----------#

## Test - non-empty title, description, deadline and logged in user successfully save task to event
    def test_post_create_task(self): 
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
        response = self.client.post(reverse('create_task', kwargs={'nid': event.pk}), data=data)
        self.assertEqual(Task.objects.count(), db_count+1)
        self.assertEqual(response.status_code, 302)

## Test - non-empty title, description, deadline and logged in user successfully save task to event
    def test_post_create_task(self): 
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
        response = self.client.post(reverse('create_task', kwargs={'nid': event.pk}), data=data)
        self.assertEqual(Task.objects.count(), db_count)
        self.assertEqual(response.status_code, 302)

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


#----------- TASK FORM -----------#

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


#----------- TASK AJAX TESTS FOR TASK DELETE/UNCOMPLETE/COMPLETE AND EDIT -----------#

## Test - task deleted object if user is logged in. Test view, check the delete_success json response is true
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
        login = self.client.login(username='annacarter', password='MyPassword123') 
        task = Task.objects.get(pk=2)
        data = {
            "task_id": task.pk
        }
        response = self.client.get(reverse('complete_task'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['complete'], True)

# Test - task cannot be complete with ajax function when user is not logged in.
    def test_complete_task_not_logged_in(self):
        task = Task.objects.get(pk=2)
        data = {
            "task_id": task.pk
        }
        response = self.client.get(reverse('complete_task'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 302)


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

# Test - task cannot be set to uncomplete with ajax function when user is not logged in.
    def test_set_to_not_complete_task_not_logged_in(self):
        # The task.pk=1 attribute complete set up as true
        task = Task.objects.get(pk=1)
        data = {
            "task_id": task.pk
        }
        response = self.client.get(reverse('complete_task'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 302)

# Test - task can be edited with ajax function when user is logged in.
    def test_edit_task_logged_in(self):
        login = self.client.login(username='annacarter', 
        password='MyPassword123') 
        event=Event.objects.get(pk=1)
        person=Person.objects.get(pk=1)
        # The task.pk=1 attribute complete is true
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


