from django.utils.module_loading import autodiscover_modules
from django.db import DEFAULT_DB_ALIAS
from django.apps import apps as global_apps


def autodiscover_riskmanagement_backends(
    app_config, verbosity=2, interactive=True, using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs
):
    # we wrap the autodiscover into a post_migrate receiver because we expect db calls
    autodiscover_modules("risk_management.backends")
