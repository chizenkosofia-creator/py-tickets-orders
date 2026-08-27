from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.serializers import Serializer
from cinema.models import Genre, Actor, CinemaHall, Movie, MovieSession
from cinema.serializers import (
    GenreSerializer,
    ActorSerializer,
    CinemaHallSerializer,
    MovieSerializer,
    MovieSessionSerializer,
    MovieListSerializer,
    MovieRetrieveSerializer,
    MovieSessionListSerializer,
    MovieSessionRetrieveSerializer,
)


class GenreViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ActorViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class CinemaHallViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = CinemaHall.objects.all()
    serializer_class = CinemaHallSerializer


class MovieViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

    @staticmethod
    def parse_query_params(params: str | None) -> list[int] | None:
        if params is None:
            return None
        return [int(id_) for id_ in params.split(",")]

    def get_serializer_class(self):
        serializer = self.serializer_class

        if self.action == "list":
            serializer = MovieListSerializer

        if self.action == "retrieve":
            serializer = MovieRetrieveSerializer

        return serializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related("actors", "genres")
            if self.action == "list":
                actors = self.parse_query_params(
                    self.request.query_params.get("actors")
                )
                if actors:
                    queryset = queryset.filter(actors__id__in=actors)

                genres = self.parse_query_params(
                    self.request.query_params.get("genres")
                )
                if genres:
                    queryset = queryset.filter(genres__id__in=genres)

                title = self.request.query_params.get("title")
                if title:
                    queryset = queryset.filter(title__icontains=title)

        return queryset.distinct()


class MovieSessionViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = MovieSession.objects.all()

    def get_queryset(self) -> QuerySet[MovieSession]:
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            return queryset.select_related("movie", "cinema_hall")
        return queryset

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "list":
            return MovieSessionListSerializer
        elif self.action == "retrieve":
            return MovieSessionRetrieveSerializer
        return MovieSessionSerializer
