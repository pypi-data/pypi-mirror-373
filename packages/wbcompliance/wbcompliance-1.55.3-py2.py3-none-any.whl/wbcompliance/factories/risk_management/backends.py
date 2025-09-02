from typing import Generator

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from faker import Faker
from wbcore import serializers as wb_serializers

from wbcompliance.models.risk_management import backend

User = get_user_model()
fake = Faker()


class RuleBackend(backend.AbstractRuleBackend):
    @classmethod
    def get_serializer_class(cls):
        class RuleBackendSerializer(wb_serializers.Serializer):
            date = wb_serializers.DateField(required=False)
            name = wb_serializers.CharField(required=False)
            int = wb_serializers.IntegerField(required=False)
            anonymous_user = wb_serializers.PrimaryKeyRelatedField(
                queryset=User.objects.all(), default=User.objects.none(), required=False
            )

            @classmethod
            def get_parameter_fields(cls):
                return ["date", "name", "int", "anonymous_user"]

        return RuleBackendSerializer

    def check_rule(self, *dto_args, **kwargs) -> Generator[backend.IncidentResult, None, None]:
        severity = self.thresholds.first().severity if self.thresholds.exists() else None
        yield backend.IncidentResult(
            breached_object=None,
            breached_value=str(fake.word()),
            breached_object_repr=fake.text(max_nb_chars=125),
            report_details={"label": fake.paragraph()},
            severity=severity,
        )

    @classmethod
    def get_allowed_content_type(cls) -> "ContentType":
        return None
