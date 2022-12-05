from django.test import TestCase
from events.models import Event, Task, User 
from datetime import date, timedelta
from django.urls import reverse
from events.forms import *

class ViewTests(TestCase):
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
        t1 = Task(title='This is the task title', description='This is the task description', complete=True, deadline="2024-11-10", event=e1, person=p1)
        t1.full_clean
        t1.save()
        t2 = Task(title='This is the second task title', description='This is the second task description', complete=False, deadline="2024-11-10", event=e1, person=p1)
        t2.full_clean
        t2.save()

        # RegisteredEvent object for testing
        re1 = RegisteredEvent(event=e1, member=user1)
        re1.full_clean
        re1.save()



#----------- VIEWS AND TEMPLATE TESTS -----------#

    #----------- EVENTS VIEW AND TEMPLATES -----------#

    ## Test- Load the past events index.html content in events index view
    def test_events_index_view_logged_in(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        # get event with past date from test data, Charlies 1st Birthday
        # get events with over a week away date from test data, Rugby Party
        # get event with date less than a week away from test data, Winterwonderland
        response = self.client.get(reverse('events_index'), follow=True)
        # Check template content
        self.assertContains(response, '<h5 class="card-title">Manage Your Events</h5>', status_code=200)
        self.assertContains(response, '<a onclick="location.href=\'/events/nextweek\';" href="#" class="btn btn-primary more-events-btn">More Events</a>', status_code=200)
        self.assertContains(response, '<a onclick="location.href=\'/events/past\';" href="#" class="btn btn-primary more-events-btn">More Events</a>', status_code=200)
        self.assertContains(response, '<a onclick="location.href=\'/events/future\';" href="#" class="btn btn-primary more-events-btn">More Events</a>', status_code=200)
        self.assertContains(response, '<div id="header">VISIT THE HOMEPAGE TO GRAB A SPOT AT ONE OF OUR EXCLUSIVE EVENTS</div>', status_code=200)
        # Check events have been loaded in the correct places on the page depending on their date
        # Past event - 'Charlies 1st Birthday'
        self.assertContains(response, '<h5 class="card-title">Past Events</h5>\n          <ul class="list-group list-group-flush">\n            \n            <li class="list-group-item">Charlies 1st Birthd', status_code=200)
        # Event < a week away - 'Winterwonderland'
        self.assertContains(response, '<h5 class="card-title">Events < Week Away</h5>\n          <ul class="list-group list-group-flush">\n            \n            <li class="list-group-item">Winterwonderland</li>', status_code=200)
        # Event > a week away - Rugby Party
        self.assertContains(response, '<h5 class="card-title">Events > Week Away</h5>\n          <ul class="list-group list-group-flush">\n            \n            <li class="list-group-item">Rugby Party</li>', status_code=200)
 
    ## Test events index view logged out redirects to login page
    def test_events_index_view_not_logged_in(self):
        response = self.client.get(reverse('events_index'), follow=True)
        self.assertEquals(response.status_code, 200)

    ## Test events create view logged in
    def test_events_create_view(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        response = self.client.get(reverse('events_new'), follow=True)
        # Check form template loaded correctly
        self.assertContains(response, '<form method="POST" enctype="multipart/form-data">', status_code=200)
        self.assertContains(response, '<input type="text" name="title" class="form-control" placeholder="Event Title" maxlength="128" required id="id_title">', status_code=200)
        self.assertContains(response, '<textarea name="description" cols="60" rows="25" class="form-control" placeholder="Event Description" required id="id_description">\n</textarea>', status_code=200)
        self.assertContains(response, '<input type="text" name="date" class="form-control" placeholder="yyyy-mm-dd" required id="id_date">', status_code=200)
        self.assertContains(response, '<input type="hidden" name="author" value="1" id="id_author">', status_code=200)
        self.assertContains(response, '<input type="submit" value="Submit">', status_code=200)
        self.assertContains(response, '<div id="header">VISIT THE HOMEPAGE TO GRAB A SPOT AT ONE OF OUR EXCLUSIVE EVENTS</div>', status_code=200)

    ## Test events create view logged out redirects to login page
    def test_events_create_view_not_logged_in(self):
        response = self.client.get(reverse('events_new'), follow=True)
        self.assertEquals(response.status_code, 200)

    ## Test events past view logged in
    def test_events_past_view_logged_in(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        response = self.client.get(reverse('past_events'), follow=True)
        # Check template content
        self.assertContains(response, '<div class="card text-center" style="margin-bottom: 40px">\n    <div class="card-header">\n      PAST EVENTS \n    </div>', status_code=200)
        # Check correct event has been loaded, ie. Charlies 1st birthday is an event in the past
        self.assertContains(response, '<h5 class="card-title"><a href="/events/3">\n                    Charlies 1st Birthday</a></h5>', status_code=200)

    ## Test events past view logged out redirects to login page
    def test_events_past_view_not_logged_in(self):
        response = self.client.get(reverse('past_events'), follow=True)
        self.assertEquals(response.status_code, 200)

    ## Test events past view does not show publish button
    def test_events_past_view_do_not_load_publish(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        response = self.client.get(reverse('past_events'), follow=True)
        # Check publish button has not been loaded
        self.assertNotContains(response, '<button id="publish-4" onClick=\'setPublish(4);\' class="btn btn-primary">Publish</button>', status_code=200)

    ## Test events this week view does show publish button
    def test_events_this_week_view_does_load_publish(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        response = self.client.get(reverse('thisweek_events'), follow=True)
        # Check publish button has been loaded
        self.assertContains(response, '<button id="publish-4" onClick=\'setPublish(4);\' class="btn btn-primary">Publish</button>', status_code=200)

    ## Test events this week view logged in
    def test_events_this_week_view_logged_in(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        response = self.client.get(reverse('thisweek_events'), follow=True)
        # Check template content
        self.assertContains(response, '<div class="card text-center" style="margin-bottom: 40px">\n    <div class="card-header">\n      EVENTS WITHIN A WEEK \n    </div>', status_code=200)
        # Check correct event has been loaded, ie. Winterwonderland is an event within a weeks time
        self.assertContains(response, '<h5 class="card-title"><a href="/events/4">\n                    Winterwonderland</a></h5>', status_code=200)

    ## Test events this week view logged out redirects to login page
    def test_events_this_week_view_not_logged_in(self):
        response = self.client.get(reverse('thisweek_events'), follow=True)
        self.assertEquals(response.status_code, 200)

    ## Test events over a week away view logged in
    def test_events_over_a_week_away_view_logged_in(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        response = self.client.get(reverse('future_events'), follow=True)
        # Check template content
        self.assertContains(response, '<div class="card text-center" style="margin-bottom: 40px">\n    <div class="card-header">\n      EVENTS IN OVER A WEEK \n    </div>', status_code=200)
        # Check correct event has been loaded, ie. Rugby Party is an event over a weeks away
        self.assertContains(response, '<h5 class="card-title"><a href="/events/1">\n                    Rugby Party</a>', status_code=200)

    ## Test events in over a week logged out redirects to login page
    def test_events_over_a_week_away_not_logged_in(self):
        response = self.client.get(reverse('future_events'), follow=True)
        self.assertEquals(response.status_code, 200)

    ## Test events in registered view logged in
    def test_registered_events_view_logged_in(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        user1 = User.objects.get(pk=1)
        author = User.objects.get(pk=2)
        e6 = Event.objects.create(title='Charity Fair', description="Location tbc", date = "2024-11-10", publish = True, author=author) 
        re = RegisteredEvent.objects.create(event=e6,member=user1)
        response = self.client.get(reverse('registered_events_index'), follow=True)
        # Check template content
        self.assertContains(response, '<h5 class="card-title">Your Registered Events </h5>', status_code=200)
        # Check correct event has been loaded, ie. Charity Event is an event registered in this test
        self.assertContains(response, '<h5 class="card-title">Charity Fair</a></h5>', status_code=200)

    ## Test events detail page when logged in
    def test_events_detail_view_logged_in(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        event = Event.objects.get(pk=1)
        response = self.client.get(reverse('events_detail', kwargs={'pk': event.pk}), follow=True)
        # Check template content
        self.assertContains(response, '<input type="button" onclick="location.href=\'/events/edit/1\';" value="Edit" />', status_code=200)
        self.assertContains(response, '<input type="button" onclick="location.href=\'/events/delete/1\';" value="Delete" />', status_code=200)
        self.assertContains(response, '<h3>Tasks</h3>\n<table id="taskTable"', status_code=200)
        # Check correct event has been loaded, ie. Rugby Party event with pk=1
        self.assertContains(response, '<h2>Rugby Party</h2><hr>\n<p> Location tbc</p>\n<hr>\n<p>Date: Nov. 21, 2024<p>', status_code=200)

    ## Test events detail view logged out redirects to login page
    def test_events_detail_view_not_logged_in(self):
        event = Event.objects.get(pk=1)
        response = self.client.get(reverse('events_detail', kwargs={'pk': event.pk}), follow=True)
        self.assertEquals(response.status_code, 200)

    ## Test events edit page when logged in
    def test_events_edit_view_logged_in(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        event = Event.objects.get(pk=1)
        response = self.client.get(reverse('events_update', kwargs={'nid': event.pk}), follow=True)
        # Check template content
        self.assertContains(response, '<form method="POST"', status_code=200)
        self.assertContains(response, '<input type="submit" value="Update">', status_code=200)
        # Check correct edit form has been loaded
        self.assertContains(response, '<input type="text" name="title" value="Rugby Party"', status_code=200)

    ## Test events detail view logged out redirects to login page
    def test_events_edit_view_not_logged_in(self):
        event = Event.objects.get(pk=1)
        response = self.client.get(reverse('events_update', kwargs={'nid': event.pk}), follow=True)
        self.assertEquals(response.status_code, 200)

    ## Test events delete view logged in, upon deletion, redirects user to events index page
    def test_events_delete_view_logged_in(self):
        db_count = Event.objects.count()
        login = self.client.login(username='annacarter', password='MyPassword123') 
        event = Event.objects.get(pk=1)
        response = self.client.get(reverse('events_delete', kwargs={'nid': event.pk}), follow=True)
        self.assertRedirects(response, reverse('events_index'))
        self.assertEquals(db_count-1, Event.objects.count())
        self.assertEqual(response.status_code, 200)

    ## Test events publish change to publish from false to true view logged in
    def test_events_publish_ajax_false_to_tue_and_validation_logged_in(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        author = User.objects.get(pk=2)
        # event publish set to false
        event = Event.objects.create(title='Charity Fair', description="Location tbc", date = "2024-11-10", publish = False, author=author) 
        data = {
            'event_id': event.pk
        }
        response = self.client.get(reverse('publish_ajax_event'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest', follow=True)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['publish'], True)
 
    ## Test events publish change to publish from true to false view logged in
    def test_events_publish_ajax_true_to_false_and_validation_logged_in(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        author = User.objects.get(pk=2)
        # event publish set to false
        event = Event.objects.create(title='Charity Fair', description="Location tbc", date = "2024-11-10", publish = True, author=author) 
        data = {
            'event_id': event.pk
        }
        response = self.client.get(reverse('publish_ajax_event'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest', follow=True)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['publish'], False)

    #----------- TASKS VIEW AND TEMPLATE -----------#

    ## Test - task list view logged in
    def test_task_list_view_logged_in(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        event = Event.objects.get(pk=1)
        response = self.client.get(reverse('task_list', kwargs={'nid': event.pk}), follow=True)
        # Check template content
        self.assertContains(response, '<table id="taskTable"', status_code=200)
        # Check correct edit form has been loaded, ie. Task of event with pk=1
        self.assertContains(response, '<td class="taskTitle taskData" name="title">This is the task title</td>', status_code=200)
        self.assertContains(response, '<button class="task_edit_button" onClick=\'editTask(2, );', status_code=200)

    ## Test - task form view create new task
    def test_task_create_new_logged_in(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        event = Event.objects.get(pk=1)
        response = self.client.get(reverse('create_task', kwargs={'nid': event.pk}), follow=True)
        self.assertContains(response, '<form method="POST"', status_code=200)
        self.assertContains(response, '<input type="checkbox" name="complete"', status_code=200)
        self.assertContains(response, '<input type="submit" value="Submit">', status_code=200)
        # Check correct edit form has been loaded, ie. Task of event with pk=1
        self.assertContains(response, '<input type="text" name="title" class="form-control" placeholder="Task Title"', status_code=200)
        self.assertContains(response, '<input type="text" name="deadline"', status_code=200)
        

    #----------- TASK AJAX TESTS FOR TASK DELETE/UNCOMPLETE/COMPLETE AND EDIT -----------#

    ## Test - task deleted object if user is logged in. Test view, check the delete_success json response is true
    def test_delete_task_logged_in(self):
        db_count = Task.objects.all().count()
        task = Task.objects.get(pk=1)
        login = self.client.login(username='annacarter', password='MyPassword123') 
        data = {
            "task_id": task.pk
        }
        response = self.client.get(reverse('delete_task'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest', follow=True)
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
        response = self.client.get(reverse('delete_task'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), db_count)

    # Test - task can be complete with ajax function when user is logged in.
    def test_complete_task_logged_in(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        task = Task.objects.get(pk=2)
        data = {
            "task_id": task.pk
        }
        response = self.client.get(reverse('complete_task'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest', follow=True)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['complete'], True)

    # Test - task cannot be complete with ajax function when user is not logged in.
    def test_complete_task_not_logged_in(self):
        task = Task.objects.get(pk=2)
        data = {
            "task_id": task.pk
        }
        response = self.client.get(reverse('complete_task'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest', follow=True)
        self.assertEqual(response.status_code, 200)

    # Test - task can be set to uncomplete with ajax function when user is logged in.
    def test_set_to_not_complete_task_logged_in(self):
        login = self.client.login(username='annacarter', 
        password='MyPassword123') 
        # The task.pk=1 attribute complete set up as true
        task = Task.objects.get(pk=1)
        data = {
            "task_id": task.pk
        }
        response = self.client.get(reverse('complete_task'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest', follow=True)
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
        response = self.client.get(reverse('complete_task'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest', follow=True)
        self.assertEqual(response.status_code, 200)

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
        response = self.client.post(reverse('task_ajax_update'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest', follow=True)
        new_task.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_task.title, "New_Title")