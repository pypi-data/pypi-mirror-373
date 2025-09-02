from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Any, Dict, Generator, Iterable, Optional

from django.contrib.contenttypes.models import ContentType
from django.db import models
from wbcore import serializers as wb_serializers

if TYPE_CHECKING:
    from wbcompliance.models.risk_management.incidents import RiskIncidentType


@dataclass(frozen=True)
class IncidentResult:
    breached_object: models.Model | None
    breached_object_repr: str
    breached_value: str | None
    report_details: dict[str, Any]
    severity: "RiskIncidentType"


class AbstractRuleBackend:
    OBJECT_FIELD_NAME = "evaluated_object"
    evaluated_object: Any
    evaluation_date: date
    parameters: dict[str, Any]

    def __init__(
        self,
        evaluation_date: date,
        evaluated_object: Any,
        json_parameters: Optional[Dict[str, Any]] = None,
        thresholds: Optional[
            Iterable
        ] = None,  # TODO refactor threshold to be a dataclass (DTO) to remove indirect dependency to the module
        **kwargs,
    ):
        if not json_parameters:
            json_parameters = {}
        self.evaluation_date = evaluation_date
        setattr(self, self.OBJECT_FIELD_NAME, evaluated_object)
        self.thresholds = thresholds if thresholds else []
        self.parameters = self._deserialize_parameters(json_parameters)

        for k, v in self.parameters.items():
            setattr(self, k, v)

    @classmethod
    def get_all_active_relationships(cls) -> Iterable:
        raise NotImplementedError()

    @classmethod
    def get_serializer_class(cls) -> wb_serializers.Serializer:
        """
        Return the serializer to deserialize the parameters given as json
        Returns:
            A serializer class
        Raises:
            NotImplementedError
        """
        raise NotImplementedError()

    @classmethod
    def _deserialize_parameters(cls, json_parameters) -> Dict[str, Any]:
        """
        The parameters are stored in the rule as a json field.

        E.g. As such, model are stored with their id.

        This allows for the implementing backend to override the default deserialization behavior
        Args:
            json_parameters: The serialized dictionary

        Returns:
            The deserializer dictionary. Default to returning the json parameters untouched
        """
        # If parameters are not empty, we expect the backend to define `get_serializer_class. This will crash otherwise
        serializer = cls.get_serializer_class()(data=json_parameters)
        if serializer.is_valid():
            return serializer.validated_data
        else:
            raise ValueError(serializer.errors)

    @classmethod
    def get_allowed_content_type(cls) -> "ContentType":
        """
        This function is called upon backend registration in order to determine the allowed checked_object content type

        Returns:
            The allowed content type

        Raises:
            NotImplementedError
        """
        raise NotImplementedError()

    def _build_dto_args(self):
        """
        Can be overrided to define what the default DataTransferObject is going to be
        It defaults to calling _build_dto on the evaluated object
        Returns:
            An object holding the DTO representation
        """
        if hasattr(self.evaluated_object, "_build_dto"):
            return self.evaluated_object._build_dto(self.evaluation_date)
        return tuple()

    def _process_dto(self, *dtos) -> Generator[IncidentResult, None, None]:
        """
        Check the rule against the instantiated backend given the DTO

        Returns:
            yield the breach object, its string representation, the incident report and the severity as IncidentResult

        Raises:
            NotImplementedError
        """
        raise NotImplementedError()

    def check_rule(self, *dto_args, **kwargs) -> Generator[IncidentResult, None, None]:
        """
        Build and Check the rule against the instantiated backend given its attributes

        Returns:
            yield the breach object, its string representation, the incident report and the severity as IncidentResult
        """
        if not dto_args:
            # We build the data transfer object if it is not provided.
            dto_args = self._build_dto_args()
        if any(dto_args):
            yield from self._process_dto(*dto_args, **kwargs)

    def is_passive_evaluation_valid(self) -> bool:
        """
        Determine if the instantiated backend can be evaluated given its attributes

        Returns:
            True if the backend rule can be evaluated
        """
        return True
