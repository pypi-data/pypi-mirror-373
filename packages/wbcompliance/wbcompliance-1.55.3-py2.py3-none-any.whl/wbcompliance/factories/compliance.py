import factory
import pytz

from wbcompliance.models import (
    ComplianceAction,
    ComplianceEvent,
    ComplianceForm,
    ComplianceFormRule,
    ComplianceFormSection,
    ComplianceFormSignature,
    ComplianceFormSignatureRule,
    ComplianceFormSignatureSection,
    ComplianceFormType,
    ComplianceTask,
    ComplianceTaskGroup,
    ComplianceTaskInstance,
    ComplianceType,
    ReviewComplianceTask,
)


class ComplianceFormTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComplianceFormType

    name = factory.Faker("text", max_nb_chars=32)


class ComplianceFormFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComplianceForm

    form_type = factory.SubFactory(ComplianceFormTypeFactory)
    creator = factory.SubFactory("wbcore.contrib.authentication.factories.AuthenticatedPersonFactory")
    created = factory.Faker("date_time", tzinfo=pytz.utc)
    changer = factory.SubFactory("wbcore.contrib.authentication.factories.AuthenticatedPersonFactory")
    changed = factory.Faker("date_time", tzinfo=pytz.utc)
    title = factory.Faker("text", max_nb_chars=64)
    policy = factory.Faker("paragraph", nb_sentences=5)
    only_internal = factory.Faker("pybool")
    start = factory.Faker("date_between", start_date="+2d", end_date="+3d")
    end = factory.Faker("date_between", start_date="+4d", end_date="+5d")
    compliance_type = factory.SubFactory("wbcompliance.factories.ComplianceTypeFactory")

    @factory.post_generation
    def assigned_to(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for group in extracted:
                self.assigned_to.add(group)


class UnsignedComplianceFormSignatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComplianceFormSignature

    compliance_form = factory.SubFactory(ComplianceFormFactory)
    policy = factory.Faker("paragraph", nb_sentences=5)
    person = factory.SubFactory("wbcore.contrib.authentication.factories.AuthenticatedPersonFactory")
    remark = factory.Faker("paragraph", nb_sentences=5)
    start = factory.Faker("date_between", start_date="+2d", end_date="+3d")
    end = factory.Faker("date_between", start_date="+4d", end_date="+5d")


class ComplianceFormSignatureFactory(UnsignedComplianceFormSignatureFactory):
    signed = None


class ComplianceFormSectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComplianceFormSection

    compliance_form = factory.SubFactory(ComplianceFormFactory)
    name = factory.Faker("text", max_nb_chars=32)


class ComplianceFormRuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComplianceFormRule

    section = factory.SubFactory(ComplianceFormSectionFactory)
    text = factory.Faker("text", max_nb_chars=255)


class ComplianceFormSignatureSectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComplianceFormSignatureSection

    compliance_form_signature = factory.SubFactory(UnsignedComplianceFormSignatureFactory)
    name = factory.Faker("text", max_nb_chars=32)


class ComplianceFormSignatureRuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComplianceFormSignatureRule

    section = factory.SubFactory(ComplianceFormSignatureSectionFactory)
    text = factory.Faker("text", max_nb_chars=255)


class ComplianceTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComplianceType

    name = factory.Faker("text", max_nb_chars=32)
    description = factory.Faker("text", max_nb_chars=255)

    @factory.post_generation
    def in_charge(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for group in extracted:
                self.in_charge.add(group)


class ComplianceTaskGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComplianceTaskGroup

    name = factory.Faker("text", max_nb_chars=32)
    order = factory.Faker("pyint", min_value=0, max_value=9999)


class ParentReviewComplianceTaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReviewComplianceTask

    title = factory.Faker("text", max_nb_chars=32)
    from_date = factory.Faker("date_between", start_date="+2d", end_date="+3d")
    to_date = factory.Faker("date_between", start_date="+4d", end_date="+5d")
    description = factory.Faker("text", max_nb_chars=255)
    year = factory.Faker("year")
    creator = factory.SubFactory("wbcore.contrib.authentication.factories.AuthenticatedPersonFactory")
    created = factory.Faker("date_time", tzinfo=pytz.utc)
    changer = factory.SubFactory("wbcore.contrib.authentication.factories.AuthenticatedPersonFactory")
    changed = factory.Faker("date_time", tzinfo=pytz.utc)
    review_task = None
    occured = factory.Faker("date")
    type = factory.SubFactory("wbcompliance.factories.ComplianceTypeFactory")


class ReviewComplianceTaskFactory(ParentReviewComplianceTaskFactory):
    class Meta:
        model = ReviewComplianceTask

    review_task = factory.SubFactory(ParentReviewComplianceTaskFactory)


class ComplianceTaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComplianceTask

    title = factory.Faker("text", max_nb_chars=32)
    description = factory.Faker("text", max_nb_chars=255)
    group = factory.SubFactory(ComplianceTaskGroupFactory)
    type = factory.SubFactory(ComplianceTypeFactory)
    risk_level = "LOW"
    remarks = factory.Faker("text", max_nb_chars=255)

    @factory.post_generation
    def review(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for item in extracted:
                self.review.add(item)


class ComplianceTaskReviewFactory(ComplianceTaskFactory):
    @factory.post_generation
    def review(self, create, extracted, **kwargs):
        review = ReviewComplianceTaskFactory()
        self.review.add(review)


class ComplianceTaskReviewNoGroupFactory(ComplianceTaskReviewFactory):
    group = None


class ComplianceTaskInstanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComplianceTaskInstance

    text = factory.Faker("text", max_nb_chars=255)
    summary_text = factory.Faker("text", max_nb_chars=255)
    task = factory.SubFactory(ComplianceTaskFactory)

    @factory.post_generation
    def review(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for item in extracted:
                self.review.add(item)


class ComplianceTaskInstanceReviewFactory(ComplianceTaskInstanceFactory):
    @factory.post_generation
    def review(self, create, extracted, **kwargs):
        review = ReviewComplianceTaskFactory()
        self.review.add(review)


class ComplianceTaskInstanceReviewNoGroupFactory(ComplianceTaskInstanceFactory):
    @factory.post_generation
    def review(self, create, extracted, **kwargs):
        self.task.group = None
        review = ReviewComplianceTaskFactory()
        self.review.add(review)
        self.task.save()


class ComplianceActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComplianceAction

    title = factory.Faker("text", max_nb_chars=32)
    description = factory.Faker("text", max_nb_chars=255)
    summary_description = factory.Faker("text", max_nb_chars=255)
    deadline = factory.Faker("date_between", start_date="+2d", end_date="+3d")
    type = factory.SubFactory(ComplianceTypeFactory)
    creator = factory.SubFactory("wbcore.contrib.authentication.factories.AuthenticatedPersonFactory")
    created = factory.Faker("date_time", tzinfo=pytz.utc)
    changer = factory.SubFactory("wbcore.contrib.authentication.factories.AuthenticatedPersonFactory")


class ComplianceEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComplianceEvent

    title = factory.Faker("text", max_nb_chars=32)
    exec_summary = factory.Faker("text", max_nb_chars=255)
    exec_summary_board = factory.Faker("text", max_nb_chars=255)
    description = factory.Faker("text", max_nb_chars=255)
    actions_taken = factory.Faker("text", max_nb_chars=255)
    consequences = factory.Faker("text", max_nb_chars=255)
    future_suggestions = factory.Faker("text", max_nb_chars=255)
    type = factory.SubFactory(ComplianceTypeFactory)
    creator = factory.SubFactory("wbcore.contrib.authentication.factories.AuthenticatedPersonFactory")
    created = factory.Faker("date_time", tzinfo=pytz.utc)
    changer = factory.SubFactory("wbcore.contrib.authentication.factories.AuthenticatedPersonFactory")
