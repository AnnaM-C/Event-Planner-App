from django.shortcuts import render
from .models import *
from django.contrib import messages
from django.views.generic import ListView, CreateView, DetailView
from django.shortcuts import (get_object_or_404, render, redirect)
from .forms import EventForm, TaskForm
from django.urls import reverse_lazy
from django.views.generic import View 
from django.http import JsonResponse, HttpResponseRedirect
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils import timezone


def is_admin(user):
    return user.groups.filter(name='EventsAdminUsers').exists()

#----------- EVENTS VIEW -----------#

# view events index view which contains 3 sections, past events, event < a week and > a week
@login_required
def events_index_view(request):
    context = {}
    if is_admin(request.user): 
        context["events_past"] = Event.objects.filter(date__lt = timezone.now())
        context["events_week"] = Event.objects.filter(date__range = [timezone.now(), timezone.now()+timedelta(days=7)])
        context["events_future"] = Event.objects.filter(date__gt = timezone.now()+timedelta(days=7))
    else:
        context["events_past"] = Event.objects.filter(author=request.user, date__lt = timezone.now())
        context["events_week"] = Event.objects.filter(author=request.user, date__range = [timezone.now(), timezone.now()+timedelta(days=7)])
        context["events_future"] = Event.objects.filter(author=request.user, date__gt = timezone.now()+timedelta(days=7))
    return render(request, 'events/index.html', context)

#  view past events
@login_required
def index_past_events(request):
    context = {}
    if is_admin(request.user): 
        context["events_list"] = Event.objects.filter(date__lt = timezone.now())
    else:
        context["events_list"] = Event.objects.filter(date__lt = timezone.now(), author=request.user)
        context["title"] = "PAST EVENTS"
    return render(request, 'events/events_view.html', context)

#  view events next week
@login_required
def index_nextweek_events(request):
    context = {}
    if is_admin(request.user): 
        context["events_list"] = Event.objects.filter(date__range = [timezone.now(), timezone.now()+timedelta(days=7)])
        context['today'] = timezone.now()
    else:
        context["events_list"] = Event.objects.filter(date__range = [timezone.now(), timezone.now()+timedelta(days=7)], author=request.user)
        context['today'] = timezone.now()
    context["title"] = "EVENTS WITHIN A WEEK"
    return render(request, 'events/events_view.html', context)

#  view events > a week from today
@login_required
def index_future_events(request):
    context = {}
    if is_admin(request.user): 
        context["events_list"] = Event.objects.filter(date__gt = timezone.now()+timedelta(days=7))
        context['today'] = timezone.now()
    else:
        context["events_list"] = Event.objects.filter(date__gt = timezone.now()+timedelta(days=7), author=request.user)
        context['today'] = timezone.now()
    context["title"] = "EVENTS IN OVER A WEEK"
    return render(request, 'events/events_view.html', context)

# event detail view
class EventDetailView(LoginRequiredMixin, DetailView): 
    model = Event
    template_name = 'events/detail_view.html'
    def get_context_data(self, **kwargs):
        event = Event.objects.get(id=self.kwargs['pk'])
        context = {}
        if(self.request.user == event.author or is_admin(self.request.user)):
            context['event'] = Event.objects.get(id=self.kwargs['pk']) 
            context['task_list'] = Task.objects.filter(event__id=self.kwargs['pk'])
        else:
            raise PermissionDenied()
        return context

# create event
@login_required
def events_create_view(request):
    context = {}
    form = EventForm(request.POST or None, initial={'author':request.user})
    if(request.method == 'POST'):
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Event Created')
            return redirect('events_index')
        else:
            messages.add_message(request, messages.ERROR, 'Invalid Form Data; Event not created')
        
    context['form']= form
    return render(request, "events/create_view.html", context)

# update event
@login_required
def events_update_view(request, nid):
    context ={}
    # fetch the object related to passed id
    obj = get_object_or_404(Event, id = nid)
    if(obj.author != request.user and not(is_admin(request.user))):
        raise PermissionDenied()
    # pass the object as instance in form
    form = EventForm(request.POST or None, instance = obj)
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, 'Event Updated')
        return redirect('events_detail', nid)
    # add form dictionary to context
    context["form"] = form
    return render(request, "events/update_view.html", context)

# delete the event
@login_required
def events_delete_view(request, nid):
    # fetch the object related to passed id
    obj = get_object_or_404(Event, id = nid)
    if(obj.author != request.user and not(is_admin(request.user))):
        raise PermissionDenied()
    # delete object
    obj.delete()
    messages.add_message(request, messages.SUCCESS, 'Event Deleted') # after deleting redirect to index view
    return redirect('events_index')

# publish the event
class PublishEvent(LoginRequiredMixin, View):
 def get(self, request):
  eid = request.GET.get('event_id')
  event = get_object_or_404(Event, pk=eid)
  event.publish = not(event.publish)
  event.save()

  return JsonResponse({'publish': event.publish, 'eid': eid}, status=200)

#-----------SIGNED UP EVENTS VIEW-----------#

# events user has registered to
@login_required
def index_registered_events(request):
    context = {}
    # User
    user1 = request.user
    # Store the events the user is registered on in a list to pass into the rendering template   
    list = []
    for item in RegisteredEvent.objects.all():
        # Get the event and user for each RegisterdEvent object
        event = getattr(item,'event')
        user = getattr(item,'member')
        # Get the primary key attributes of event and user for each event and user object in the RegisteredEvent
        # set of objects to check if the user is registered for that event
        db_u_id = getattr(user, 'id')
        if(str(db_u_id) == str(user1.id)):
            list.append(event)
    
    context["registered_events"] = list

    return render(request, "events/registered_events.html", context)


#-----------TASK VIEWS-----------#

# view task list
class TaskListView(LoginRequiredMixin, ListView):
 model = Task
 template_name = 'events/task_list.html'
 context_object_name = 'task_list'

 def get_queryset(self):
  return Task.objects.filter(event__id=self.kwargs['nid'])

# create a task
class CreateTaskView(LoginRequiredMixin, CreateView):
 model = Task
 form_class = TaskForm
 template_name = "events/create_view.html"
 def get_initial(self): 
  # set the initial value of our event field
  event = Event.objects.get(id=self.kwargs['nid'])
  return {'event': event}
 def get_success_url(self): 
  # redirect to the event detail view on success
  return reverse_lazy('events_detail', kwargs={'pk':self.kwargs['nid']})

# complete a task
class CompleteTaskView(LoginRequiredMixin, View):
 def get(self, request):
  tid = request.GET.get('task_id')
  task = get_object_or_404(Task, pk=tid)
  task.complete = not(task.complete)
  task.save()
  return JsonResponse({'complete': task.complete, 'tid': tid}, status=200)

# delete a task
class DeleteTaskView(LoginRequiredMixin, View):
 def get(self, request):
  tid = request.GET.get('task_id')
  try:
   task = Task.objects.get(pk=tid)
  except Task.DoesNotExist:
   return JsonResponse({'delete_success': False, 'tid': tid}, status=200)
  task.delete()
  return JsonResponse({'delete_success': True, 'tid': tid}, status=200)

# edit a task
class EditTaskView(LoginRequiredMixin, View):
     def post(self, request):
        obj = Task.objects.filter(id = request.POST.get('taskId'))
        obj.update(title = request.POST.get('taskTitle'),description = request.POST.get('taskDescription'))
        return HttpResponseRedirect('' + request.POST.get('eventId'))



