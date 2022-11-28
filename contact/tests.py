from django.test import TestCase
from django.urls import reverse

class HomePageTests(TestCase):

    """Test whether our notes application homepage"""

    def setUp(self):
        # Will be used to do any set up before test cases
        return

    def test_contact(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This is my header')
        self.assertContains(response, 'Contact Us Page')
        self.assertContains(response, 'This is my footer')