from django.urls import path
from . import views

urlpatterns = [
    # events/
    path('', views.events_index_view, name='events_index'),
    # events/id
    path('<int:pk>', views.EventDetailView.as_view(), name='events_detail'),
    # events/past
    path('past', views.index_past_events, name="past_events"),
    # events/nextweek
    path('nextweek', views.index_nextweek_events, name="thisweek_events"),
    # events/future
    path('future', views.index_future_events, name="future_events"),
    # events/registered
    path('registered', views.index_registered_events, name="registered_events_index"),
    # events/new
    path('new', views.events_create_view, name='events_new'),

    #events/edit/id
    path('edit/<int:nid>', views.events_update_view, name='events_update'),
    #events/delete/id
    path('delete/<int:nid>', views.events_delete_view, name='events_delete'),

    path('publish', views.PublishEvent.as_view(), name='publish_ajax_event'),
    #events/id/tasks/ view.tasklistView
    path('<int:nid>/tasks', views.TaskListView.as_view(), name='task_list'),

    #events/id/task/new
    path('<int:nid>/task/new', views.CreateTaskView.as_view(), name='create_task'),

    #/events/togglecomplete
    path('togglecomplete', views.CompleteTaskView.as_view(), name='complete_task'),
    #/events/deletetask
    path('deletetask', views.DeleteTaskView.as_view(), name='delete_task'),

    path('edittask', views.EditTaskView.as_view(), name='task_ajax_update'),
    # tasks edit
    # path('edit/<int:nid>/task/<int:nid>', views.task_update_view, name='tasks_update'),


]