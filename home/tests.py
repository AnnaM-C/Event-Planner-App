from django.test import TestCase
from events.models import Event, User, RegisteredEvent
from django.urls import reverse
from datetime import date
from .forms import UserCreationWithEmailForm
import json

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


#----------- Login and Log out Views -----------#

## Test - Login user
    def test_login(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        self.assertTrue(login)

## Test - Log out user
    def test_logout(self):
        self.client.login(username='annacarter', password='MyPassword123') 
        log_out = self.client.logout
        # log_out = self.client.logout(username='annacarter', password='MyPassword123') 
        self.assertTrue(log_out)

# User is not logged in loads the <button id="register-button-no_login" element
# and does not load the <button id="register-button-login" element
    def test_no_login_home_events_view_page(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, '<button id="register-button-no_login"', status_code=200)
        self.assertNotContains(response, '<button id="register-button-login"', status_code=200)

    
# View test is false if user is not logged the view does not load the <button id="register-button-no_login" element
# and does load the <button id="register-button-login" element
    def test_login_home_events_view(self):
        login = self.client.login(username='annacarter', password='MyPassword123') 
        response = self.client.get(reverse('home'))
        self.assertNotContains(response, '<button id="register-button-no_login"', status_code=200)
        self.assertContains(response, '<button id="register-button-login"', status_code=200)


#----------- Testing sign up to use application -----------#
    
# Test sign up form with valid input
# Test form is valid
# Test no error messages are displayed on the page
# Test page redirects to the correct place
# Test user was successfully saved
    def test_register_view_valid_inputs(self):
        db_count = User.objects.all().count()
        data = {
            "username":"testuser2",
            "email": "test@gmail.com",
            "password1": "terminal123",
            "password2": "terminal123",
        }
        form = UserCreationWithEmailForm(data)
        form.save()
        self.assertTrue(form.is_valid())
        self.assertTrue(db_count+1, User.objects.all().count())

        response = self.client.post(reverse('signup_user'), data=data, follow=True)
        self.assertRedirects(response, '/accounts/login/')
        self.assertNotContains(response, '<ul class="errorlist"><li>The two password fields didn’t match.</li></ul>')
        self.assertNotContains(response, '<ul class="errorlist"><li>User with this Email address already exists.</li></ul>')
        self.assertNotContains(response, '<ul class="errorlist"><li>The password is too similar to the username.</li></ul>')
        self.assertNotContains(response, '<ul class="errorlist"><li>This password is too short. It must contain at least 8 characters.</li>')
        self.assertNotContains(response, '<ul class="errorlist"><li>This password is too common.</li></ul>')
        self.assertNotContains(response, '<ul class="errorlist"><li>This password is entirely numeric.</li></ul>')


# Test register form with invalid input (different passwords)
# Test form is invalid 
# Test user was not created
# Test correct error message was displayed in the view
    def test_register_view_valid_inputs(self):
        data = {
            "username":"testuser2",
            "email": "test@gmail.com",
            "password1": "terminal123",
            "password2": "terminal111",
        }
        form = UserCreationWithEmailForm(data)
        self.assertFalse(form.is_valid())
        self.assertFalse(User.objects.filter(username="testuser2").exists())
        response = self.client.post(reverse('signup_user'), data=data, follow=True)
        self.assertContains(response, '<ul class="errorlist"><li>The two password fields didn’t match.</li></ul>')

# Test register form with invalid input (duplicate username)
# # Test form is invalid 
# Test user was not created
# Test correct error message was displayed in the view
    def test_register_view_duplicate_usernames(self):
        data = {
            "username":"annacarter",
            "email": "ac@gmail.com",
            "password1": "terminal123",
            "password2": "terminal123",
        }
        form = UserCreationWithEmailForm(data)
        self.assertFalse(form.is_valid())
        self.assertFalse(User.objects.filter(username="testuser2").exists())
        response = self.client.post(reverse('signup_user'), data=data, follow=True)
        self.assertContains(response, '<ul class="errorlist"><li>A user with that username already exists.</li></ul>')

# Test register form with invalid input (duplicate email)
# Test form is invalid 
# Test user was not created
# Test correct error message was displayed in the view
    def test_register_view_duplicate_emails(self):
        data = {
            "username":"testuser2",
            "email": "testuser@surrey.ac.uk",
            "password1": "terminal123",
            "password2": "terminal123",
        }
        form = UserCreationWithEmailForm(data)
        self.assertFalse(form.is_valid())
        self.assertFalse(User.objects.filter(username="testuser2").exists())
        response = self.client.post(reverse('signup_user'), data=data, follow=True)
        self.assertContains(response, '<ul class="errorlist"><li>User with this Email address already exists.</li></ul>')

# Test register form with invalid input (password and username similar)
# Test form is invalid 
# Test user was not created
# Test correct error message was displayed in the view
    def test_register_similar_to_username_password(self):
        data = {
            "username":"testuser2",
            "email": "testuser2@surrey.ac.uk",
            "password1": "testuser2",
            "password2": "testuser2",
        }
        form = UserCreationWithEmailForm(data)
        self.assertFalse(form.is_valid())
        self.assertFalse(User.objects.filter(username="testuser2").exists())
        response = self.client.post(reverse('signup_user'), data=data, follow=True)
        self.assertContains(response, '<ul class="errorlist"><li>The password is too similar to the username.</li></ul>')

# Test register form with invalid input (short password)
# Test form is invalid 
# Test user was not created
# Test correct error message was displayed in the view
    def test_register_too_short_password(self):
        data = {
            "username":"sam1",
            "email": "sam1@surrey.ac.uk",
            "password1": "dog",
            "password2": "dog",
        }
        form = UserCreationWithEmailForm(data)
        self.assertFalse(User.objects.filter(username="testuser2").exists())
        self.assertFalse(form.is_valid())
        response = self.client.post(reverse('signup_user'), data=data, follow=True)
        self.assertContains(response, '<ul class="errorlist"><li>This password is too short. It must contain at least 8 characters.</li>')

# Test register form with invalid input (common password)
# Test form is invalid 
# Test user was not created
# Test correct error message was displayed in the view
    def test_register_common_password(self):
        data = {
            "username":"sam1",
            "email": "sam1@surrey.ac.uk",
            "password1": "password",
            "password2": "password",
        }
        form = UserCreationWithEmailForm(data)
        self.assertFalse(User.objects.filter(username="testuser2").exists())
        self.assertFalse(form.is_valid())
        response = self.client.post(reverse('signup_user'), data=data, follow=True)
        self.assertContains(response, '<ul class="errorlist"><li>This password is too common.</li></ul>')

# Test register form with invalid input (numeric password)
# Test form is invalid 
# Test user was not created
# Test correct error message was displayed in the view
    def test_register_numeric_password(self):
        data = {
            "username":"sam1",
            "email": "sam1@surrey.ac.uk",
            "password1": "123456",
            "password2": "123456",
        }
        form = UserCreationWithEmailForm(data)
        self.assertFalse(User.objects.filter(username="testuser2").exists())
        self.assertFalse(form.is_valid())
        response = self.client.post(reverse('signup_user'), data=data, follow=True)
        self.assertContains(response, '<li>This password is entirely numeric.</li>')



#----------- Testing register for an event -----------#

    def test_already_registered_alert_box(self):
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

    def test_not_registered_alert_box(self):
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


    ## View only published events on homepage
    def test_view_of_published_event(self):
        event1 = Event.objects.get(pk=1)
        data={
            'event':event1
        }
        response = self.client.get(reverse('home'),data=data)
        self.assertContains(response, event1.title, status_code=200)

    ## Unpublished events not viewable on homepage
    def test_view_of_unpublished_event(self):
            event1 = Event.objects.get(pk=3)
            data={
                'event':event1
            }
            response = self.client.get(reverse('home'),data=data)
            self.assertNotContains(response, event1.title, status_code=200)

