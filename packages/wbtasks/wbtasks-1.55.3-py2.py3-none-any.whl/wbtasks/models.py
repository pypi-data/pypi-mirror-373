from datetime import timedelta

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_fsm import FSMField, transition
from psycopg.types.range import TimestamptzRange
from rest_framework.reverse import reverse
from wbcore.contrib.agenda.models import CalendarItem
from wbcore.contrib.agenda.signals import draggable_calendar_item_ids
from wbcore.contrib.icons import WBIcon
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.contrib.tags.models import TagModelMixin
from wbcore.enums import RequestType
from wbcore.metadata.configs.buttons import ActionButton, ButtonDefaultColor
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)
from wbcore.shares.signals import handle_widget_sharing


def can_modify_status(instance, user):
    return hasattr(user, "profile") and user.profile in [instance.requester, instance.in_charge]


class Task(TagModelMixin, CalendarItem):
    class Status(models.TextChoices):
        UNSCHEDULED = "UNSCHEDULED", "Unscheduled"
        STARTED = "STARTED", "Started"
        COMPLETED = "COMPLETED", "Completed"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    fsm_base_button_parameters = {
        "method": RequestType.PATCH,
        "identifiers": ("wbtasks:task",),
        "description_fields": "<p>{{ title }}</p>",
    }

    start_button = ActionButton(
        key="start",
        label="Start",
        action_label="start",
        color=ButtonDefaultColor.WARNING,
        icon=WBIcon.SEND.icon,
        **fsm_base_button_parameters,
    )

    complete_button = ActionButton(
        key="complete",
        label="Complete",
        action_label="complete",
        color=ButtonDefaultColor.SUCCESS,
        instance_display=create_simple_display([["comment"]]),
        icon=WBIcon.CONFIRM.icon,
        **fsm_base_button_parameters,
    )

    due_date = models.DateTimeField(verbose_name="Due Date", null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Creation Date")
    starting_date = models.DateTimeField(blank=True, null=True, verbose_name="Started at")
    completion_date = models.DateTimeField(blank=True, null=True, verbose_name="Completed at")

    requester = models.ForeignKey(
        "directory.Person",
        verbose_name="Requester",
        related_name="created_tasks",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    in_charge = models.ForeignKey(
        "directory.Person",
        verbose_name="In charge",
        related_name="in_charge_of_tasks",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    assigned_to = models.ManyToManyField(
        "directory.Person",
        related_name="participates_tasks",
        blank=True,
        verbose_name="Participants",
        help_text="The list of participants",
    )
    status = FSMField(default=Status.UNSCHEDULED, choices=Status.choices, verbose_name="Status")

    description = models.TextField(default="", verbose_name="Description")
    comment = models.TextField(default="", verbose_name="Comment")
    priority = models.CharField(
        default=Priority.LOW, choices=Priority.choices, verbose_name="Priority level", max_length=16
    )

    widget_endpoint = models.CharField(max_length=256, verbose_name="Widget Endpoint", default="")

    class Meta:
        notification_types = [
            create_notification_type(
                "wbtasks.task.notify", "Task Notification", "Sends a notification when a task is due."
            ),
        ]

    @transition(
        status,
        source=[Status.UNSCHEDULED],
        target=Status.STARTED,
        permission=can_modify_status,
        custom={"_transition_button": start_button},
    )
    def start(self, by=None, description=None, **kwargs):
        self.starting_date = timezone.now()

    @transition(
        status,
        source=[Status.STARTED],
        target=Status.COMPLETED,
        permission=can_modify_status,
        custom={"_transition_button": complete_button},
    )
    def complete(self, by=None, description=None, **kwargs):
        self.completion_date = timezone.now()

    def get_tag_detail_endpoint(self):
        return reverse("wbtasks:task-detail", [self.id])

    def get_tag_representation(self):
        return self.title

    def get_color(self) -> str:
        return "#f48474"  # light red

    def get_icon(self) -> str:
        return WBIcon.WARNING.icon

    def save(self, *args, **kwargs):
        if self.due_date and not (self.starting_date and self.completion_date):
            start = self.due_date
            end = self.due_date + timedelta(seconds=1)
            self.period = TimestamptzRange(start, end)
        elif self.starting_date and self.completion_date:
            self.period = TimestamptzRange(self.starting_date, self.completion_date)

        return super().save(*args, **kwargs)

    @classmethod
    def get_endpoint_basename(cls):
        return "wbtasks:task"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbtasks:taskrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "title"


@receiver(post_save, sender=Task)
def post_save_task(sender, instance: Task, created: bool, **kwargs):
    """
    Post save signal.
    * Notifies assigned_to person that a task has been assigned to him
    """

    if (
        created
        and instance.requester != instance.in_charge
        and instance.in_charge
        and hasattr(instance.in_charge, "user_account")
    ):
        send_notification(
            code="wbtasks.task.notify",
            title="A new task has been assigned to you",
            body=f"The task {instance.title} was requested by {str(instance.in_charge)} and is due {instance.due_date:%d.%m.%Y}, check it out!",
            user=instance.in_charge.user_account,
            reverse_name="wbtasks:task-detail",
            reverse_args=[instance.id],
        )

    instance.entities.set(instance.assigned_to.values_list("id", flat=True))
    if in_charge := instance.in_charge:
        instance.entities.add(in_charge)
    if requester := instance.requester:
        instance.entities.add(requester)


@receiver(draggable_calendar_item_ids, sender="agenda.CalendarItem")
def tasks_draggable_calendar_item_ids(sender, request, **kwargs) -> models.QuerySet[CalendarItem]:
    return Task.objects.filter(in_charge=request.user.profile, status=Task.Status.UNSCHEDULED).values("id")


@receiver(handle_widget_sharing)
def received_handle_share(
    request,
    widget_relative_endpoint,
    task_share=None,
    task_title=None,
    task_description=None,
    task_due_date=None,
    task_in_charge=None,
    **kwargs,
):
    if task_share and task_in_charge:
        Task.objects.create(
            requester=request.user.profile,
            in_charge=task_in_charge,
            title=task_title if task_title else "Share widget Task",
            description=task_description if task_description else "",
            widget_endpoint=widget_relative_endpoint,
            due_date=task_due_date,
        )
