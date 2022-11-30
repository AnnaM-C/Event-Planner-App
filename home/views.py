from django.shortcuts import render
from .forms import UserCreationWithEmailForm 
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from events.models import Event    

# Create your views here.

def home(request):
    context = {}
    return render(request, 'home/home.html', context)


class RegisterUser(CreateView):
    model = User
    form_class = UserCreationWithEmailForm 
    template_name = 'home/register.html'
    success_url = reverse_lazy('login')

def show_all_events(request):
    context = {}
    context["events_list"] = Event.objects.all()
    return render(request, 'home/home.html', context)