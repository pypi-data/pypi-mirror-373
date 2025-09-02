from __future__ import absolute_import, unicode_literals

from datetime import timedelta

from celery import shared_task
from django.db.models import Q
from django.utils import timezone
from wbcore.contrib.notifications.dispatch import send_notification

from wbtasks.models import Task

NOTIFY_DUE_TASKS_INTERVAL_MINUTES = 60


@shared_task
def notify_due_tasks(now=None, notification=None):
    if not now:
        now = timezone.now()
    for task in Task.objects.filter(
        ~Q(status=Task.Status.COMPLETED)
        & Q(due_date__gt=now)
        & Q(due_date__lt=now + timedelta(minutes=NOTIFY_DUE_TASKS_INTERVAL_MINUTES))
    ):
        if (profile := task.in_charge) and (user := profile.user_account):
            send_notification(
                code="wbtasks.task.notify",
                title="Task is due",
                body=f"the task {task.title} is due at {task.due_date:%d.%m.%Y}",
                user=user,
                reverse_name="wbtasks:task-detail",
                reverse_args=[task.id],
            )
    return notification


# from restbench.celery import app as celery_app

# celery_app.conf.beat_schedule.update({
#     'Tasks: Notify Due tasks': {
#         'task': 'wbtasks.tasks.notify_due_tasks',
#         'schedule': NOTIFY_DUE_TASKS_INTERVAL_MINUTES*60
#     }
# })
