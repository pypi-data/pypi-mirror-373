"""
Configuration validation for django-bulk-drf.
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def validate_bulk_drf_config():
    """
    Validate that required settings are configured for django-bulk-drf.

    Raises:
        ImproperlyConfigured: If required settings are missing or invalid
    """
    # Check if cache is configured
    if not hasattr(settings, 'CACHES') or 'default' not in settings.CACHES:
        raise ImproperlyConfigured(
            "django-bulk-drf requires a cache backend to be configured. "
            "Please add CACHES setting to your Django settings."
        )

    # Check if Celery is configured
    if not hasattr(settings, 'CELERY_BROKER_URL'):
        raise ImproperlyConfigured(
            "django-bulk-drf requires Celery to be configured. "
            "Please add CELERY_BROKER_URL setting to your Django settings."
        )

    # Check if REST framework is installed
    if 'rest_framework' not in getattr(settings, 'INSTALLED_APPS', []):
        raise ImproperlyConfigured(
            "django-bulk-drf requires Django REST Framework to be installed. "
            "Please add 'rest_framework' to INSTALLED_APPS."
        )


def get_bulk_drf_settings():
    """
    Get django-bulk-drf specific settings with defaults.

    Returns:
        dict: Settings dictionary with defaults applied
    """
    return {
        'BULK_DRF_CHUNK_SIZE': getattr(settings, 'BULK_DRF_CHUNK_SIZE', 100),
        'BULK_DRF_MAX_RECORDS': getattr(settings, 'BULK_DRF_MAX_RECORDS', 10000),
        'BULK_DRF_CACHE_TIMEOUT': getattr(settings, 'BULK_DRF_CACHE_TIMEOUT', 86400),
        'BULK_DRF_PROGRESS_UPDATE_INTERVAL': getattr(settings, 'BULK_DRF_PROGRESS_UPDATE_INTERVAL', 10),
        'BULK_DRF_BATCH_SIZE': getattr(settings, 'BULK_DRF_BATCH_SIZE', 1000),
        'BULK_DRF_USE_OPTIMIZED_TASKS': getattr(settings, 'BULK_DRF_USE_OPTIMIZED_TASKS', True),
        'BULK_DRF_AUTO_OPTIMIZE_QUERIES': getattr(settings, 'BULK_DRF_AUTO_OPTIMIZE_QUERIES', True),
        'BULK_DRF_QUERY_TIMEOUT': getattr(settings, 'BULK_DRF_QUERY_TIMEOUT', 300),  # 5 minutes
        'BULK_DRF_ENABLE_METRICS': getattr(settings, 'BULK_DRF_ENABLE_METRICS', False),

        # Sync Upsert Settings
        'BULK_DRF_SYNC_UPSERT_MAX_ITEMS': getattr(settings, 'BULK_DRF_SYNC_UPSERT_MAX_ITEMS', 50),
        'BULK_DRF_SYNC_UPSERT_BATCH_SIZE': getattr(settings, 'BULK_DRF_SYNC_UPSERT_BATCH_SIZE', 1000),
        'BULK_DRF_SYNC_UPSERT_TIMEOUT': getattr(settings, 'BULK_DRF_SYNC_UPSERT_TIMEOUT', 30),  # 30 seconds
    } 