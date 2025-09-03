from rest_framework import viewsets, status
from rest_framework.response import Response
from django_celery_results.models import TaskResult
from celery import current_app

from ..security import oauth2_scope_required, group_required
from ..serializers import TaskResultSerializer


class TasksResultAPIView(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to view failed Celery tasks and retry them manually.
    """
    queryset = TaskResult.objects.filter(status='FAILURE')
    serializer_class = TaskResultSerializer

    @oauth2_scope_required()
    @group_required()
    def retry(self, request, pk=None, *args, **kwargs):
        """Rerun a failed task manually"""
        task_result = self.get_queryset().filter(task_id=pk).first()
        if not task_result:
             return Response({"error": "Task not registered as failed"}, status=status.HTTP_404_NOT_FOUND)

        # Gets the original arguments of the task
        task_name = task_result.task_name
        args = eval(task_result.task_args or '[]')  # Make sure arguments are evaluable
        kwargs = eval(task_result.task_kwargs or '{}')

        # Gets the task from Celery and forwards it
        task = current_app.tasks.get(task_name)
        if task:
            new_task = task.apply_async(args=args, kwargs=kwargs)
            return Response({"message": "Task resubmitted", "new_task_id": new_task.id})
        else:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)