from django.utils import timezone
from rest_framework import serializers

from .models import Author, Book, Loan


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id", "first_name", "last_name", "date_of_birth", "bio", "created_at")
        read_only_fields = ("id", "created_at")


class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "isbn",
            "description",
            "genre",
            "published_year",
            "author",
            "author_name",
            "copies_total",
            "copies_available",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "copies_available")

    def get_author_name(self, obj):
        return f"{obj.author.last_name} {obj.author.first_name}".strip()


class LoanSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True)
    effective_status = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = (
            "id",
            "user",
            "user_username",
            "book",
            "book_title",
            "issued_at",
            "due_at",
            "returned_at",
            "status",
            "effective_status",
        )
        read_only_fields = (
            "id",
            "issued_at",
            "returned_at",
            "status",
            "effective_status",
        )

    def get_effective_status(self, obj: Loan) -> str:
        if obj.returned_at is None and timezone.now() > obj.due_at:
            return Loan.Status.OVERDUE
        return obj.status


class IssueInputSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    user_id = serializers.IntegerField(required=False, allow_null=True)


class ReturnInputSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField()
