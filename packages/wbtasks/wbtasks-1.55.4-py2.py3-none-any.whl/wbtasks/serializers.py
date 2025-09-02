from datetime import date, timedelta

from django.utils.translation import gettext_lazy as _
from wbcore import serializers as wb_serializers
from wbcore import shares
from wbcore.contrib.directory.models import Person
from wbcore.contrib.directory.serializers import (
    InternalUserProfileRepresentationSerializer,
    PersonRepresentationSerializer,
)
from wbcore.contrib.tags.serializers import TagSerializerMixin
from wbcore.metadata.configs.display.instance_display import (
    create_simple_section,
    repeat_field,
)

from wbtasks.models import Task


class TaskRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = Task
        fields = ("id", "title")


class TaskModelSerializer(TagSerializerMixin, wb_serializers.ModelSerializer):
    _requester = PersonRepresentationSerializer(source="requester")
    _in_charge = InternalUserProfileRepresentationSerializer(source="in_charge")
    _assigned_to = PersonRepresentationSerializer(source="assigned_to", many=True)

    @wb_serializers.register_resource()
    def ressource(self, instance, request, user):
        ressource = {}
        if instance.widget_endpoint:
            ressource["widget"] = instance.widget_endpoint
        return ressource

    def create(self, validated_data):
        if request := self.context.get("request"):
            validated_data["requester"] = request.user.profile
        return super().create(validated_data)

    def validate(self, attrs):
        if self.instance:
            assigned_to = attrs.get("assigned_to", self.instance.assigned_to)
            in_charge = attrs.get("in_charge", self.instance.in_charge)
        else:
            assigned_to = attrs.get("assigned_to", [])
            in_charge = attrs.get("in_charge", None)

        if assigned_to or in_charge:
            list_of_ids = []
            if in_charge:
                list_of_ids.append(in_charge.id)
            if assigned_to:
                if isinstance(assigned_to, list):
                    for person in assigned_to:
                        list_of_ids.append(person.id)
                else:
                    list_of_ids += assigned_to.values_list("id", flat=True)

            attrs["entities"] = Person.objects.filter(id__in=list_of_ids).distinct()

        return super().validate(attrs)

    class Meta:
        model = Task
        required_fields = ("title", "requester")
        read_only_fields = (
            "starting_date",
            "completion_date",
            "creation_date",
        )
        fields = (
            "id",
            "title",
            "starting_date",
            "completion_date",
            "creation_date",
            "due_date",
            "requester",
            "_requester",
            "in_charge",
            "_in_charge",
            "assigned_to",
            "_assigned_to",
            "status",
            "description",
            "comment",
            "priority",
            "tags",
            "_tags",
            "_additional_resources",
        )


class TaskToActivitySerializer(TaskModelSerializer):
    title = wb_serializers.CharField(label="Title", required=False)
    starting_date = wb_serializers.DateTimeField(label="Start")
    completion_date = wb_serializers.DateTimeField(label="End")
    requester = wb_serializers.PrimaryKeyRelatedField(queryset=Person.objects.all(), label="Creator")
    in_charge = wb_serializers.PrimaryKeyRelatedField(queryset=Person.objects.all(), label="In charge to")
    description = wb_serializers.TextField(label="Description")
    comment = wb_serializers.TextField(label="Review")

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "starting_date",
            "completion_date",
            "requester",
            "_requester",
            "in_charge",
            "_in_charge",
            "assigned_to",
            "_assigned_to",
            "description",
            "comment",
            "_requester",
        )


@shares.register(
    section=create_simple_section(
        "task_section",
        _("Share as Task"),
        [
            [repeat_field(4, "task_share")],
            [repeat_field(4, "task_title")],
            [repeat_field(2, "task_due_date"), repeat_field(2, "task_in_charge")],
            [repeat_field(4, "task_description")],
        ],
        collapsed=True,
    )
)
class TaskShareSerializer(wb_serializers.Serializer):
    task_share = wb_serializers.BooleanField(default=False, label=_("Share as Task"))
    task_title = wb_serializers.CharField(
        max_length=256, label=_("Title"), required=False, depends_on=[{"field": "task_share", "options": {}}]
    )
    task_description = wb_serializers.TextField(
        label=_("Description"), required=False, depends_on=[{"field": "task_share", "options": {}}]
    )
    task_due_date = wb_serializers.DateField(
        label=_("Date"),
        required=False,
        default=lambda: date.today() + timedelta(days=7),
        depends_on=[{"field": "task_share", "options": {}}],
    )
    task_in_charge = wb_serializers.PrimaryKeyRelatedField(
        queryset=Person.objects.all(),
        label=_("In Charge"),
        required=False,
        depends_on=[{"field": "task_share", "options": {}}],
    )
    _task_in_charge = PersonRepresentationSerializer(
        source="task_in_charge", depends_on=[{"field": "task_share", "options": {}}]
    )
