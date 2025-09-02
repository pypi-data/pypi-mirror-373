import pandas as pd
from django.contrib import admin
from reversion_compare.admin import CompareVersionAdmin
from wbcore.admin import ExportCsvMixin

from wbcompliance.models import (
    ComplianceAction,
    ComplianceEvent,
    ComplianceTask,
    ComplianceTaskGroup,
    ComplianceTaskInstance,
    ComplianceType,
    ReviewComplianceTask,
)

from .utils import CustomImportCsvMixin


@admin.register(ComplianceTaskGroup)
class ComplianceTaskGroupAdmin(ExportCsvMixin, CustomImportCsvMixin, CompareVersionAdmin):
    list_display = ["name", "order"]

    def manipulate_df(self, df):
        df["name"] = df["name"].fillna("")
        return df

    def get_import_fields(self):
        return [
            "name",
        ]

    def process_model(self, model):
        if model.get("name"):
            _, created = self.model.objects.get_or_create(name=model.get("name"))
            return 1 if created else 0
        return 0


@admin.register(ComplianceTask)
class ComplianceTaskAdmin(ExportCsvMixin, CustomImportCsvMixin, CompareVersionAdmin):
    list_display = ["title", "occurrence", "active", "risk_level", "group", "type"]

    def manipulate_df(self, df):
        df["type"] = df["type_name"].apply(lambda x: ComplianceType.objects.filter(name__exact=x).first())
        df["group"] = df.apply(
            lambda x: ComplianceTaskGroup.objects.filter(name__exact=x["group_name"]).first(), axis=1
        )
        return df

    def get_import_fields(self):
        return ["type_name", "group_name", "occurrence", "title", "description"]

    def process_model(self, model):
        if model.get("title"):
            _, created = self.model.objects.update_or_create(
                title=model.get("title"),
                defaults={
                    "type": model.get("type"),
                    "group": model.get("group"),
                    "occurrence": model.get("occurrence"),
                    # 'description': model.get('description')
                },
            )
            return 1 if created else 0
        return 0


@admin.register(ComplianceTaskInstance)
class ComplianceTaskInstanceAdmin(ExportCsvMixin, CustomImportCsvMixin, CompareVersionAdmin):
    list_display = ["task", "occured", "status"]

    def manipulate_df(self, df):
        df["task"] = df.apply(lambda x: ComplianceTask.objects.filter(title__exact=x["task_name"]).first(), axis=1)
        df["occured"] = pd.to_datetime(df["occured"])
        return df

    def get_import_fields(self):
        return ["task_name", "occured", "status", "text"]

    def process_model(self, model):
        if (task := model.get("task")) and (occured := model.get("occured")):
            obj, created = self.model.objects.update_or_create(
                task=task,
                occured=occured,
                defaults={
                    "status": model.get("status"),
                    "text": model.get("text"),
                },
            )
            if created:
                obj.occured = occured
                obj.save()

            return 1 if created else 0
        return 0


@admin.register(ComplianceAction)
class ComplianceActionAdmin(CompareVersionAdmin):
    search_fields = ["title"]
    list_display = [
        "title",
        "deadline",
        "progress",
        "status",
        "type",
        "creator",
        "created",
        "changer",
        "last_modified",
    ]


@admin.register(ComplianceEvent)
class ComplianceEventAdmin(CompareVersionAdmin):
    search_fields = ["title"]
    list_display = ["title", "type", "level", "type", "confidential", "creator", "created", "changer", "last_modified"]


@admin.register(ReviewComplianceTask)
class ReviewComplianceTaskAdmin(CompareVersionAdmin):
    list_display = [
        "id",
        "year",
        "title",
        "from_date",
        "to_date",
        "status",
        "occurrence",
        "is_instance",
        "changer",
        "changed",
        "review_task",
        "occured",
    ]
    search_fields = ["title"]
