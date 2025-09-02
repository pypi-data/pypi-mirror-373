from wbcore import filters as wb_filters
from wbcore.contrib.directory.models import Entry, Person

from wbtasks.models import Task


def get_current_user_id(field, request, view):
    return request.user.profile.id


class TaskFilter(wb_filters.FilterSet):
    in_charge = wb_filters.ModelChoiceFilter(
        label="Assigned to",
        queryset=Person.objects.all(),
        endpoint=Person.get_representation_endpoint(),
        value_key=Person.get_representation_value_key(),
        label_key=Person.get_representation_label_key(),
        filter_params={"only_internal_users": True},
        # initial=get_current_user_id,
        method="filter_in_charge",
    )

    participants = wb_filters.ModelMultipleChoiceFilter(
        label="Participants",
        queryset=Entry.objects.all(),
        endpoint=Entry.get_representation_endpoint(),
        value_key=Entry.get_representation_value_key(),
        label_key=Entry.get_representation_label_key(),
        # initial=get_current_user_id,
        method="filter_participants",
    )

    def filter_in_charge(self, queryset, name, value):
        if value:
            return queryset.filter(in_charge=value)
        return queryset

    def filter_participants(self, queryset, name, value):
        if value:
            return queryset.filter(assigned_to__in=value).distinct()
        return queryset

    class Meta:
        model = Task
        fields = {
            "starting_date": ["gte", "exact", "lte"],
            "completion_date": ["gte", "exact", "lte"],
            "creation_date": ["gte", "exact", "lte"],
            "due_date": ["gte", "exact", "lte"],
            "requester": ["exact"],
            # "in_charge": ["exact"],
            "assigned_to": ["exact"],
            "status": ["exact"],
            "priority": ["exact"],
        }
