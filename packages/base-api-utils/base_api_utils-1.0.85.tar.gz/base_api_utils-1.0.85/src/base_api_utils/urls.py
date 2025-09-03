from django.urls import path

from .views import TasksResultAPIView

private_tasks_admin_patterns = ([
    path('', TasksResultAPIView.as_view({'get': 'list'}), name='tasks_result'),
    path('/<str:pk>/retry', TasksResultAPIView.as_view({'post': 'retry'}), name='retry'),
], 'private-tasks-admin-endpoints')