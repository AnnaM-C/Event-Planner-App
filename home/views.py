from django.shortcuts import render
from .forms import UserCreationWithEmailForm 
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from events.models import Event    
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import View 

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
    # user = User.objects.get(username=request.user.username)
    # context["user"] = user
    context["events_list"] = Event.objects.all()
    return render(request, 'home/home.html', context)

# class RegisterEvent(View):
#     def put(self, request):
        
#         obj = RegisterEvent.objects.filter(id = request.POST.get('taskId'))

#         obj.update(title = request.POST.get('taskTitle'),description = request.POST.get('taskDescription'))
#         # print(request.POST.get('eventId'))
#         return HttpResponseRedirect('' + request.POST.get('eventId'))

# class RegisterEvents(View):
#     def get(self, request):
#     # get the event and user from the request
#         event = Event.objects.filter(id=request.GET.get('event_id'))
#         print(event)
#         user = User.objects.filter(id=request.GET.get('user_id'))
#         print(user)
#         register = RegisteredEvent.objects.create(event=event, member=user)
#         print(register)
#         register.save()
#         return JsonResponse({'register_success': True}, status=200)