from contextlib import suppress

from django.core.exceptions import MultipleObjectsReturned
from django.db.utils import ProgrammingError

from .rules import RuleBackend, RuleGroup


def register(backend_name: str | None, incident_report_template: str | None = None, rule_group_key: str | None = None):
    """
    Decorator to include when a backend need automatic registration
    Args:
        backend_name:

    Returns:

    """
    if not backend_name:
        raise ValueError("At least one name must be passed to register.")

    def _decorator(backend_class):
        with suppress(RuntimeError, MultipleObjectsReturned, ProgrammingError):
            defaults = {
                "name": backend_name,
                "allowed_checked_object_content_type": backend_class.get_allowed_content_type(),
            }
            if incident_report_template:
                defaults["incident_report_template"] = incident_report_template
            if rule_group_key:
                defaults["rule_group"] = RuleGroup.objects.get_or_create(
                    key=rule_group_key, defaults={"name": rule_group_key.title()}
                )[0]

            RuleBackend.objects.update_or_create(
                backend_class_path=backend_class.__module__,
                backend_class_name=backend_class.__name__,
                defaults=defaults,
            )
        return backend_class

    return _decorator
