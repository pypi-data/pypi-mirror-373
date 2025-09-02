"""
Configuration validation and settings for django-bulk-drf.

This module provides clean, modern settings without backwards compatibility.
All settings use the BULK_DRF_ prefix for consistency and clarity.
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

    Settings can be overridden in Django settings using BULK_DRF_* prefix.

    Returns:
        dict: Settings dictionary with defaults applied
    """
    return {
        'chunk_size': getattr(settings, 'BULK_DRF_CHUNK_SIZE', 100),
        'max_records': getattr(settings, 'BULK_DRF_MAX_RECORDS', 10000),
        'cache_timeout': getattr(settings, 'BULK_DRF_CACHE_TIMEOUT', 86400),
        'progress_update_interval': getattr(settings, 'BULK_DRF_PROGRESS_UPDATE_INTERVAL', 10),
        'batch_size': getattr(settings, 'BULK_DRF_BATCH_SIZE', 1000),
        'use_optimized_tasks': getattr(settings, 'BULK_DRF_USE_OPTIMIZED_TASKS', True),
        'auto_optimize_queries': getattr(settings, 'BULK_DRF_AUTO_OPTIMIZE_QUERIES', True),
        'query_timeout': getattr(settings, 'BULK_DRF_QUERY_TIMEOUT', 300),  # 5 minutes
        'enable_metrics': getattr(settings, 'BULK_DRF_ENABLE_METRICS', False),

        # Sync Upsert Settings
        'sync_upsert_max_items': getattr(settings, 'BULK_DRF_SYNC_UPSERT_MAX_ITEMS', 50),
        'sync_upsert_batch_size': getattr(settings, 'BULK_DRF_SYNC_UPSERT_BATCH_SIZE', 1000),
        'sync_upsert_timeout': getattr(settings, 'BULK_DRF_SYNC_UPSERT_TIMEOUT', 30),  # 30 seconds
    } 