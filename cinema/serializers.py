from rest_framework import serializers
from cinema.models import Genre, Actor, CinemaHall, Movie, MovieSession


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name")


class ActorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="__str__", read_only=True)

    class Meta:
        model = Actor
        fields = ("id", "first_name", "last_name", "full_name")


class CinemaHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = CinemaHall
        fields = ("id", "name", "rows",
                  "seats_in_row", "capacity")


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ("id", "title", "description",
                  "duration", "genres", "actors")


class MovieListSerializer(MovieSerializer):
    genres = serializers.StringRelatedField(many=True)
    actors = serializers.StringRelatedField(many=True)


class MovieRetrieveSerializer(MovieSerializer):
    genres = GenreSerializer(many=True)
    actors = ActorSerializer(many=True)


class TicketPlacesSerializer(serializers.Serializer):
    row = serializers.IntegerField()
    seat = serializers.IntegerField()


class MovieSessionSerializer(serializers.ModelSerializer):
    taken_places = serializers.SerializerMethodField()
    tickets_available = serializers.SerializerMethodField()

    class Meta:
        model = MovieSession
        fields = (
            "id",
            "movie",
            "cinema_hall",
            "show_time",
            "taken_places",
            "tickets_available",
        )

    def get_taken_places(self, obj) -> list[dict]:
        return [
            {"row": ticket.row, "seat": ticket.seat}
            for ticket in obj.tickets.all()
        ]

    def get_tickets_available(self, obj) -> int:
        taken_count = getattr(
            obj, "tickets_count", obj.tickets.count()
        )
        return obj.cinema_hall.capacity - taken_count


class MovieSessionListSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source="movie.title",
                                        read_only=True)
    cinema_hall_name = serializers.CharField(
        source="cinema_hall.name", read_only=True
    )
    cinema_hall_capacity = serializers.IntegerField(
        source="cinema_hall.capacity", read_only=True
    )
    tickets_available = serializers.SerializerMethodField()

    class Meta:
        model = MovieSession
        fields = (
            "id",
            "show_time",
            "movie_title",
            "cinema_hall_name",
            "cinema_hall_capacity",
            "tickets_available",
        )

    def get_tickets_available(self, obj) -> int:
        taken_count = getattr(
            obj, "tickets_count", obj.tickets.count()
        )
        return obj.cinema_hall.capacity - taken_count


class MovieSessionRetrieveSerializer(MovieSessionSerializer):
    movie = MovieListSerializer(read_only=True)
    cinema_hall = CinemaHallSerializer(read_only=True)
