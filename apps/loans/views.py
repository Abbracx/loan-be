import logging
from django.core.cache import cache
from django.conf import settings
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

logger = logging.getLogger(__name__)


def safe_cache_delete_pattern(pattern):
    """Safely delete cache pattern, handling DummyCache"""
    try:
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(pattern)
        else:
            # For DummyCache or other backends without delete_pattern
            pass
    except AttributeError:
        pass


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

    def list(self, request, *args, **kwargs):
        cache_key = f"loans_list_{request.user.id}_{request.query_params}"
        cached_response = cache.get(cache_key)
        
        if cached_response:
            logger.info(f"Cache hit for loans list - User: {request.user.id}")
            return Response(cached_response)
        
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        logger.info(f"Loans list cached - User: {request.user.id}")
        return response

    def perform_create(self, serializer):
        loan_application = serializer.save()
        logger.info(f"Loan application created - ID: {loan_application.id}, User: {loan_application.user.id}, Amount: {loan_application.amount_requested}")
        
        # Run fraud detection
        fraud_reasons = FraudDetectionService.check_fraud(
            loan_application.user, 
            loan_application.amount_requested
        )
        
        if fraud_reasons:
            FraudDetectionService.flag_loan(loan_application, fraud_reasons)
            logger.warning(f"Loan flagged for fraud - ID: {loan_application.id}, Reasons: {fraud_reasons}")

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        loan = self.get_object()
        loan.status = LoanStatus.APPROVED
        loan.save()
        logger.info(f"Loan approved - ID: {loan.id}, Admin: {request.user.id}")
        
        # Clear cache safely
        safe_cache_delete_pattern(f"loans_list_{loan.user.id}_*")
        
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        loan = self.get_object()
        loan.status = LoanStatus.REJECTED
        loan.save()
        logger.info(f"Loan rejected - ID: {loan.id}, Admin: {request.user.id}")
        
        # Clear cache safely
        safe_cache_delete_pattern(f"loans_list_{loan.user.id}_*")
        
        return Response({'status': 'rejected'})

    @action(detail=True, methods=['post'])
    def flag(self, request, pk=None):
        loan = self.get_object()
        reason = request.data.get('reason', 'Manual flag by admin')
        FraudDetectionService.flag_loan(loan, [reason])
        logger.warning(f"Loan manually flagged - ID: {loan.id}, Admin: {request.user.id}, Reason: {reason}")
        
        # Clear cache safely
        safe_cache_delete_pattern(f"loans_list_{loan.user.id}_*")
        
        return Response({'status': 'flagged'})


class FlaggedLoansView(generics.ListAPIView):
    serializer_class = LoanApplicationSerializer
    permission_classes = [IsAdminUser]
    pagination_class = LoanPagination

    def get_queryset(self):
        return LoanApplication.objects.filter(status=LoanStatus.FLAGGED).prefetch_related('fraud_flags')

    def list(self, request, *args, **kwargs):
        cache_key = "flagged_loans_list"
        cached_response = cache.get(cache_key)
        
        if cached_response:
            logger.info("Cache hit for flagged loans list")
            return Response(cached_response)
        
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        logger.info("Flagged loans list cached")
        return response