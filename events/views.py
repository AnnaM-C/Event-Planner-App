from django.shortcuts import render
from .models import *
from django.contrib import messages
from django.views.generic import ListView, CreateView, DetailView
from django.shortcuts import (get_object_or_404, render, redirect)
from .forms import EventForm, TaskForm
from django.urls import reverse_lazy

# Events Views
def events_index_view(request):
    context = {}
    context["events_list"] = Event.objects.all()
    return render(request, 'events/index.html', context)

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
def tasks_index_view(request):
    context = {}
    return render(request, 'tasks/tasks.html', context)

def task_detail_view(request):
    people = {}
    people['person_list'] = Person.objects.all()
    return render(request, 'tasks/detail_view.html', people)


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
