from django.apps import AppConfig
from django.db.models.signals import post_migrate

from wbcompliance.management import autodiscover_riskmanagement_backends


class WbcomplianceConfig(AppConfig):
    name = "wbcompliance"

    #
    def ready(self) -> None:
        post_migrate.connect(
            autodiscover_riskmanagement_backends,
            dispatch_uid="wbcrm.synchronization.initialize_task",
        )
