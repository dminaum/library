from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Author(TimeStampedModel):
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
        ]
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name}".strip()


class Book(TimeStampedModel):
    class Genre(models.TextChoices):
        FICTION = "fiction", "Художественная"
        NONFICTION = "nonfiction", "Нон-фикшн"
        SCIENCE = "science", "Наука"
        FANTASY = "fantasy", "Фэнтези"
        DETECTIVE = "detective", "Детектив"
        OTHER = "other", "Другое"

    title = models.CharField(max_length=255, db_index=True)
    isbn = models.CharField(max_length=32, unique=True)
    description = models.TextField(blank=True)
    genre = models.CharField(max_length=32, choices=Genre.choices, default=Genre.OTHER)
    published_year = models.PositiveIntegerField()
    author = models.ForeignKey(Author, on_delete=models.PROTECT, related_name="books")
    copies_total = models.PositiveIntegerField(default=1)
    copies_available = models.PositiveIntegerField(default=1)

    class Meta:
        indexes = [
            models.Index(fields=["genre"]),
            models.Index(fields=["published_year"]),
            models.Index(fields=["author"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(copies_available__gte=0),
                name="copies_available_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(copies_available__lte=models.F("copies_total")),
                name="copies_available_le_total",
            ),
        ]
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.isbn})"


class Loan(TimeStampedModel):
    class Status(models.TextChoices):
        ISSUED = "ISSUED", "Выдана"
        RETURNED = "RETURNED", "Возвращена"
        OVERDUE = "OVERDUE", "Просрочена"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="loans"
    )
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="loans")
    issued_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.ISSUED
    )

    class Meta:
        indexes = [
            models.Index(fields=["user", "book"]),
            models.Index(fields=["due_at"]),
            models.Index(fields=["status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"],
                condition=models.Q(returned_at__isnull=True),
                name="uniq_active_loan_per_user_book",
            )
        ]
        ordering = ["-issued_at"]

    def __str__(self):
        return f"Loan[{self.pk}] {self.user} -> {self.book}"
