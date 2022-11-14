from django.urls import path
from . import views

urlpatterns = [
    # events/
    path('', views.events_index_view, name='events_index'),
    # events/id
    path('<int:pk>', views.EventDetailView.as_view(), name='events_detail'),
     #events/new
    path('new', views.events_create_view, name='events_new'),
    #events/edit/id
    path('edit/<int:nid>', views.events_update_view, name='events_update'),
    #events/delete/id
    path('delete/<int:nid>', views.events_delete_view, name='events_delete'),

    #notes/id/tasks/ view.tasklistView
    path('<int:nid>/tasks', views.TaskListView.as_view(), name='task_list'),
    #notes/id/task/new
    path('<int:nid>/task/new', views.CreateTaskView.as_view(), name='create_task'),
    
    path('tasks/', views.tasks_index_view, name='tasks_index'),
    path('test/', views.task_detail_view, name='task_detail'),
]