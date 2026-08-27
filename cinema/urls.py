from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cinema.views import (
    MovieViewSet,
    MovieSessionViewSet,
    OrderViewSet,
)

router = DefaultRouter()
router.register("movies", MovieViewSet)
router.register("movie_sessions", MovieSessionViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "cinema"