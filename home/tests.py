from django.test import TestCase
from events.models import Event, Task, User, RegisteredEvent
from django.urls import reverse
from datetime import date
import json

# Create your tests here.
class HomeTests(TestCase):
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

        e1 = Event(title='Rugby Party', description="Location tbc", date = date.today(), publish = True, author=user2) 
        e1.save()
        e2 = Event(title='Alfies 1st Birthday', description="Location tbc", author=user1) 
        e2.save()
        e3 = Event(title='Park Run Charity Event', description="Location: Bushy Park", date = date.today(), publish = False, author=user2) 
        e3.save()

        register1 = RegisteredEvent.objects.create(event=e1, member=user1)
        register1.save()

    # View test if user is not logged loads the <button id="register-button-no_login" element
    # and does not load the <button id="register-button-login" element
    def test_no_login_home_view_page(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, '<button id="register-button-no_login"', status_code=200)
        self.assertNotContains(response, '<button id="register-button-login"', status_code=200)

    # View test is false if user is not logged the view does not load the <button id="register-button-no_login" element
    # and does load the <button id="register-button-login" element
    def test_login_home_view(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        response = self.client.get(reverse('home'))
        self.assertNotContains(response, '<button id="register-button-no_login"', status_code=200)
        self.assertContains(response, '<button id="register-button-login"', status_code=200)

    def test_already_registered_alert(self):
        login = self.client.login(username='annacarter', password='MyPassword123')
        user1=User.objects.get(pk=1)
        event1=Event.objects.get(pk=1)
        db_count = RegisteredEvent.objects.all().count()
        data={
            "event_id": event1.pk,
            "user_id": user1.pk
        }
        response = self.client.get(reverse('register_event'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')      
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['register_success'], False)
        self.assertEqual(db_count, RegisteredEvent.objects.count())

    def test_not_registered_alert(self):
        login = self.client.login(username='annacarter', password='MyPassword123')
        db_count = RegisteredEvent.objects.all().count()
        user1=User.objects.get(pk=1)
        event2=Event.objects.get(pk=2)
        data={
            "event_id": event2.pk,
            "user_id": user1.pk
        }
        response = self.client.get(reverse('register_event'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['register_success'], True)
        self.assertEqual(db_count+1, RegisteredEvent.objects.count())


    ## Test for viewing only published events on homepage
    # def test_view_of_published_event(self):
    #     event1 = Event.objects.get(pk=1)
    #     data={
    #         'event':event1
    #     }
    #     response = self.client.get(reverse('home'),data=data)
    #     print(response)

