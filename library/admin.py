from django.contrib import admin

from .models import Author, Book, Loan


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "date_of_birth", "created_at")
    search_fields = ("first_name", "last_name")
    list_filter = ("date_of_birth",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "genre",
        "published_year",
        "isbn",
        "copies_total",
        "copies_available",
        "created_at",
    )
    search_fields = ("title", "isbn", "author__last_name", "author__first_name")
    list_filter = ("genre", "published_year")
    autocomplete_fields = ("author",)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "issued_at", "due_at", "returned_at", "status")
    list_filter = ("status", "due_at", "returned_at")
    search_fields = ("user__username", "book__title", "book__isbn")
    autocomplete_fields = ("user", "book")
