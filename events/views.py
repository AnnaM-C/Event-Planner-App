from django.shortcuts import render

# Create your views here.
def event(request):
    context = {}
    return render(request, 'events/events.html', context)
