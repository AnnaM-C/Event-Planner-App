from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='tasks_index'),
     path('test/', views.detail_view, name='task_detail'),
]