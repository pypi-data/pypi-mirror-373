from django.urls import include, path
from wbcore.routers import WBCoreRouter

from wbtasks.viewsets import viewsets

router = WBCoreRouter()
router.register(r"task", viewsets.TaskModelViewSet, basename="task")
router.register(r"taskrepresentation", viewsets.TaskRepresentationViewSet, basename="taskrepresentation")

urlpatterns = [
    path("", include(router.urls)),
]
