from datetime import datetime

from django.contrib import admin
from django.contrib import messages
from django.contrib.admin import FieldListFilter
from django.db import models
from django.db.models import F
from django.utils.formats import localize
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportMixin
from import_export.results import RowResult

from ..admin import ChoiceWidget
from ..admin import FullFilenameExportAdminMixin
from ..admin import SmartModelResource
from ..gettext import _
from .models import AbstractTask
from .models import QueueState
from .models import ResultType


class AbstractTaskResource(SmartModelResource):
    class Meta:
        use_bulk = True
        clean_model_instances = True
        skip_unchanged = True
        exclude = [
            "id",
            "created_at",
            "updated_at",
            "queue_priority",
            "queue_updated_at",
            "result_details",
        ]
        widgets = {
            "queue_state": ChoiceWidget(choice_class=QueueState),
            "result_type": ChoiceWidget(choice_class=ResultType),
        }

    now: datetime
    seen_instances: set

    def before_import(self, *args, **kwargs):
        self.seen_instances = set()

    def import_instance(self, obj, data, **kwargs):
        super().import_instance(obj, data, **kwargs)
        obj.queue_state = QueueState.PENDING

    def after_import_row(self, row, row_result: RowResult, row_number=None, **kwargs):
        if row_result.object_id:
            self.seen_instances.add(row_result.object_id)

    def skip_row(self, instance: AbstractTask, original: AbstractTask, *args, **kwargs):
        if instance.pk in self.seen_instances:
            return True
        if instance.queue_state == original.queue_state:
            return True


class CompletedResultTypeFilter(FieldListFilter):
    def expected_parameters(self):
        return [
            "result_type__exact",
            "result_type__in",
        ]

    def get_facet_counts(self, pk_attname, filtered_qs):
        return {
            "PENDING": models.Count(pk_attname, filter=models.Q(result_type__exact=ResultType.PENDING)),
            "COMPLETED": models.Count(pk_attname, filter=models.Q(result_type__in=[ResultType.SUCCESS, ResultType.ABSENT])),
            "SUCCESS": models.Count(pk_attname, filter=models.Q(result_type__exact=ResultType.SUCCESS)),
            "ABSENT": models.Count(pk_attname, filter=models.Q(result_type__exact=ResultType.ABSENT)),
            "ERROR": models.Count(pk_attname, filter=models.Q(result_type__exact=ResultType.ERROR)),
        }

    def choices(self, changelist):
        add_facets = changelist.add_facets
        facet_counts = self.get_facet_queryset(changelist) if add_facets else {}
        return [
            {
                "selected": not self.used_parameters,
                "query_string": changelist.get_query_string(remove=self.expected_parameters()),
                "display": _("All"),
            },
            {
                "selected": self.used_parameters.get("result_type__exact") == [str(ResultType.PENDING)],
                "query_string": changelist.get_query_string({"result_type__exact": ResultType.PENDING}, remove=self.expected_parameters()),
                "display": f"PENDING ({facet_counts.get('PENDING', '?')})" if add_facets else "PENDING",
            },
            {
                "selected": self.used_parameters.get("result_type__in") == [[str(ResultType.SUCCESS), str(ResultType.ABSENT)]],
                "query_string": changelist.get_query_string(
                    {"result_type__in": f"{ResultType.SUCCESS},{ResultType.ABSENT}"}, remove=self.expected_parameters()
                ),
                "display": f"COMPLETED ({facet_counts.get('COMPLETED', '?')})" if add_facets else "COMPLETED",
            },
            {
                "selected": self.used_parameters.get("result_type__exact") == [str(ResultType.SUCCESS)],
                "query_string": changelist.get_query_string({"result_type__exact": ResultType.SUCCESS}, remove=self.expected_parameters()),
                "display": f"SUCCESS ({facet_counts.get('SUCCESS', '?')})" if add_facets else "SUCCESS",
            },
            {
                "selected": self.used_parameters.get("result_type__exact") == [str(ResultType.ABSENT)],
                "query_string": changelist.get_query_string({"result_type__exact": ResultType.ABSENT}, remove=self.expected_parameters()),
                "display": f"ABSENT ({facet_counts.get('ABSENT', '?')})" if add_facets else "ABSENT",
            },
            {
                "selected": self.used_parameters.get("result_type__exact") == [str(ResultType.ERROR)],
                "query_string": changelist.get_query_string({"result_type__exact": ResultType.ERROR}, remove=self.expected_parameters()),
                "display": f"ERROR ({facet_counts.get('ERROR', '?')})" if add_facets else "ERROR",
            },
        ]


class AbstractTaskAdmin(FullFilenameExportAdminMixin, ImportExportMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "details",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "request_count",
        "request_updated_at",
        "queue_priority",
        "queue_updated_at",
        "result_details",
        "get_result_details_display",
        "result_type",
        "result_updated_at",
    )
    show_facets = admin.ShowFacets.ALWAYS if hasattr(admin, "ShowFacets") else False
    list_filter = [
        "queue_state",
        ("result_type", CompletedResultTypeFilter),
        "result_provider",
    ]
    ordering = [
        F("result_updated_at").desc(nulls_last=True),
        F("queue_updated_at").desc(nulls_last=True),
        F("request_updated_at").desc(nulls_last=True),
        "-id",
    ]
    actions = [
        "reschedule_action",
    ]

    @admin.action(description="Reschedule (change state to pending)", permissions=["change"])
    def reschedule_action(self, request, queryset):
        count = queryset.update(queue_state=QueueState.PENDING)
        self.message_user(request, f"Rescheduled {count} tasks.", messages.SUCCESS)

    @admin.display(description="details")
    def details(self, obj: AbstractTask):
        result_details = []
        if obj.result_updated_at:
            result_details.append(f"<br>@{localize(obj.result_updated_at, use_l10n=True)}")
        if obj.result_provider:
            result_details.append(
                f"<br><em>{obj.get_result_provider_display() if hasattr(obj, 'get_result_provider_display') else obj.result_provider}</em>"
            )
        if obj.result_details:
            result_details.append(f"<br>{obj.result_details.splitlines()[0]}")
        queue_details = f"<br>@{localize(obj.queue_updated_at)}" if obj.queue_state else ""
        request_details = f"<br>@{localize(obj.request_updated_at)}" if obj.request_updated_at else ""
        return mark_safe(
            "<table><tbody>"
            f"<tr bgcolor=transparent><th>requests</th><td>{obj.request_count}{request_details}</td></tr>"
            f"<tr bgcolor=transparent><th>queue</th><td><strong>{obj.get_queue_state_display()}</strong>{queue_details}</td></tr>"
            f"<tr bgcolor=transparent><th>result</th><td><strong>{obj.get_result_type_display()}</strong>{''.join(result_details)}</td></tr>"
            f"</tbody></table>"
        )

    @admin.display(description="result details")
    def get_result_details_display(self, obj):
        return format_html("<pre>{}</pre>", obj.result_details)

    def has_add_permission(self, request):
        return False
