from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LoansConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.loans"
    verbose_name = _("Loans Management")