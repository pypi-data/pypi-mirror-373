from django.db.models import Q
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy, pgettext
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.contrib.directory.models import Person
from wbcore.contrib.directory.serializers import PersonRepresentationSerializer
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)

from wbhuman_resources.models import Review
from wbhuman_resources.serializers import ReviewModelSerializer


class ReviewButtonConfig(bt.ButtonViewConfig):
    def get_custom_buttons(self):
        if not self.view.kwargs.get("pk", None):
            return {
                bt.WidgetButton(
                    endpoint=reverse("wbhuman_resources:reviewprogress-list", args=[], request=self.request),
                    label=_("Progress"),
                    icon=WBIcon.CHART_BARS_HORIZONTAL.icon,
                )
            }
        return {}

    def get_custom_list_instance_buttons(self):
        return self.get_custom_instance_buttons()

    def get_custom_instance_buttons(self):
        BUTTONS = [
            bt.WidgetButton(key="progress", label=_("Progress"), icon=WBIcon.CHART_BARS_HORIZONTAL.icon),
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbhuman_resources:review",),
                key="completelyfilledreviewee",
                action_label=_("Sending Review"),
                title=_("Finish and Send Review"),
                label=_("Finish and Send Review"),
                icon=WBIcon.CONFIRM.icon,
                description_fields=_(
                    "<p>Have you finished filling in the review? </p> <p><span style='color:red'>This action is not reversible</span></p>"
                ),
                confirm_config=bt.ButtonConfig(label=_("Confirm")),
                cancel_config=bt.ButtonConfig(label=pgettext("Non-Transition button", "Cancel")),
            ),
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbhuman_resources:review",),
                key="completelyfilledreviewer",
                action_label=_("Sending Review"),
                title=_("Finish and Send Review"),
                label=_("Finish and Send Review"),
                icon=WBIcon.CONFIRM.icon,
                description_fields=_(
                    "<p>Have you finished filling in the review? </p> <p><span style='color:red'>This action is not reversible</span></p>"
                ),
                confirm_config=bt.ButtonConfig(label=_("Confirm")),
                cancel_config=bt.ButtonConfig(label=pgettext("Non-Transition button", "Cancel")),
            ),
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbhuman_resources:review",),
                key="signaturereviewee",
                action_label=_("Signing"),
                title=_("Sign"),
                label=_("Sign"),
                icon=WBIcon.CONFIRM.icon,
                description_fields=_(
                    "<p>Do you want to sign the review? </p> <p><span style='color:red'>This action is not reversible</span></p>"
                ),
                confirm_config=bt.ButtonConfig(label=_("Confirm")),
                cancel_config=bt.ButtonConfig(label=pgettext("Non-Transition button", "Cancel")),
                instance_display=create_simple_display([["feedback_reviewee"]]),
            ),
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbhuman_resources:review",),
                key="signaturereviewer",
                action_label=_("Signing"),
                title=_("Sign"),
                label=_("Sign"),
                icon=WBIcon.CONFIRM.icon,
                description_fields=_(
                    "<p>Do you want to sign the review? </p> <p><span style='color:red'>This action is not reversible</span></p>"
                ),
                confirm_config=bt.ButtonConfig(label=_("Confirm")),
                cancel_config=bt.ButtonConfig(label=pgettext("Non-Transition button", "Cancel")),
                instance_display=create_simple_display([["feedback_reviewer"]]),
            ),
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbhuman_resources:review",),
                key="generate_pdf",
                action_label=_("Sending Report"),
                title=_("Generate and Send Report"),
                label=_("Generate and Send Report"),
                icon=WBIcon.SEND.icon,
                confirm_config=bt.ButtonConfig(label=_("Confirm")),
                cancel_config=bt.ButtonConfig(label=pgettext("Non-Transition button", "Cancel")),
            ),
        ]

        if self.view.kwargs.get("pk", None):
            review = self.view.get_object()

            if review.is_template and review.review_group and review.moderator == self.view.request.user.profile:

                class GenerateReviewModelSerializer(ReviewModelSerializer):
                    employees = wb_serializers.PrimaryKeyRelatedField(
                        queryset=Person.objects.all(),
                        label=gettext_lazy("Employees"),
                        many=True,
                        default=[_employee for _employee in review.review_group.employees.all()],
                    )
                    _employees = PersonRepresentationSerializer(many=True, source="employees")
                    include_kpi = wb_serializers.BooleanField(default=False, label=gettext_lazy("Include KPI"))

                    class Meta:
                        model = Review
                        fields = (
                            "from_date",
                            "to_date",
                            "review_deadline",
                            "auto_apply_deadline",
                            "employees",
                            "_employees",
                            "include_kpi",
                        )

                BUTTONS.append(
                    bt.ActionButton(
                        method=RequestType.PATCH,
                        identifiers=("wbhuman_resources:review",),
                        key="generate",
                        action_label=_("Generating Review"),
                        title=_("Generate Review from Template"),
                        label=_("Generate Review"),
                        icon=WBIcon.DATA_GRID.icon,
                        description_fields=_(
                            "<p>Generate report from :  <p> <b><span>{{computed_str}} </span></b> </p>"
                        ),
                        confirm_config=bt.ButtonConfig(label=_("Confirm")),
                        cancel_config=bt.ButtonConfig(label=pgettext("Non-Transition button", "Cancel")),
                        serializer=GenerateReviewModelSerializer,
                        instance_display=create_simple_display(
                            [
                                ["from_date", "from_date"],
                                ["to_date", "to_date"],
                                ["review_deadline", "review_deadline"],
                                ["auto_apply_deadline", "include_kpi"],
                                ["employees", "employees"],
                            ]
                        ),
                    )
                )
        return {*BUTTONS}


class ReviewGroupButtonConfig(bt.ButtonViewConfig):
    def get_custom_instance_buttons(self):
        class ReviewCounterSerializer(wb_serializers.Serializer):
            counter = wb_serializers.IntegerField(
                read_only=True,
                label=gettext_lazy("Number of reviews found"),
                default=Review.objects.filter(
                    Q(review_group=self.view.get_object())
                    & Q(status=Review.Status.PREPARATION_OF_REVIEW)
                    & Q(moderator=self.view.request.user.profile)
                    & Q(is_template=False)
                ).count(),
            )

        return {
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbhuman_resources:reviewgroup",),
                key="submitreviews",
                action_label=_("Submitting Reviews from Stage 1 to Stage 2"),
                title=_("Submit Reviews from Stage 1 to Stage 2"),
                label=_("Submit Reviews"),
                icon=WBIcon.SEND.icon,
                description_fields=_(
                    "<p>Submit Reviews</p> <p>Group : <b>{{name}}</b><p> From : <b>Stage 1: Preparation of review</b></p> <p> To : <b>Stage 2: Fill in review</b></p>  <p style='background-color:skyblue;border-radius:2px;padding:5px;'> <b><span style=color:black> You are going to submit the reviews that are in stage 1 to stage 2 </span></b> </p>"
                ),
                confirm_config=bt.ButtonConfig(label=_("Confirm")),
                cancel_config=bt.ButtonConfig(label=pgettext("Non-Transition button", "Cancel")),
                serializer=ReviewCounterSerializer,
                instance_display=create_simple_display([["counter"]]),
            ),
        }
