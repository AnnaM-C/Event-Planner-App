from .forms import UserCreationWithEmailForm 
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from events.models import Event, RegisteredEvent
from django.http import JsonResponse
from django.views.generic import View 
from django.shortcuts import (get_object_or_404, render)
from django.utils import timezone

# Create your views here.

# home view
def home(request):
    context = {}
    return render(request, 'home/home.html', context)

# sing up view
class RegisterUser(CreateView):
    model = User
    form_class = UserCreationWithEmailForm 
    template_name = 'home/register.html'
    success_url = reverse_lazy('login')

# show events view
def show_all_events(request):
    context = {}
    context["events_list"] = Event.objects.filter(date__gt = timezone.now())
    return render(request, 'home/home.html', context)

# user register to events
class RegisterEvents(View):
    def get(self, request):
    # get the event and user from the request
        e_id = request.GET.get('event_id')
        u_id = request.GET.get('user_id')
        # Flag used to check if user is already registered to an event
        flag = False
        for item in RegisteredEvent.objects.all():
            # Get the event and user for each RegisterdEvent object
            event = getattr(item,'event')
            user = getattr(item,'member')
            # Get the primary key attributes of event and user for each event and user object in the RegisteredEvent
            # query set of objects to check if the user wanting to register for that event has already 
            # registerd
            db_e_id = getattr(event, 'pk')
            db_u_id = getattr(user, 'pk')
            # if statement to check if the user wanting to register for that event has already 
            # registerd
            if(e_id == str(db_e_id) and u_id == str(db_u_id)):
                flag = True

        if(flag==True):
            return JsonResponse({'register_success': False}, status=200)
        else:
            event = get_object_or_404(Event, pk=e_id)
            user = get_object_or_404(User, pk=u_id)
            register = RegisteredEvent.objects.create(event=event, member=user)
            register.save()
            return JsonResponse({'register_success': True}, status=200)