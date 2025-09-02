from io import StringIO

import pandas as pd
from django.contrib import admin
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from reversion.errors import RevertError
from wbcore.admin import CsvImportForm, ExportCsvMixin, ImportCsvMixin

from ..models.review import (
    Review,
    ReviewAnswer,
    ReviewGroup,
    ReviewQuestion,
    ReviewQuestionCategory,
)


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


@admin.register(ReviewGroup)
class ReviewGroupAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "year",
        "type",
        "from_date",
        "to_date",
        "review_deadline",
        "review",
        "auto_apply_deadline",
        "status",
        "reviewee",
        "reviewer",
        "moderator",
        "review_group",
        "is_template",
    ]


@admin.register(ReviewQuestionCategory)
class ReviewQuestionCategoryAdmin(ExportCsvMixin, CustomImportCsvMixin, admin.ModelAdmin):
    list_display = ["name", "order", "weight"]

    def manipulate_df(self, df):
        return df

    def get_import_fields(self):
        return ["name", "order", "weight"]

    def process_model(self, model):
        if category_name := model.get("name"):
            _, created = self.model.objects.update_or_create(
                name=category_name,
                defaults={
                    "order": model.get("order"),
                    "weight": model.get("weight"),
                },
            )
            return 1 if created else 0
        return 0


@admin.register(ReviewQuestion)
class ReviewQuestion(ExportCsvMixin, CustomImportCsvMixin, admin.ModelAdmin):
    list_display = [
        "id",
        "question",
        "review",
        "category",
        "mandatory",
        "answer_type",
        "for_reviewee",
        "for_reviewer",
        "for_department_peers",
        "for_company_peers",
        "order",
        "weight",
    ]

    def manipulate_df(self, df):
        df["review"] = df["review_id"].apply(lambda x: Review.objects.get(id=x))
        df["category"] = df["category_name"].apply(lambda x: ReviewQuestionCategory.objects.filter(name=x).first())
        return df

    def get_import_fields(self):
        return ["review_id", "category_name", "answer_type", "order", "weight", "question"]

    def process_model(self, model):
        if review := model.get("review"):
            _, created = self.model.objects.update_or_create(
                review=review,
                question=model.get("question"),
                defaults={
                    "category": model.get("category"),
                    "answer_type": model.get("answer_type"),
                    "order": model.get("order"),
                    "weight": model.get("weight"),
                },
            )
            return 1 if created else 0
        return 0


@admin.register(ReviewAnswer)
class ReviewAnswerAdmin(admin.ModelAdmin):
    list_display = ["question", "answered_by", "answer_number", "answered_anonymized"]
