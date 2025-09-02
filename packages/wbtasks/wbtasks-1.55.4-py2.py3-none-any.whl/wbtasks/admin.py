from django.contrib import admin

from wbtasks.models import Task


@admin.register(Task)
class TaskModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "due_date", "requester", "in_charge")

    autocomplete_fields = ["requester", "in_charge"]
