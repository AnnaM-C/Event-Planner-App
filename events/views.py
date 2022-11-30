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

# Events Views
@login_required
def events_index_view(request):
    context = {}
    if is_admin(request.user): 
        # context["events_list"] = Event.objects.all()
        context["events_past"] = Event.objects.filter(date__lt = timezone.now())
        context["events_week"] = Event.objects.filter(date__range = [timezone.now(), timezone.now()+timedelta(days=7)])
        context["events_future"] = Event.objects.filter(date__gt = timezone.now()+timedelta(days=7))
    else:
        # context["events_list"] = Event.objects.filter(author=request.user)
        context["events_past"] = Event.objects.filter(author=request.user, date__lt = timezone.now())
        context["events_week"] = Event.objects.filter(author=request.user, date__range = [timezone.now(), timezone.now()+timedelta(days=7)])
        context["events_future"] = Event.objects.filter(author=request.user, date__gt = timezone.now()+timedelta(days=7))
    return render(request, 'events/index.html', context)


@login_required
def index_past_events(request):
    context = {}
    if is_admin(request.user): 
        context["events_list"] = Event.objects.filter(date__lt = timezone.now())
    else:
        context["events_list"] = Event.objects.filter(date__lt = timezone.now(), author=request.user)
    return render(request, 'events/events_view.html', context)

@login_required
def index_nextweek_events(request):
    context = {}
    if is_admin(request.user): 
        context["events_list"] = Event.objects.filter(date__range = [timezone.now(), timezone.now()+timedelta(days=7)])
        context['today'] = timezone.now()
    else:
        context["events_list"] = Event.objects.filter(date__range = [timezone.now(), timezone.now()+timedelta(days=7)], author=request.user)
        context['today'] = timezone.now()
    return render(request, 'events/events_view.html', context)

@login_required
def index_future_events(request):
    context = {}
    if is_admin(request.user): 
        context["events_list"] = Event.objects.filter(date__gt = timezone.now()+timedelta(days=7))
        context['today'] = timezone.now()
    else:
        context["events_list"] = Event.objects.filter(date__gt = timezone.now()+timedelta(days=7), author=request.user)
        context['today'] = timezone.now()
    return render(request, 'events/events_view.html', context)

# view
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

# create
@login_required
def events_create_view(request):
    context = {}
    form = EventForm(request.POST or None, initial={'author':request.user})
    print(request.POST)
    if(request.method == 'POST'):
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Event Created')
            print(request)
            return redirect('events_index')
        else:
            messages.add_message(request, messages.ERROR, 'Invalid Form Data; Event not created')
        
    context['form']= form
    return render(request, "events/create_view.html", context)

# update
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

# delete
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

class TaskListView(LoginRequiredMixin, ListView):
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

class CreateTaskView(LoginRequiredMixin, CreateView):
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

class CompleteTaskView(LoginRequiredMixin, View):
 def get(self, request):
  tid = request.GET.get('task_id')
  task = get_object_or_404(Task, pk=tid)

  task.complete = not(task.complete)
  task.save()

  return JsonResponse({'complete': task.complete, 'tid': tid}, status=200)

class DeleteTaskView(LoginRequiredMixin, View):
 def get(self, request):
  tid = request.GET.get('task_id')
  try:
   task = Task.objects.get(pk=tid)
  except Task.DoesNotExist:
   return JsonResponse({'delete_success': False, 'tid': tid}, status=200)
  task.delete()
  return JsonResponse({'delete_success': True, 'tid': tid}, status=200)

class EditTaskView(LoginRequiredMixin, View):
     def post(self, request):
        obj = Task.objects.filter(id = request.POST.get('taskId'))
        obj.update(title = request.POST.get('taskTitle'),description = request.POST.get('taskDescription'))
        # print(request.POST.get('eventId'))
        return HttpResponseRedirect('' + request.POST.get('eventId'))
        # return reverse_lazy('events_detail', kwargs={'pk':request.POST.get('eventId')})

    #  def get(self, request):
        # eid = self.kwargs['pk']
        # print(eid)
        # tid = request.GET.get('id', None)
        # ttitle = request.GET.get('title', None)
        # tdescription = request.GET.get('description', None)
        # # tdeadline = request.GET.get('deadline', None)
        # # tcomplete = request.GET.get('complete', None)
        # # tevent = request.GET.get('event', None)
        # # tperson = request.GET.get('person', None)

        # obj = Task.objects.get(id = tid)
        # obj.title = ttitle
        # obj.description = tdescription
        # # obj.deadline = tdeadline
        # # obj.complete = tcomplete
        # # obj.event = tevent
        # # obj.person = tperson
        # obj.save()

        # task = {'id':obj.id, 'title':obj.title, 'description':obj.description}
        # data = {
        #     'task': task
        # }
        # return JsonResponse(data)

class PublishEvent(LoginRequiredMixin, View):
 def get(self, request):
  eid = request.GET.get('event_id')
  event = get_object_or_404(Event, pk=eid)

  event.publish = not(event.publish)
  event.save()

  return JsonResponse({'publish': event.publish, 'eid': eid}, status=200)
