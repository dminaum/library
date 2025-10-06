from datetime import timedelta

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import Book, Loan


@transaction.atomic
def issue_book(
    *, actor, book_id: int, borrower_id: int | None = None, days: int | None = None
) -> Loan:
    """
    Выдать книгу.
    - actor: кто инициирует (для проверок прав)
    - borrower_id: кому выдаём (если None → actor.id, т.е. самовыдача)
    - транзакция + select_for_update на книгу
    """
    if borrower_id is None:
        borrower_id = actor.id

    if not actor.is_staff and borrower_id != actor.id:
        raise PermissionDenied("Вы не можете выдавать книги другим пользователям")
    if not actor.is_staff and not settings.ALLOW_SELF_ISSUE:
        raise PermissionDenied("Вы не можете самостоятельно брать книги")

    book = Book.objects.select_for_update().get(pk=book_id)

    if book.copies_available <= 0:
        raise ValidationError("Все копии этой книги недоступны")

    due_days = days or settings.LOAN_DEFAULT_DAYS
    issued_at = timezone.now()
    due_at = issued_at + timedelta(days=due_days)

    try:
        loan = Loan.objects.create(
            user_id=borrower_id,
            book=book,
            issued_at=issued_at,
            due_at=due_at,
            status=Loan.Status.ISSUED,
        )
    except IntegrityError as e:
        raise ValidationError("Этот пользователь уже взял эту книгу") from e

    book.copies_available -= 1
    if book.copies_available < 0:
        raise ValidationError("Вы не можете взять книгу")
    book.save(update_fields=["copies_available"])

    return loan


@transaction.atomic
def return_loan(*, actor, loan_id: int) -> Loan:
    """
    Возврат книги.
    - увеличиваем copies_available
    - ставим returned_at, статус RETURNED
    - только владелец займа или staff
    """
    loan = (
        Loan.objects.select_for_update().select_related("book", "user").get(pk=loan_id)
    )

    if not actor.is_staff and loan.user_id != actor.id:
        raise PermissionDenied("Вы не можете возвращать чужие книги")
    if loan.returned_at:
        raise ValidationError("Книга уже возвращена")

    loan.returned_at = timezone.now()
    loan.status = Loan.Status.RETURNED
    loan.save(update_fields=["returned_at", "status"])

    book = loan.book
    book.copies_available += 1
    if book.copies_available > book.copies_total:
        book.copies_available = book.copies_total
    book.save(update_fields=["copies_available"])

    return loan
