from rest_framework import filters
from wbcore.filters import DjangoFilterBackend
from wbcore.viewsets import ModelViewSet, RepresentationViewSet

from wbtasks.filters import TaskFilter
from wbtasks.models import Task
from wbtasks.serializers import TaskModelSerializer, TaskRepresentationSerializer
from wbtasks.viewsets import TaskButtonConfig, TaskDisplayConfig, TaskTitleConfig


class TaskRepresentationViewSet(RepresentationViewSet):
    serializer_class = TaskRepresentationSerializer
    queryset = Task.objects.all()

    search_fields = ("title",)


class TaskModelViewSet(ModelViewSet):
    IDENTIFIER = "wbtasks:task"

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    ordering_fields = ["due_date", "creation_date", "starting_date", "completion_date"]
    ordering = ["-due_date"]
    search_fields = ["title", "requester__computed_str", "assigned_to__computed_str", "description"]

    serializer_class = TaskModelSerializer
    filterset_class = TaskFilter
    queryset = Task.objects.all()

    display_config_class = TaskDisplayConfig
    button_config_class = TaskButtonConfig
    title_config_class = TaskTitleConfig
