from rest_framework import generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import LoanApplication, LoanStatus
from .serializers import LoanApplicationSerializer, AdminLoanApplicationSerializer
from .permissions import IsOwnerOrAdmin, IsAdminUser
from .services import FraudDetectionService
from .paginations import LoanPagination


class LoanApplicationViewSet(ModelViewSet):
    serializer_class = LoanApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LoanPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['date_applied', 'amount_requested']
    ordering = ['-date_applied']

    def get_queryset(self):
        if self.request.user.is_staff:
            return LoanApplication.objects.all().prefetch_related('fraud_flags')
        return LoanApplication.objects.filter(user=self.request.user).prefetch_related('fraud_flags')

    def get_serializer_class(self):
        if self.request.user.is_staff and self.action in ['update', 'partial_update']:
            return AdminLoanApplicationSerializer
        return LoanApplicationSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'approve', 'reject', 'flag']:
            permission_classes = [IsAdminUser]
        elif self.action in ['retrieve']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        loan_application = serializer.save()
        
        # Run fraud detection
        fraud_reasons = FraudDetectionService.check_fraud(
            loan_application.user, 
            loan_application.amount_requested
        )
        
        if fraud_reasons and len(fraud_reasons) > 0:
            FraudDetectionService.flag_loan(loan_application, fraud_reasons)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        loan = self.get_object()
        loan.status = LoanStatus.APPROVED
        loan.save()
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        loan = self.get_object()
        loan.status = LoanStatus.REJECTED
        loan.save()
        return Response({'status': 'rejected'})

    @action(detail=True, methods=['post'])
    def flag(self, request, pk=None):
        loan = self.get_object()
        reason = request.data.get('reason', 'Manual flag by admin')
        FraudDetectionService.flag_loan(loan, [reason])
        return Response({'status': 'flagged'})


class FlaggedLoansView(generics.ListAPIView):
    serializer_class = LoanApplicationSerializer
    permission_classes = [IsAdminUser]
    pagination_class = LoanPagination

    def get_queryset(self):
        return LoanApplication.objects.filter(status=LoanStatus.FLAGGED).prefetch_related('fraud_flags')
