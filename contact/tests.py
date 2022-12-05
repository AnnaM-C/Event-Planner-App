from django.test import TestCase
from django.urls import reverse
from .forms import ContactForm
from django.core import mail


class ContactTests(TestCase):
    def setUp(self):
        return

#----------- VIEW and FORM TESTS -----------#

    # Test contact us view template
    def test_contact(self):
        response = self.client.get(reverse('contact'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form method="post">')
        self.assertContains(response, '<label for="id_name">Name:</label>')
        self.assertContains(response, '<input type="text" name="subject" class="form-control" required id="id_subject">')
        self.assertContains(response, '<label for="id_message">Message:</label>')
        self.assertContains(response, '<input type="text" name="email" class="form-control" required id="id_email">')

    # Test email sending
    def test_send_email(self):
        mail.send_mail('This is the subject', 'This is the message body.',
            'from@example.com', ['to@example.com'],
            fail_silently=False)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'This is the subject')

    # Test valid form posted
    def test_post_form_view(self):
        data = {
            "name": "Anna",
            "email": "ac@gmail.com",
            "subject": "I like your web application!",
            "message": "Please make more", 
        }
        form = ContactForm(data) 
        self.assertTrue(form.is_valid())
        response = self.client.post(reverse('contact'), data=data, follow=True)
        self.assertContains(response, '<div class="card-header">\n      BROWSE EVENTS', status_code=200)
        self.assertRedirects(response, reverse('home'))
        self.assertContains(response, '<p\nclass="success"\n>\nMessage Sent\n</p>', status_code=200)
        self.assertEqual(response.status_code, 200)


    # Test empty name
    def test_post_empty_name_invalid_form(self): 
        data = {
            "name": "",
            "email": "ac@gmail.com",
            "subject": "I like your web application!",
            "message": "Please make more", 
        }
        form = ContactForm(data) 
        response = self.client.post(reverse('contact'), data=data, follow=True)
        self.assertFalse(form.is_valid())
        self.assertEqual(response.status_code, 200)

    # Test invaild form empty email
    def test_post_empty_email_invalid_form(self): 
        data = {
            "name": "Anna",
            "email": "",
            "subject": "I like your web application!",
            "message": "Please make more", 
        }
        form = ContactForm(data)
        response = self.client.post(reverse('contact'), data=data, follow=True)
        self.assertFalse(form.is_valid())
        self.assertEqual(response.status_code, 200)

    # Test invaild form empty subject
    def test_post_empty_subject_invalid_form(self): 
        data = {
            "name": "Anna",
            "email": "ac@gmail.com",
            "subject": "",
            "message": "Please make more", 
        }
        form = ContactForm(data)
        response = self.client.post(reverse('contact'), data=data, follow=True)
        self.assertFalse(form.is_valid())
        self.assertEqual(response.status_code, 200)

    # Test invaild form empty message
    def test_post_empty_message_invalid_form(self): 
        data = {
            "name": "Anna",
            "email": "ac@gmail.com",
            "subject": "I like your web application!",
            "message": "", 
        }
        form = ContactForm(data)
        response = self.client.post(reverse('contact'), data=data, follow=True)
        self.assertFalse(form.is_valid())
        self.assertEqual(response.status_code, 200)


