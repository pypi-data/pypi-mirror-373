import pytest


@pytest.mark.django_db
class TestSpecificModels:
    def test_start(self, task_factory):
        obj = task_factory()
        assert obj.status == obj.Status.UNSCHEDULED
        obj.start()
        assert obj.status == obj.Status.STARTED

    def test_complete(self, task_factory):
        obj = task_factory()
        obj.start()
        obj.complete()
        assert obj.status == obj.Status.COMPLETED
