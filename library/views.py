from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .filters import AuthorFilter, BookFilter
from .models import Author, Book, Loan
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .serializers import (
    AuthorSerializer,
    BookSerializer,
    IssueInputSerializer,
    LoanSerializer,
    ReturnInputSerializer,
)
from .services import issue_book, return_loan


@extend_schema(tags=["Authors"], summary="CRUD авторов")
class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all().order_by("last_name", "first_name")
    serializer_class = AuthorSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = AuthorFilter
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ("first_name", "last_name", "bio")
    ordering_fields = ("last_name", "first_name", "created_at")


@extend_schema(tags=["Books"], summary="CRUD книг")
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related("author").all().order_by("title")
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = BookFilter
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ("title", "description")
    ordering_fields = ("published_year", "title", "created_at")


@extend_schema(tags=["Loans"], summary="Список/детали выданных книг")
class LoanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/loans/         -> staff видит все, user — только свои
    GET /api/loans/{id}/    -> staff или владелец
    POST /api/loans/issue/  -> выдать (staff — кому угодно; user — себе при ALLOW_SELF_ISSUE)
    POST /api/loans/return/ -> вернуть (staff — любой; user — только свой)
    """

    serializer_class = LoanSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        qs = Loan.objects.select_related("user", "book").order_by("-issued_at")
        user = self.request.user
        if user.is_staff:
            return qs
        return qs.filter(user=user)

    def get_permissions(self):
        if self.action in ("retrieve",):
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        if self.action in ("issue", "return_book"):
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @extend_schema(
        request=IssueInputSerializer,
        responses={201: LoanSerializer, 400: dict},
        summary="Выдать книгу",
    )
    @action(detail=False, methods=["post"], url_path="issue")
    def issue(self, request):
        """
        body: { "book_id": int, "user_id": optional }
        """
        book_id = request.data.get("book_id")
        borrower_id = request.data.get("user_id")
        if not book_id:
            return Response({"detail": "book_id is required"}, status=400)
        try:
            loan = issue_book(
                actor=request.user, book_id=int(book_id), borrower_id=borrower_id
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=400)
        return Response(LoanSerializer(loan).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=ReturnInputSerializer,
        responses={200: LoanSerializer, 400: dict},
        summary="Вернуть книгу",
    )
    @action(detail=False, methods=["post"], url_path="return")
    def return_book(self, request):
        """
        body: { "loan_id": int }
        """
        loan_id = request.data.get("loan_id")
        if not loan_id:
            return Response({"detail": "loan_id is required"}, status=400)
        try:
            loan = return_loan(actor=request.user, loan_id=int(loan_id))
        except Exception as e:
            return Response({"detail": str(e)}, status=400)
        return Response(LoanSerializer(loan).data, status=status.HTTP_200_OK)
