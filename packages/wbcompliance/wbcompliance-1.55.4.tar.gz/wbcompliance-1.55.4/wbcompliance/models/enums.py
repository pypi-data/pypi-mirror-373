from django.db import models
from wbcore.contrib.color.enums import WBColor


class IncidentSeverity(models.TextChoices):
    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"

    @classmethod
    def get_color_map(cls) -> list:
        colors = [WBColor.GREEN_LIGHT.value, WBColor.YELLOW_LIGHT.value, WBColor.RED_LIGHT.value]
        return [choice for choice in zip(cls, colors)]
