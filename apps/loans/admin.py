from django.contrib import admin
from .models import LoanApplication, FraudFlag


class FraudFlagInline(admin.TabularInline):
    model = FraudFlag
    extra = 0
    readonly_fields = ['reason']


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount_requested', 'status', 'date_applied']
    list_filter = ['status', 'date_applied']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['date_applied', 'date_updated']
    inlines = [FraudFlagInline]

    actions = ['approve_loans', 'reject_loans']

    def approve_loans(self, request, queryset):
        queryset.update(status='approved')
    approve_loans.short_description = "Approve selected loans"

    def reject_loans(self, request, queryset):
        queryset.update(status='rejected')
    reject_loans.short_description = "Reject selected loans"


@admin.register(FraudFlag)
class FraudFlagAdmin(admin.ModelAdmin):
    list_display = ['loan_application', 'reason', 'created_at']
    list_filter = ['created_at']
    search_fields = ['reason', 'loan_application__user__email']
