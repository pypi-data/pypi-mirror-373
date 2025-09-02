"""
Django Bulk DRF - Enhanced operations for Django REST Framework

Provides a unified mixin that enhances standard ViewSet endpoints with synchronous
bulk operations that execute heavy database work (including triggers) in Celery workers
while maintaining synchronous API behavior for clients.
"""

__version__ = "0.3.0"
__author__ = "Konrad Beck"
__email__ = "konrad.beck@merchantcapital.co.za"

# Make common imports available at package level
from .mixins import OperationsMixin
from .views import OperationStatusView
from .config import validate_bulk_drf_config, get_bulk_drf_settings

__all__ = [
    "OperationsMixin",
    "OperationStatusView",
    "validate_bulk_drf_config",
    "get_bulk_drf_settings",
]