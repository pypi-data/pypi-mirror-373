from django.urls import include, path
from wbcore.routers import WBCoreRouter

from wbcompliance import viewsets

router = WBCoreRouter()
router.register(
    r"complianceformrepresentation",
    viewsets.ComplianceFormRepresentationViewSet,
    basename="complianceformrepresentation",
)
router.register(
    r"complianceformsectionrepresentation",
    viewsets.ComplianceFormSectionRepresentationViewSet,
    basename="complianceformsectionrepresentation",
)
router.register(
    r"complianceformsignaturesectionrepresentation",
    viewsets.ComplianceFormSignatureSectionRepresentationViewSet,
    basename="complianceformsignaturesectionrepresentation",
)

router.register(
    r"complianceformtyperepresentation",
    viewsets.ComplianceFormTypeRepresentationViewSet,
    basename="complianceformtyperepresentation",
)
router.register(r"complianceformtype", viewsets.ComplianceFormTypeViewSet, basename="complianceformtype")

router.register(r"complianceform", viewsets.ComplianceFormModelViewSet)
router.register(
    r"complianceformsignature", viewsets.ComplianceFormSignatureModelViewSet, basename="complianceformsignature"
)

router.register(r"complianceformsection", viewsets.ComplianceFormSectionViewSet, basename="complianceformsection")

router.register(r"complianceformrule", viewsets.ComplianceFormRuleViewSet, basename="complianceformrule")

router.register(
    r"compliancetaskrepresentation",
    viewsets.ComplianceTaskRepresentationViewSet,
    basename="compliancetaskrepresentation",
)
router.register(r"compliancetask", viewsets.ComplianceTaskModelViewSet, basename="compliancetask")
router.register(
    r"compliancetaskinstance", viewsets.ComplianceTaskInstanceModelViewSet, basename="compliancetaskinstance"
)

router.register(r"complianceaction", viewsets.ComplianceActionModelViewSet, basename="complianceaction")
router.register(r"complianceevent", viewsets.ComplianceEventModelViewSet, basename="complianceevent")

router.register(
    r"compliancetyperepresentation",
    viewsets.ComplianceTypeRepresentationViewSet,
    basename="compliancetyperepresentation",
)
router.register(r"compliancetype", viewsets.ComplianceTypeModelViewSet, basename="compliancetype")

router.register(
    r"reviewcompliancetaskrepresentation",
    viewsets.ReviewComplianceTaskRepresentationViewSet,
    basename="reviewcompliancetaskrepresentation",
)
router.register(r"reviewcompliancetask", viewsets.ReviewComplianceTaskModelViewSet, basename="reviewcompliancetask")


router.register(
    r"compliancetaskgrouprepresentation",
    viewsets.ComplianceTaskGroupRepresentationViewSet,
    basename="compliancetaskgrouprepresentation",
)
router.register(r"compliancetaskgroup", viewsets.ComplianceTaskGroupModelViewSet, basename="compliancetaskgroup")

# Subrouter for compliance type
compliance_type_router = WBCoreRouter()
compliance_type_router.register(
    r"complianceaction",
    viewsets.TypeComplianceActionModelViewSet,
    basename="type-complianceaction",
)
compliance_type_router.register(
    r"complianceevent",
    viewsets.TypeComplianceEventModelViewSet,
    basename="type-complianceevent",
)


# Subrouter for forms to be signed of a Compliance Form
compliance_form_router = WBCoreRouter()
compliance_form_router.register(
    r"signatures",
    viewsets.CFComplianceFormSignatureModelViewSet,
    basename="complianceform-signatures",
)
# Subrouter for the section of a Compliance Form
compliance_form_router.register(
    r"sections",
    viewsets.ComplianceFormSectionComplianceFormViewSet,
    basename="complianceform-sections",
)


# Subrouter for the rules of a section
section_router = WBCoreRouter()
section_router.register(
    r"rules",
    viewsets.ComplianceFormSectionRuleViewSet,
    basename="complianceformsection-rules",
)

section_router.register(
    r"signauturerules",
    viewsets.ComplianceFormSignatureSectionRuleViewSet,
    basename="complianceformsignaturesection-rules",
)


# Subrouter for the compliance task of a group
taskgroup_router = WBCoreRouter()
taskgroup_router.register(
    r"compliancetaskgroup",
    viewsets.ComplianceTaskComplianceTaskGroupModelViewSet,
    basename="compliancetaskgroup-compliancetask",
)

task_router = WBCoreRouter()
task_router.register(
    r"compliancetask",
    viewsets.ComplianceTaskInstanceComplianceTaskModelViewSet,
    basename="compliancetask-compliancetaskinstance",
)


# Subrouter for the compliance task of a review
review_router = WBCoreRouter()
review_router.register(
    r"compliancetasknogroup",
    viewsets.ComplianceTaskReviewNoGroupModelViewSet,
    basename="review-compliancetasknogroup",
)
review_router.register(
    r"compliancetaskinstancenogroup",
    viewsets.ComplianceTaskInstanceReviewNoGroupModelViewSet,
    basename="review-compliancetaskinstancenogroup",
)

# Subrouter for the compliance task of a group of  a review
review_group_router = WBCoreRouter()
review_group_router.register(
    r"compliancetaskgroup",
    viewsets.ComplianceTaskReviewGroupModelViewSet,
    basename="review-compliancetaskgroup",
)
review_group_router.register(
    r"compliancetaskinstancegroup",
    viewsets.ComplianceTaskInstanceReviewGroupModelViewSet,
    basename="review-compliancetaskinstancegroup",
)

# Risk Management url routing

router.register("riskcheckrepresentation", viewsets.RiskCheckRepresentationViewSet, basename="riskcheckrepresentation")
router.register("rulegrouprepresentation", viewsets.RuleGroupRepresentationViewSet, basename="rulegrouprepresentation")
router.register(
    "riskincidentrepresentation", viewsets.RiskIncidentRepresentationViewSet, basename="riskincidentrepresentation"
)
router.register(
    "riskincidenttyperepresentation",
    viewsets.RiskIncidentTypeRepresentationViewSet,
    basename="riskincidenttyperepresentation",
)
router.register(
    "checkedobjectincidentrelationshiprepresentation",
    viewsets.CheckedObjectIncidentRelationshipRepresentationViewSet,
    basename="checkedobjectincidentrelationshiprepresentation",
)
router.register(
    "rulechecked_objectrelationshiprepresentation",
    viewsets.RuleCheckedObjectRelationshipRepresentationViewSet,
    basename="rulechecked_objectrelationshiprepresentation",
)
router.register(
    "rulebackendrepresentation", viewsets.RuleBackendRepresentationViewSet, basename="rulebackendrepresentation"
)
router.register(
    "rulethresholdrepresentation", viewsets.RuleThresholdRepresentationViewSet, basename="rulethresholdrepresentation"
)
router.register("riskrulerepresentation", viewsets.RiskRuleRepresentationViewSet, basename="riskrulerepresentation")
router.register("riskincident", viewsets.RiskIncidentModelViewSet, basename="riskincident")
router.register(
    "checkedobjectincidentrelationship",
    viewsets.CheckedObjectIncidentRelationshipModelViewSet,
    basename="checkedobjectincidentrelationship",
)
router.register("riskcheck", viewsets.RiskCheckModelViewSet, basename="riskcheck")
router.register("riskrule", viewsets.RiskRuleModelViewSet, basename="riskrule")

rule_group_router = WBCoreRouter()
rule_group_router.register(
    r"incident",
    viewsets.RiskIncidentRiskRuleModelViewSet,
    basename="riskrule-incident",
)
rule_group_router.register(
    r"relationship",
    viewsets.RuleCheckedObjectRelationshipRiskRuleModelViewSet,
    basename="riskrule-relationship",
)
rule_group_router.register(
    r"threshold",
    viewsets.RuleThresholdRiskRuleModelViewSet,
    basename="riskrule-threshold",
)

incident_group_router = WBCoreRouter()
incident_group_router.register(
    r"relationship",
    viewsets.CheckedObjectIncidentRelationshipRiskRuleModelViewSet,
    basename="riskincident-relationship",
)

# Pandas ViewSet
router.register("compliancetaskmatrix", viewsets.ComplianceTaskMatrixPandasViewSet, basename="compliancetaskmatrix")
router.register(
    "riskmanagementincidenttable", viewsets.RiskManagementIncidentTableView, basename="riskmanagementincidenttable"
)

urlpatterns = [
    path("", include(router.urls)),
    path("riskrule/<int:rule_id>/", include(rule_group_router.urls)),
    path("riskincident/<int:incident_id>/", include(incident_group_router.urls)),
    path("complianceform/<int:compliance_form_id>/", include(compliance_form_router.urls)),
    path("section/<int:section_id>/", include(section_router.urls)),
    path("taskgroup/<int:group_id>/", include(taskgroup_router.urls)),
    path("task/<int:task_id>/", include(task_router.urls)),
    path("review/<int:review_id>/", include(review_router.urls)),
    path("review/<int:review_id>/group/<int:group_id>/", include(review_group_router.urls)),
    path("type/<int:type_id>/", include(compliance_type_router.urls)),
]
