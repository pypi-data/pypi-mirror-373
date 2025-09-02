import pytest
from wbcore.contrib.authentication.factories import AuthenticatedPersonFactory
from wbtasks.viewsets.viewsets import TaskModelViewSet


@pytest.mark.django_db
class TestSpecificFilters:
    def test_filter_in_charge(self, task_factory):
        person = AuthenticatedPersonFactory()
        person2 = AuthenticatedPersonFactory()
        task_factory(in_charge=person2)
        mvs = TaskModelViewSet()
        qs = mvs.get_serializer_class().Meta.model.objects.all()
        assert mvs.filterset_class().filter_in_charge(qs, "", None) == qs
        assert mvs.filterset_class().filter_in_charge(qs, "", person).count() == 0
        assert mvs.filterset_class().filter_in_charge(qs, "", person2).count() == 1

    def test_filter_participants(self, task_factory):
        person = AuthenticatedPersonFactory()
        person2 = AuthenticatedPersonFactory()
        person3 = AuthenticatedPersonFactory()
        task_factory(
            in_charge=person2,
            assigned_to=(
                person2,
                person3,
            ),
        )
        mvs = TaskModelViewSet()
        qs = mvs.get_serializer_class().Meta.model.objects.all()
        assert mvs.filterset_class().filter_participants(qs, "", None) == qs
        assert mvs.filterset_class().filter_participants(qs, "", [person]).count() == 0
        assert mvs.filterset_class().filter_participants(qs, "", [person2]).count() == 1
        assert mvs.filterset_class().filter_participants(qs, "", [person3]).count() == 1
        assert mvs.filterset_class().filter_participants(qs, "", [person2, person3]).count() == 1
