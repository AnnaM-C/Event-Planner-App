from django.test import TestCase
from django.urls import reverse
from .forms import ContactForm

class HomePageTests(TestCase):

    """Test whether our notes application homepage"""

    def setUp(self):
        # Will be used to do any set up before test cases
        return

    def test_contact(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)


    def test_post_valid_form(self): 
        data = {
            "name": "Anna",
            "email": "ac@gmail.com",
            "subject": "I like you're web application!",
            "message": "Please make more", 
        }
        form = ContactForm(data) 
        self.assertTrue(form.is_valid())

##  Test - Empty name, title, email and subject fields will throw errors
    def test_post_empty_name_invalid_form(self): 
        data = {
            "name": "",
            "email": "ac@gmail.com",
            "subject": "I like you're web application!",
            "message": "Please make more", 
        }
        form = ContactForm(data) 
        self.assertFalse(form.is_valid())

    def test_post_empty_email_invalid_form(self): 
        data = {
            "name": "Anna",
            "email": "",
            "subject": "I like you're web application!",
            "message": "Please make more", 
        }
        form = ContactForm(data) 
        self.assertFalse(form.is_valid())

    def test_post_empty_subject_invalid_form(self): 
        data = {
            "name": "Anna",
            "email": "ac@gmail.com",
            "subject": "",
            "message": "Please make more", 
        }
        form = ContactForm(data) 
        self.assertFalse(form.is_valid())

    def test_post_empty_message_invalid_form(self): 
        data = {
            "name": "Anna",
            "email": "ac@gmail.com",
            "subject": "I like you're web application!",
            "message": "", 
        }
        form = ContactForm(data) 
        self.assertFalse(form.is_valid())