from django.shortcuts import render
from .models import *
from django.shortcuts import (get_object_or_404, render, redirect) 

# Create your views here.
def index_view(request):
    context = {}
    return render(request, 'tasks/tasks.html', context)

def detail_view(request):
    people = {}
    people['person_list'] = Person.objects.all()
    return render(request, 'tasks/detail_view.html', people)
