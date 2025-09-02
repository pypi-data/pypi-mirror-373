from io import StringIO

import pandas as pd
from django.contrib import admin
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from reversion.errors import RevertError
from wbcore.admin import CsvImportForm, ImportCsvMixin

from ..models.absence import AbsenceRequest, AbsenceRequestPeriods, AbsenceRequestType


class CustomImportCsvMixin(ImportCsvMixin):
    def _import_csv(self, request, _sep=";"):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]

            str_text = ""
            for line in csv_file:
                str_text = str_text + line.decode()
            # Import csv as df
            df = pd.read_csv(StringIO(str_text), sep=_sep)
            # Sanitize dataframe
            df = df.where(pd.notnull(df), None)
            df = df.drop(df.columns.difference(self.get_import_fields()), axis=1)

            # Overide this function if there is foreign key ids in the dataframe
            df = self.manipulate_df(df)
            errors = 0
            revert_errors = 0
            nb_added = 0
            for model in df.to_dict("records"):
                # by default, process the modela as a create request. Can be override to change the behavior
                try:
                    nb_added += self.process_model(model)
                # https://django-reversion.readthedocs.io/en/stable/common-problems.html
                except RevertError:
                    revert_errors += 1
                except Exception as e:
                    print(e)  # noqa: T201
                    errors += 1
            self.message_user(
                request,
                _(
                    "Your CSV file has been imported : {} imported ({} added, {} updated), {} errors, {} revert errors found due to failure to restore old versions"
                ).format(
                    df.shape[0] - errors - revert_errors,
                    nb_added,
                    df.shape[0] - errors - revert_errors - nb_added,
                    errors,
                    revert_errors,
                ),
            )
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "wbcore/admin/csv_form.html", payload)


@admin.register(AbsenceRequestType)
class AbsenceRequestTypeAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "is_vacation",
        "is_timeoff",
        "is_extensible",
        "auto_approve",
        "days_in_advance",
    ]

    autocomplete_fields = ["crossborder_countries", "extra_notify_groups"]


class AbsenceRequestPeriodsInline(admin.TabularInline):
    model = AbsenceRequestPeriods
    ordering = ("timespan__startswith",)
    extra = 0
    raw_id_fields = ["balance", "request"]


@admin.register(AbsenceRequest)
class AbsenceRequestAdmin(admin.ModelAdmin):
    list_display = ["status", "employee", "period", "type", "_total_hours", "_total_vacation_hours"]

    fieldsets = (
        (
            "",
            {
                "fields": (
                    ("status", "type"),
                    ("period", "employee"),
                    "attachment",
                )
            },
        ),
        (
            _("Notes"),
            {"fields": ("notes", "reason")},
        ),
    )
    inlines = (AbsenceRequestPeriodsInline,)
    autocomplete_fields = ["employee"]
    list_filter = ["type__is_vacation"]

    def _total_hours(self, obj):
        return obj._total_hours

    def _total_vacation_hours(self, obj):
        return obj._total_vacation_hours

    #
    # def get_queryset(self, request):
    #     return super().get_queryset().
