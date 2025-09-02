import factory
import pytz
from wbcore.contrib.authentication.factories import AuthenticatedPersonFactory

from wbtasks.models import Task


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Faker("text", max_nb_chars=64)
    due_date = factory.Faker("date_time", tzinfo=pytz.utc)
    creation_date = factory.Faker("date_time_between", start_date="+2d", end_date="+3d", tzinfo=pytz.utc)
    starting_date = factory.Faker("date_time_between", start_date="+2d", end_date="+3d", tzinfo=pytz.utc)
    completion_date = factory.Faker("date_time_between", start_date="+4d", end_date="+5d", tzinfo=pytz.utc)
    requester = factory.SubFactory(AuthenticatedPersonFactory)
    in_charge = factory.SubFactory(AuthenticatedPersonFactory)
    widget_endpoint = factory.Faker("text", max_nb_chars=64)
    description = factory.Faker("paragraph")
    comment = factory.Faker("paragraph")

    @factory.post_generation
    def assigned_to(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for participant in extracted:
                self.assigned_to.add(participant)
