from django.shortcuts import render
from .models import *
from django.contrib import messages
from django.views.generic import ListView, CreateView, DetailView
from django.shortcuts import (get_object_or_404, render, redirect)
from .forms import EventForm, TaskForm
from django.urls import reverse_lazy
from django.views.generic import View 
from django.http import JsonResponse
from datetime import datetime, timedelta

# Events Views
def events_index_view(request):
    context = {}
    context["events_list"] = Event.objects.all()
    context["events_past"] = Event.objects.filter(date__lt = datetime.today())
    context["events_week"] = Event.objects.filter(date__range = [datetime.today(), datetime.today()+timedelta(days=7)])
    context["events_future"] = Event.objects.filter(date__gt = datetime.today()+timedelta(days=7))
    return render(request, 'events/index.html', context)

def index_past_events(request):
    context = {}
    context["events_list"] = Event.objects.filter(date__lt = datetime.today())
    return render(request, 'events/events_view.html', context)

def index_nextweek_events(request):
    context = {}
    context["events_list"] = Event.objects.filter(date__range = [datetime.today(), datetime.today()+timedelta(days=7)])
    context['today'] = datetime.today()
    return render(request, 'events/events_view.html', context)

def index_future_events(request):
    context = {}
    context["events_list"] = Event.objects.filter(date__gt = datetime.today()+timedelta(days=7))
    context['today'] = datetime.today()
    return render(request, 'events/events_view.html', context)

# view
class EventDetailView(DetailView): 
    model = Event
    template_name = 'events/detail_view.html'
    def get_context_data(self, **kwargs):
        context = {}
        context['event'] = Event.objects.get(id=self.kwargs['pk']) 
        context['task_list'] = Task.objects.filter(event__id=self.kwargs['pk'])
        return context

# create
def events_create_view(request):
    context = {}
    form = EventForm(request.POST or None)
    if(request.method == 'POST'):
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Event Created')
            return redirect('events_index')
        else:
            messages.add_message(request, messages.ERROR, 'Invalid Form Data; Event not created')
        
    context['form']= form
    return render(request, "events/create_view.html", context)

# update
def events_update_view(request, nid):
    context ={}
    # fetch the object related to passed id
    obj = get_object_or_404(Event, id = nid)
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

# delete
def events_delete_view(request, nid):
    # fetch the object related to passed id
    obj = get_object_or_404(Event, id = nid)
    # delete object
    obj.delete()
    messages.add_message(request, messages.SUCCESS, 'Event Deleted') # after deleting redirect to index view
    return redirect('events_index')

# Task Views

# def task_detail_view(request):
#     people = {}
#     people['person_list'] = Person.objects.all()
#     return render(request, 'tasks/detail_view.html', people)

# update
# def task_update_view(request, nid):
#     context ={}
#     # fetch the object related to passed id
#     obj = get_object_or_404(Event, id = nid)
#     # pass the object as instance in form
#     form = TaskForm(request.POST or None, instance = obj)
#     # save the data from the form and
#     # redirect to detail_view
#     if form.is_valid():
#         form.save()
#         messages.add_message(request, messages.SUCCESS, 'Task Updated')
#         return redirect('tasks_detail', nid)
#     # add form dictionary to context
#     context["form"] = form
#     return render(request, "events/update_view.html", context)

class TaskListView(ListView):
 model = Task
 template_name = 'events/task_list.html'
 context_object_name = 'task_list'

 def get_queryset(self):
  return Task.objects.filter(event__id=self.kwargs['nid'])

# def taskListView(request, nid):
#     tasks = Task.objects.filter(event__id=nid)
#     context = {}
#     context['task_list'] = tasks
#     return render(request, 'events/task_list.html', context)

class CreateTaskView(CreateView):
 model = Task
 form_class = TaskForm
 template_name = "events/create_view.html"

 def get_initial(self): # set the initial value of our event field
  event = Event.objects.get(id=self.kwargs['nid'])
  return {'event': event}

 def get_success_url(self): # redirect to the event detail view on success
  return reverse_lazy('events_detail', kwargs={'pk':self.kwargs['nid']})

# def task_create_view(request):
#     context = {}
#     form = EventForm(request.POST or None)
#     if(request.method == 'POST'):
#         if form.is_valid():
#             form.save()
#             messages.add_message(request, messages.SUCCESS, 'Event Created')
#             return redirect('events_index')
#         else:
#             messages.add_message(request, messages.ERROR, 'Invalid Form Data; Event not created')
        
#     context['form']= form
#     return render(request, "events/create_view.html", context)

class CompleteTaskView(View):
 def get(self, request):
  tid = request.GET.get('task_id')
  task = get_object_or_404(Task, pk=tid)

  task.complete = not(task.complete)
  task.save()

  return JsonResponse({'complete': task.complete, 'tid': tid}, status=200)

class DeleteTaskView(View):
 def get(self, request):
  tid = request.GET.get('task_id')
  try:
   task = Task.objects.get(pk=tid)
  except Task.DoesNotExist:
   return JsonResponse({'delete_success': False, 'tid': tid}, status=200)
  task.delete()
  return JsonResponse({'delete_success': True, 'tid': tid}, status=200)

class EditTaskView(View):
     def get(self, request):
        tid = request.GET.get('id', None)
        ttitle = request.GET.get('title', None)
        tdescription = request.GET.get('description', None)
        # tdeadline = request.GET.get('deadline', None)
        # tcomplete = request.GET.get('complete', None)
        # tevent = request.GET.get('event', None)
        # tperson = request.GET.get('person', None)

        obj = Task.objects.get(id = tid)
        obj.title = ttitle
        obj.description = tdescription
        # obj.deadline = tdeadline
        # obj.complete = tcomplete
        # obj.event = tevent
        # obj.person = tperson
        obj.save()

        task = {'id':obj.id, 'title':obj.title, 'description':obj.description, 'deadline':obj.deadline, 'complete': obj.complete, 'event': obj.event, 'person': obj.person}
        data = {
            'task': task
        }
        return JsonResponse(data)

def is_admin(user):
    return user.groups.filter(name='NotesAdminUsers').exists()