from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoanApplicationViewSet, FlaggedLoansView

app_name = 'loans'

router = DefaultRouter()
router.register('applications', LoanApplicationViewSet, basename='loan-applications')

urlpatterns = [
    path('', include(router.urls)),
    path('flagged/', FlaggedLoansView.as_view(), name='flagged-loans'),
]
