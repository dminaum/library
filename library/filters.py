import django_filters as df

from .models import Author, Book


class AuthorFilter(df.FilterSet):
    first_name = df.CharFilter(field_name="first_name", lookup_expr="icontains")
    last_name = df.CharFilter(field_name="last_name", lookup_expr="icontains")

    class Meta:
        model = Author
        fields = ["first_name", "last_name", "date_of_birth"]


class BookFilter(df.FilterSet):
    title = df.CharFilter(field_name="title", lookup_expr="icontains")
    description = df.CharFilter(field_name="description", lookup_expr="icontains")
    author = df.NumberFilter(field_name="author_id")
    author_name = df.CharFilter(method="filter_author_name")
    genre = df.CharFilter(field_name="genre", lookup_expr="iexact")
    published_year = df.NumberFilter(field_name="published_year")
    published_year_min = df.NumberFilter(field_name="published_year", lookup_expr="gte")
    published_year_max = df.NumberFilter(field_name="published_year", lookup_expr="lte")
    isbn = df.CharFilter(field_name="isbn", lookup_expr="iexact")

    class Meta:
        model = Book
        fields = ["title", "author", "genre", "published_year", "isbn"]

    def filter_author_name(self, queryset, name, value):
        return queryset.filter(author__first_name__icontains=value) | queryset.filter(
            author__last_name__icontains=value
        )
