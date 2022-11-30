# from django.test import TestCase
# from .models import Event, Task, User 

# class NoteTests(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         user1 = User(username='annacarter', email='anna@surrey.ac.uk') 
#         user1.set_password('MyPassword123')
#         user1.save()
#         user2 = User(username='testadminuser', email='testadminuser@surrey.ac.uk') 
#         user2.set_password('MyPassword123')
#         user2.save()
#         user3 = User(username='testuser', email='testuser@surrey.ac.uk') 
#         user2.set_password('MyPassword123')
#         user3.save()

#         n1 = Event(title='1st Note', description="This is my 1st note", author=user1) 
#         n1.save()
#         n2 = Event(title='2nd Note', description="This is my 2nd note", author=user1) 
#         n2.save()

# ## Add users to events
#     def test_login(self):
#         login = self.client.login(username='user1', password='MyPassword123') 
#         self.assertTrue(login)


#     def test_save_note(self):
#         db_count = Event.objects.all().count() 
#         user1=User.objects.get(pk=1)

#         note = Event(title='new Event', description='New description', author=user1) 
#         note.save()
#         self.assertEqual(db_count+1, Event.objects.all().count())

#     def test_duplicate_title(self):
#         db_count = Event.objects.all().count()
#         user1=User.objects.get(pk=1)
#         event = Event(title='1st Event', description="This is my 1st Event", author=user1) 
#         #with self.assertRaises(IntegrityError):
#         try:
#             with transaction.atomic(): 
#                 event.save()
#         except IntegrityError: 
#             pass
#         self.assertNotEqual(db_count+1, Event.objects.all().count())

# ## Test protected URL's
#     def test_post_create_event_no_login(self): 
#         db_count = Event.objects.all().count() 
#         user1=User.objects.get(pk=1)
#         data={
#             "title": "new Event", 
#             "description": " new description", 
#             "author": user1
#         }
#         response = self.client.post(reverse('events_new'), data=data) 
#         self.assertEqual(Event.objects.count(), db_count)

#     def test_post_create_event_with_login(self):
#         db_count = Event.objects.all().count()
#         user1=User.objects.get(pk=1)
#         login = self.client.login(username='user1', password='MyPassword123') 
#         data={
#             "title": "new event", 
#             "description": " new description", 
#             "author": user1.id
#         }
#         response = self.client.post(reverse('notes_new'), data=data) 
#         self.assertEqual(Event.objects.count(), db_count+1)