import datetime
from django.db.models import Count, QuerySet
from rest_framework import viewsets
from rest_framework.serializers import Serializer

from cinema.models import (Genre, Actor,
                           CinemaHall, Movie, MovieSession)
from cinema.serializers import (
    GenreSerializer,
    ActorSerializer,
    CinemaHallSerializer,
    MovieSerializer,
    MovieListSerializer,
    MovieRetrieveSerializer,
    MovieSessionSerializer,
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
        if not params:
            return None
        return [int(id_) for id_ in params.split(",") if id_.isdigit()]

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "list":
            return MovieListSerializer
        if self.action == "retrieve":
            return MovieRetrieveSerializer
        return self.serializer_class

    def get_queryset(self) -> QuerySet[Movie]:
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

        if self.action == "list":
            queryset = (
                queryset.select_related("movie", "cinema_hall")
                .annotate(tickets_count=Count("tickets"))
            )

            movie_id = self.request.query_params.get("movie")
            if movie_id:
                if movie_id.isdigit():
                    queryset = queryset.filter(movie__id=int(movie_id))
                else:
                    return queryset.none()

            date_param = self.request.query_params.get("date")
            if date_param:
                try:
                    parts = date_param.split("-")
                    year, month, day = map(int, parts)
                    q_date = datetime.date(year, month, day)
                    queryset = queryset.filter(show_time__date=q_date)
                except (ValueError, TypeError):
                    return queryset.none()

        elif self.action == "retrieve":
            queryset = (
                queryset.select_related("movie", "cinema_hall")
                .prefetch_related("movie__genres",
                                  "movie__actors", "tickets")
                .annotate(tickets_count=Count("tickets"))
            )

        return queryset.distinct()

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "list":
            return MovieSessionListSerializer
        if self.action == "retrieve":
            return MovieSessionRetrieveSerializer
        return MovieSessionSerializer
