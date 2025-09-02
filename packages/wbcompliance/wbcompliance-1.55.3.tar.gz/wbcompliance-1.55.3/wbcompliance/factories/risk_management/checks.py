import factory
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from wbcompliance.models.risk_management.checks import RiskCheck


class RiskCheckFactory(factory.django.DjangoModelFactory):
    rule = factory.SubFactory("wbcompliance.factories.risk_management.rules.RiskRuleFactory")
    evaluation_date = factory.Faker("date_object")
    checked_object_content_type = factory.LazyAttribute(lambda o: ContentType.objects.get_for_model(get_user_model()))
    checked_object_id = 1

    @factory.post_generation
    def rule_checked_object_relationship(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.rule = extracted.rule
            self.checked_object_id = extracted.checked_object_id
            self.checked_object_content_type = extracted.checked_object_content_type

    class Meta:
        model = RiskCheck
