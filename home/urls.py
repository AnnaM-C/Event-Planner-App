from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_all_events, name='home'),
    path('signup', views.RegisterUser.as_view(), name='signup_user'),
]