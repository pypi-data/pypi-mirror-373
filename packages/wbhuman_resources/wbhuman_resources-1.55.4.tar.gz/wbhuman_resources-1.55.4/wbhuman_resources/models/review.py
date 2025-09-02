from datetime import datetime, timedelta
from decimal import Decimal
from typing import TypeVar

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import (
    BooleanField,
    Case,
    F,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.loader import get_template
from django.utils import timezone
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from slugify import slugify
from wbcore.contrib.color.enums import WBColor
from wbcore.contrib.directory.models import Person
from wbcore.contrib.documents.models import Document, DocumentType
from wbcore.contrib.icons import WBIcon
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.enums import RequestType
from wbcore.markdown.utils import custom_url_fetcher
from wbcore.metadata.configs.buttons import ActionButton, ButtonDefaultColor
from wbcore.models import WBModel
from wbcore.models.fields import YearField
from wbcore.models.orderable import OrderableModel
from wbcore.utils.models import CloneMixin, ComplexToStringMixin
from weasyprint import HTML

from wbhuman_resources.models.employee import get_main_company
from wbhuman_resources.models.kpi import Evaluation

SelfReview = TypeVar("SelfReview", bound="Review")
User = get_user_model()


def can_trigger_review(instance, user):
    return user.profile == instance.moderator and not instance.is_template and instance.reviewee and instance.reviewer


def can_validate_review(instance, user):
    return can_trigger_review(instance, user) and instance.signed_reviewee and instance.signed_reviewer


class ReviewGroup(WBModel):
    class Meta:
        verbose_name = _("Review Group")
        verbose_name_plural = _("Review Groups")

    name = models.CharField(max_length=255, verbose_name=_("Name"))
    employees = models.ManyToManyField("directory.Person", related_name="reviewgroups", blank=True)

    def __str__(self):
        return f"{self.name}"

    @classmethod
    def get_endpoint_basename(cls):
        return "wbhuman_resources:reviewgroup"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbhuman_resources:reviewgrouprepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{name}}"


class Review(CloneMixin, ComplexToStringMixin, WBModel):
    class Status(models.TextChoices):
        PREPARATION_OF_REVIEW = "PREPARATION_OF_REVIEW", _("Stage 1: Preparation of review")
        FILL_IN_REVIEW = "FILL_IN_REVIEW", _("Stage 2: Fill in review")
        REVIEW = "REVIEW", _("Stage 3: Review")
        EVALUATION = "EVALUATION", _("Stage 4: Evalutation")
        VALIDATION = "VALIDATION", _("Stage 5: Validation")

        @classmethod
        def get_color_map(cls):
            colors = [
                WBColor.BLUE_LIGHT.value,
                "rgb(230,230,250)",
                WBColor.YELLOW_LIGHT.value,
                WBColor.GREEN_LIGHT.value,
                WBColor.GREEN_DARK.value,
            ]
            return [choice for choice in zip(cls, colors)]

    class Type(models.TextChoices):
        ANNUAL = "ANNUAL", _("Annual")
        INTERMEDIARY = "INTERMEDIARY", _("Intermediary")

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        permissions = [
            ("administrate_review", "Can Administrate Reviews"),
        ]

        notification_types = [
            create_notification_type(
                code="wbhuman_resources.review.notify",
                title="Review Notification",
                help_text="Notifies you when a review has been submitted",
            )
        ]

    from_date = models.DateField(null=True, blank=True, verbose_name=_("From"))
    to_date = models.DateField(null=True, blank=True, verbose_name=_("To"))
    review_deadline = models.DateField(null=True, blank=True, verbose_name=_("Deadline"))
    review = models.DateTimeField(null=True, blank=True, verbose_name=_("Review Date"))
    auto_apply_deadline = models.BooleanField(default=True, verbose_name=_("Auto Apply Deadline"))
    year = YearField(null=True, blank=True, verbose_name=_("Year"))
    type = models.CharField(max_length=32, choices=Type.choices, default=Type.ANNUAL, verbose_name=_("Type"))
    status = FSMField(
        default=Status.PREPARATION_OF_REVIEW,
        choices=Status.choices,
        verbose_name=_("Status"),
        help_text=_("Indicates one of the four stages defined by the workflow"),
    )

    reviewee = models.ForeignKey(
        to="directory.Person",
        null=True,
        blank=True,
        related_name="reviewee_reviews",
        on_delete=models.deletion.SET_NULL,
        verbose_name=_("Reviewee"),
    )
    reviewer = models.ForeignKey(
        to="directory.Person",
        null=True,
        blank=True,
        related_name="reviewer_reviews",
        on_delete=models.deletion.SET_NULL,
        verbose_name=_("Reviewer"),
    )

    moderator = models.ForeignKey(
        to="directory.Person",
        null=True,
        blank=True,
        related_name="moderator_reviews",
        on_delete=models.deletion.SET_NULL,
    )

    review_group = models.ForeignKey(
        to="wbhuman_resources.ReviewGroup",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="review_related",
        verbose_name=_("Group"),
    )

    is_template = models.BooleanField(default=False)
    feedback_reviewee = models.TextField(default="", blank=True, verbose_name=_("Feedback Reviewee"))
    feedback_reviewer = models.TextField(default="", blank=True, verbose_name=_("Feedback Reviewer"))

    signed_reviewee = models.DateTimeField(null=True, blank=True, verbose_name=_("Date of reviewee's signature"))
    signed_reviewer = models.DateTimeField(null=True, blank=True, verbose_name=_("Date of reviewer's signature"))

    completely_filled_reviewee = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Completely Filled Out Reviewee")
    )
    completely_filled_reviewer = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Completely Filled Out Reviewer")
    )

    changed = models.DateTimeField(auto_now=True, null=True, blank=True)

    def compute_str(self) -> str:
        _str = ""
        if self.is_template:
            _str += (
                _("{group} [Template]").format(group=str(self.review_group)) if self.review_group else _("[Template]")
            )
        else:
            _str += (
                _("{reviewee}'s Review").format(reviewee=self.reviewee.computed_str) if self.reviewee else _("Review")
            )
        if self.from_date and self.to_date:
            _str += f" - ({self.from_date} - {self.to_date})"
        elif self.year:
            _str += f" - ({self.year})"
        return _str

    def __str__(self):
        return self.computed_str

    def save(self, *args, **kwargs):
        if self.reviewee and (employee := getattr(self.reviewee, "human_resources", None)) and not self.reviewer:
            self.reviewer = next(employee.get_managers(only_direct_manager=True), None)
        self.computed_str = self.compute_str()
        super().save(*args, **kwargs)

    @property
    def is_cloneable(self) -> bool:
        """
        Property used by the CloneMixin to disable the instance cloning functionality from the view
        """
        return self.is_template

    def _clone(self, **kwargs) -> SelfReview:
        """
        Create new row in database with the same data as original instance have.
        We need to clone also the related objects and set correct foreign key value
        """
        object_copy = Review.objects.get(id=self.id)
        object_copy.id = None
        object_copy.save()
        for related_object in self.questions.all():
            related_object.review = object_copy
            related_object.id = None
            related_object.save()
        return object_copy

    @classmethod
    def get_administrators(cls) -> QuerySet[User]:
        return (
            get_user_model()
            .objects.filter(
                Q(groups__permissions__codename="administrate_review")
                | Q(user_permissions__codename="administrate_review")
            )
            .distinct()
        )

    @transition(
        field=status,
        source=Status.PREPARATION_OF_REVIEW,
        target=Status.FILL_IN_REVIEW,
        permission=can_trigger_review,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbhuman_resources:review",),
                icon=WBIcon.SEND.icon,
                key="submit",
                label=_("Submit"),
                action_label=_("Stage 2: Fill in review"),
                description_fields=_(
                    "<p>Status: <b>Stage 1: Preparation of review</b></p> <p>Reviewee: <b>{{_reviewee.computed_str}}</b></p>  <p>Reviewer: <b>{{_reviewer.computed_str}}</b></p>  <p>From: <b>{{from_date}}</b></p> <p>To: <b>{{to_date}}</b></p> <p>Deadline: <b>{{review_deadline}}</b></p>  <p>Do you want to submit this review to <b>Stage 2: Fill in review?</b></p>"
                ),
            )
        },
    )
    def submit(self, by=None, description=None, **kwargs):
        submit_review.delay(self.id)

    @transition(
        field=status,
        source=Status.FILL_IN_REVIEW,
        target=Status.REVIEW,
        permission=can_trigger_review,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbhuman_resources:review",),
                icon=WBIcon.SEND.icon,
                key="finalize",
                label=_("Finalize"),
                action_label=_("Stage 3: Review"),
                description_fields=_(
                    "<p>Status: <b>Stage 2: Fill in review</b></p> <p>Reviewee: <b>{{_reviewee.computed_str}}</b></p>  <p>Reviewer: <b>{{_reviewer.computed_str}}</b></p>  <p>From: <b>{{from_date}}</b></p> <p>To: <b>{{to_date}}</b></p> <p>Deadline: <b>{{review_deadline}}</b></p>  <p>Do you want to send this review to <b>Stage 3: Review?</b></p>"
                ),
            )
        },
    )
    def finalize(self, by=None, description=None, **kwargs):
        if not self.review_deadline:
            self.review_deadline = datetime.now().date()
        finalize_review.delay(self.id)
        if not by:
            self.send_review_notification(
                title=gettext("Stage 3: Review - {self}").format(self=str(self)),
                message=gettext("{self} has moved to stage 3: Review. You can now organize the evaluation").format(
                    self=str(self)
                ),
                recipient=self.moderator.user_account,
                message_alert_deadline=False,
            )

    @transition(
        field=status,
        source=Status.REVIEW,
        target=Status.FILL_IN_REVIEW,
        permission=can_trigger_review,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbhuman_resources:review",),
                icon=WBIcon.EDIT.icon,
                key="undo",
                label=_("Undo"),
                action_label=_("Stage 2: Fill in review"),
                description_fields=_(
                    "<p>Status: <b>Stage 3: Review</b></p> <p>Reviewee: <b>{{_reviewee.computed_str}}</b></p>  <p>Reviewer: <b>{{_reviewer.computed_str}}</b></p>  <p>From: <b>{{from_date}}</b></p> <p>To: <b>{{to_date}}</b></p> <p>Deadline: <b>{{review_deadline}}</b></p>  <p>Do you want to send this review to <b>Stage 2: Fill in review?</b></p>"
                ),
            )
        },
    )
    def undo(self, by=None, description=None, **kwargs):
        if self.review_deadline <= datetime.now().date():
            self.review_deadline = datetime.now().date() + timedelta(days=1)

    @transition(
        field=status,
        source=Status.REVIEW,
        target=Status.EVALUATION,
        permission=can_trigger_review,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbhuman_resources:review",),
                icon=WBIcon.SEND.icon,
                key="evaluate",
                label=_("Evaluate"),
                action_label=_("Stage 4: Evaluation"),
                description_fields=_(
                    "<p>Status: <b>Stage 3: Review</b></p> <p>Reviewee: <b>{{_reviewee.computed_str}}</b></p>  <p>Reviewer: <b>{{_reviewer.computed_str}}</b></p>  <p>From: <b>{{from_date}}</b></p> <p>To: <b>{{to_date}}</b></p> <p>Deadline: <b>{{review_deadline}}</b></p>  <p>Do you want to send this review to <b>Stage 4: Evaluation?</b></p>"
                ),
            )
        },
    )
    def evaluate(self, by=None, description=None, **kwargs):
        if not self.review:
            self.review = timezone.now()

    @transition(
        field=status,
        source=Status.EVALUATION,
        target=Status.VALIDATION,
        permission=can_validate_review,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbhuman_resources:review",),
                icon=WBIcon.SEND.icon,
                key="validation",
                label=_("Validate"),
                action_label=_("Stage 4: Evaluation"),
                description_fields=_(
                    "<p>Status: <b>Stage 4: Evaluation</b></p> <p>Reviewee: <b>{{_reviewee.computed_str}}</b></p>  <p>Reviewer: <b>{{_reviewer.computed_str}}</b></p>  <p>From: <b>{{from_date}}</b></p> <p>To: <b>{{to_date}}</b></p> <p>Do you want to send this review to <b>Stage 5: Validation?</b></p>"
                ),
            )
        },
    )
    def validation(self, by=None, description=None, **kwargs):
        users = (
            get_user_model()
            .objects.filter(
                Q(groups__permissions__codename="administrate_review")
                | Q(user_permissions__codename="administrate_review")
            )
            .distinct()
        )
        for user in users:
            send_review_report_via_mail.delay(user.id, self.id)

    def send_review_notification(self, title, message, recipient, message_alert_deadline=True):
        if message_alert_deadline:
            message += gettext(
                "<p>Please pay particular attention to the deadline <b>{deadline}</b>, the review will automatically move to step 3 of the workflow on that date. At this stage the data will be frozen, you will not be able to modify it.</p>"
            ).format(deadline=self.review_deadline)

        send_notification(
            code="wbhuman_resources.review.notify",
            title=title,
            body=message,
            user=recipient,
            reverse_name="wbhuman_resources:review-detail",
            reverse_args=[self.id],
        )

    def generate_pdf(self):
        html = get_template("review/review_report.html")

        text_answers = ReviewAnswer.objects.filter(
            Q(question__review=self) & Q(question__answer_type=ReviewQuestion.ANSWERTYPE.TEXT)
        ).order_by("question__category__order", "question__order")
        category_ids = text_answers.values_list("question__category", flat=True).distinct()

        table = {}
        for category_id in category_ids:
            if category_id:
                category = ReviewQuestionCategory.objects.get(id=category_id)
                table[category.id] = {"name": category.name, "questions": {}}
            else:
                category_id = ""
                category = None
                table[""] = {"name": "", "questions": {}}
            question_ids = (
                text_answers.filter(question__category=category)
                .order_by("question__order")
                .values_list("question", flat=True)
                .distinct()
            )
            for question_id in question_ids:
                question = ReviewQuestion.objects.get(id=question_id)
                table[category_id]["questions"][question_id] = {"name": question.question, "answers": {}}
                for answer in text_answers.filter(
                    Q(question__category=category) & Q(question__id=question_id)
                ).order_by("question__order", "answered_by"):
                    table[category_id]["questions"][question_id]["answers"][answer.answered_by] = answer.answer_text

        rating_answers = (
            ReviewAnswer.objects.filter(Q(question__review=self) & Q(question__answer_type="RATING"))
            .annotate(
                is_reviewee=Case(
                    When(answered_by=self.reviewee, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ),
                is_reviewer=Case(
                    When(answered_by=self.reviewer, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ),
            )
            .order_by("question__category__order")
        )
        category_ids = rating_answers.values_list("question__category", flat=True).distinct()

        rating_table = {}
        for category_id in category_ids:
            if category_id:
                category = ReviewQuestionCategory.objects.get(id=category_id)
                rating_table[category.id] = {"name": category.name, "questions": {}}
            else:
                category_id = ""
                category = None
                rating_table[""] = {"name": "", "questions": {}}
            question_ids = (
                rating_answers.filter(question__category=category)
                .order_by("question__order")
                .values_list("question", flat=True)
                .distinct()
            )
            for question_id in question_ids:
                question = ReviewQuestion.objects.get(id=question_id)
                rating_table[category_id]["questions"][question_id] = {
                    "name": question.question,
                    "answers": {},
                    "answers_text": {},
                }
                for answer in rating_answers.filter(
                    Q(question__category=category) & Q(question__id=question_id)
                ).order_by("question__order", "answered_by"):
                    if answer.is_reviewee:
                        rating_table[category_id]["questions"][question_id]["answers"]["reviewee"] = (
                            answer.answer_number if answer.answer_number else "-"
                        )
                        rating_table[category_id]["questions"][question_id]["answers_text"]["reviewee"] = (
                            answer.answer_text if answer.answer_text else None
                        )
                    if answer.is_reviewer:
                        rating_table[category_id]["questions"][question_id]["answers"]["reviewer"] = (
                            answer.answer_number if answer.answer_number else "-"
                        )
                        rating_table[category_id]["questions"][question_id]["answers_text"]["reviewer"] = (
                            answer.answer_text if answer.answer_text else None
                        )

        total_reviewee = rating_answers.filter(is_reviewee=True).aggregate(total=Sum("question__weight"))["total"]
        total_reviewer = rating_answers.filter(is_reviewer=True).aggregate(total=Sum("question__weight"))["total"]
        global_rating_reviewee = (
            rating_answers.filter(is_reviewee=True)
            .annotate(global_rating=F("question__weight") * F("answer_number"))
            .aggregate(total=Sum("global_rating"))["total"]
        )
        global_rating_reviewer = (
            rating_answers.filter(is_reviewer=True)
            .annotate(global_rating=F("question__weight") * F("answer_number"))
            .aggregate(total=Sum("global_rating"))["total"]
        )
        global_rating_reviewee = (
            0 if total_reviewee is None or global_rating_reviewee is None else global_rating_reviewee / total_reviewee
        )
        global_rating_reviewer = (
            0 if total_reviewer is None or global_rating_reviewer is None else global_rating_reviewer / total_reviewer
        )

        html_content = html.render(
            {
                "base_url": Site.objects.get_current().domain,
                "review": self,
                "table": table,
                "rating_table": rating_table,
                "global_rating_reviewee": round(global_rating_reviewee, 2),
                "global_rating_reviewer": round(global_rating_reviewer, 2),
                "number_total_rating": ReviewQuestion.objects.filter(Q(review=self) & Q(answer_type="RATING")).count(),
            }
        )
        return HTML(
            string=html_content, base_url=settings.BASE_ENDPOINT_URL, url_fetcher=custom_url_fetcher
        ).write_pdf()

    @classmethod
    def get_subquery_review_related_to(cls, requester):
        answers = ReviewAnswer.objects.filter(question__review=OuterRef("pk"), answered_by=requester).order_by()
        return Coalesce(Subquery(answers.values("question__review")[:1]), None)

    @classmethod
    def subquery_global_rating(cls, requester):
        answers = ReviewAnswer.objects.filter(
            question__review=OuterRef("pk"),
            answered_by=requester,
            question__answer_type=ReviewQuestion.ANSWERTYPE.RATING,
            answer_number__isnull=False,
        ).order_by()

        subquery = (
            answers.annotate(
                rating_weighted=F("question__weight") * F("answer_number"),
            )
            .values("question__review")
            .annotate(
                total_rating=Sum("rating_weighted"),
                total_weight=Sum("question__weight"),
            )
            .annotate(global_rating=Coalesce(F("total_rating") / F("total_weight"), Decimal(0)))
            .values("global_rating")[:1]
        )

        return Coalesce(Subquery(subquery), None)

    def get_question_categories(self) -> models.QuerySet:
        return ReviewQuestionCategory.objects.filter(questions_related__review=self).order_by("order").distinct()

    def get_answer_categories_for_user(self, user: User) -> models.QuerySet:
        if self.status in [self.Status.FILL_IN_REVIEW, self.Status.REVIEW]:
            return (
                ReviewQuestionCategory.objects.filter(
                    questions_related__answers__answered_by=user.profile, questions_related__review=self
                )
                .order_by("order")
                .distinct()
            )
        else:  # EVALUATION
            return (
                ReviewQuestionCategory.objects.filter(
                    questions_related__answer_type=ReviewQuestion.ANSWERTYPE.TEXT, questions_related__review=self
                )
                .order_by("order")
                .distinct()
            )

    @classmethod
    def get_endpoint_basename(cls):
        return "wbhuman_resources:review"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbhuman_resources:reviewrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{computed_str}}"


class ReviewQuestionCategory(OrderableModel, WBModel):
    name = models.CharField(max_length=255, verbose_name=_("Name"), unique=True)
    weight = models.DecimalField(default=1.0, max_digits=16, decimal_places=1, verbose_name=_("Weight"))

    class Meta(OrderableModel.Meta):
        verbose_name = _("Review Question Category")
        verbose_name_plural = _("Review Question Categories")

    def __str__(self):
        return f"{self.name}"

    @classmethod
    def get_endpoint_basename(cls):
        return "wbhuman_resources:reviewquestioncategory"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbhuman_resources:reviewquestioncategoryrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{name}}"


class ReviewQuestion(ComplexToStringMixin, OrderableModel, WBModel):
    order_with_respect_to = ("review", "category")

    class ANSWERTYPE(models.TextChoices):
        TEXT = "TEXT", _("Text")
        RATING = "RATING", _("Rating")

    review = models.ForeignKey(
        to="wbhuman_resources.Review",
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name=_("Review"),
    )
    category = models.ForeignKey(
        to="wbhuman_resources.ReviewQuestionCategory",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="questions_related",
        verbose_name=_("Category"),
    )
    question = models.TextField(default="", blank=True, verbose_name=_("Question"))
    mandatory = models.BooleanField(default=True, verbose_name=_("Mandatory"))
    answer_type = models.CharField(
        max_length=32,
        default=ANSWERTYPE.TEXT,
        choices=ANSWERTYPE.choices,
        verbose_name=_("Type"),
    )
    for_reviewee = models.BooleanField(default=True, verbose_name=_("For Reviewee"))
    for_reviewer = models.BooleanField(default=True, verbose_name=_("For Reviewer"))
    for_department_peers = models.BooleanField(default=False, verbose_name=_("For Department Peers"))
    for_company_peers = models.BooleanField(default=False, verbose_name=_("For Company Peers"))
    weight = models.DecimalField(default=1.0, max_digits=16, decimal_places=1, verbose_name=_("Weight"))
    evaluation = models.ForeignKey(
        to="wbhuman_resources.Evaluation",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="evaluation_questions",
        verbose_name=_("Evaluation"),
    )

    class Meta:
        verbose_name = _("Review Question")
        verbose_name_plural = _("Review Questions")
        ordering = ("review", "category", "order")

    def compute_str(self) -> str:
        return f"{self.question}"

    def __str__(self):
        return f"({self.id}) - {self.computed_str}"

    def save(self, *args, **kwargs):
        self.computed_str = self.compute_str()
        super().save(*args, **kwargs)

    @classmethod
    def get_endpoint_basename(cls):
        return "wbhuman_resources:reviewquestion"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbhuman_resources:reviewquestionrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{computed_str}}"


class ReviewAnswer(models.Model):
    class Meta:
        verbose_name = _("Review Answer")
        verbose_name_plural = _("Review Answers")

    question = models.ForeignKey(
        to="wbhuman_resources.ReviewQuestion",
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name=_("Question"),
    )

    answered_by = models.ForeignKey(
        to="directory.Person",
        null=True,
        blank=True,
        related_name="related_answers",
        on_delete=models.deletion.SET_NULL,
        verbose_name=_("Answered By"),
    )

    answered_anonymized = models.CharField(
        null=True, blank=True, max_length=255, verbose_name=_("Answered Anonymized")
    )
    answer_number = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("Rating"), validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    answer_text = models.TextField(null=True, blank=True, verbose_name=_("Comment"))

    @classmethod
    def get_endpoint_basename(cls):
        return "wbhuman_resources:reviewanswer"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "id"


@receiver(pre_save, sender=Review)
def pre_save_review(sender, instance, **kwargs):
    if (
        not instance.is_template
        and instance.auto_apply_deadline
        and instance.review_deadline
        and instance.status == Review.Status.FILL_IN_REVIEW
    ):
        if instance.review_deadline < datetime.now().date():
            instance.finalize()

    if (
        not instance.is_template
        and instance.signed_reviewee
        and instance.signed_reviewer
        and instance.status == Review.Status.EVALUATION
    ):
        instance.validation()


@shared_task
def finalize_review(review_id):
    review = Review.objects.get(id=review_id)
    ReviewAnswer.objects.filter(
        Q(question__review=review)
        & Q(answered_by=review.reviewee)
        & Q(question__answer_type=ReviewQuestion.ANSWERTYPE.RATING)
        & Q(answer_number=None)
    ).update(answer_number=1)


@shared_task
def submit_reviews_from_group(group_id, user_id):
    user = get_user_model().objects.get(id=user_id)

    reviews = Review.objects.filter(
        Q(review_group__id=group_id)
        & Q(status=Review.Status.PREPARATION_OF_REVIEW)
        & Q(moderator=user.profile)
        & Q(is_template=False)
    )
    for review in reviews:
        review.submit()
        review.save()


@shared_task
def create_review_from_template(
    template_id, from_date, to_date, review_deadline, auto_apply_deadline, employees, include_kpi
):
    template = Review.objects.get(id=template_id)

    from_date = datetime.strptime(from_date, "%Y-%m-%d").date() if from_date and from_date != "null" else None
    to_date = datetime.strptime(to_date, "%Y-%m-%d").date() if to_date and to_date != "null" else None
    review_deadline = (
        datetime.strptime(review_deadline, "%Y-%m-%d").date()
        if review_deadline and review_deadline != "null"
        else None
    )

    include_kpi = str(include_kpi).lower() in ("yes", "true", "t", "1") if include_kpi else False

    _auto_apply_deadline = (
        str(auto_apply_deadline).lower() in ("yes", "true", "t", "1")
        if auto_apply_deadline
        else template.auto_apply_deadline
    )
    list_employees = Person.objects.filter(id__in=employees.split(",")) if employees else []

    for employee in list_employees:
        review = Review.objects.create(
            from_date=from_date,
            to_date=to_date,
            review_deadline=review_deadline,
            reviewee=employee,
            moderator=template.moderator,
            auto_apply_deadline=_auto_apply_deadline,
            status=template.status,
            review_group=template.review_group,
            year=template.year,
            type=template.type,
        )

        for _question in ReviewQuestion.objects.filter(review__id=template.id).order_by("order"):
            kwargs = {
                "review": review,
                "category": _question.category,
                "question": _question.question,
                "answer_type": _question.answer_type,
                "mandatory": _question.mandatory,
                "for_reviewee": _question.for_reviewee,
                "for_reviewer": _question.for_reviewer,
                "for_department_peers": _question.for_department_peers,
                "for_company_peers": _question.for_company_peers,
                "order": _question.order,
                "weight": _question.weight,
            }
            ReviewQuestion.objects.create(**kwargs)

        if include_kpi:
            qs_evaluations = Evaluation.objects.filter(is_active=True)
            evaluations = (
                qs_evaluations.filter(
                    Q(person=employee) | (Q(person__isnull=True) & Q(kpi__evaluated_persons=employee))
                )
                .annotate(
                    goal=F("kpi__goal"),
                    kpi_name=F("kpi__name"),
                    interval=F("kpi__evaluated_intervals"),
                    period=F("kpi__period"),
                    person_name=F("person__computed_str"),
                )
                .order_by("kpi", "-evaluation_date")
                .distinct("kpi")
            )

            category, _ = ReviewQuestionCategory.objects.get_or_create(name="KPI Evaluations")
            for evaluation in evaluations:
                percentage = round((evaluation.evaluated_score / evaluation.goal) * 100, 2)
                person_name = evaluation.person_name if evaluation.person_name else "Group"
                _question = gettext(
                    """The KPI '{kpi_name}' is evaluated {interval} over the period from {lower_period} to {upper_period}.
{person_name}'s evaluation as of {evaluation_date} was {evaluated_score} for a goal of {goal}. That is an accomplished percentage of {percentage}%.
What do you think of this result?
                """
                ).format(
                    kpi_name=evaluation.kpi_name,
                    interval=evaluation.interval,
                    lower_period=evaluation.period.lower,
                    upper_period=evaluation.period.upper,
                    person_name=person_name,
                    evaluation_date=evaluation.evaluation_date,
                    evaluated_score=evaluation.evaluated_score,
                    goal=evaluation.goal,
                    percentage=percentage,
                )

                kwargs = {
                    "review": review,
                    "category": category,
                    "question": _question,
                    "answer_type": ReviewQuestion.ANSWERTYPE.RATING,
                    "evaluation": evaluation,
                }
                ReviewQuestion.objects.create(**kwargs)


@shared_task
def submit_review(review_id):
    review = Review.objects.get(id=review_id)
    questions = ReviewQuestion.objects.filter(review=review)
    dict_questions = {}

    questions_for_company = questions.filter(for_company_peers=True)
    if questions_for_company.exists() and (main_company_id := get_main_company()):
        if _company := review.reviewee.employers.filter(id=main_company_id).first():
            for _person in (
                Person.objects.filter_only_internal()
                .filter(employers=_company)
                .exclude(Q(id=review.reviewee.id) | Q(id=review.reviewer.id))
            ):
                dict_questions[_person] = questions_for_company

    questions_for_department = questions.filter(for_department_peers=True)
    if questions_for_department.exists() and hasattr(review.reviewee, "human_resources"):
        if review.reviewee.human_resources.position:
            employees_peers = []
            for _position in review.reviewee.human_resources.position.get_ancestors(include_self=True):
                employees_peers += _position.get_employees().exclude(
                    Q(id=review.reviewee.id) & Q(id=review.reviewer.id)
                )
            person_peers = [_employee.profile for _employee in list(set(employees_peers))]
            for _peer in list(set(person_peers)):
                if _peer in dict_questions:
                    dict_questions[_peer] = questions_for_department.union(questions_for_company)
                else:
                    dict_questions[_peer] = questions_for_department

    dict_questions[review.reviewee] = questions.filter(for_reviewee=True)
    dict_questions[review.reviewer] = questions.filter(for_reviewer=True)

    for person, values in dict_questions.items():
        for _question in values:
            kwargs = {"question": _question, "answered_by": person, "answered_anonymized": hash(person)}
            if _evaluation := _question.evaluation:
                rating = _evaluation.get_rating()
                kwargs.update({"answer_number": rating})
            ReviewAnswer.objects.create(**kwargs)
        if hasattr(person, "user_account"):
            if person == review.reviewee:
                msg = gettext(
                    "Dear {first_name} {last_name}, <p>your review is ready. You can fill it in until {deadline}.</p>"
                ).format(first_name=person.first_name, last_name=person.last_name, deadline=review.review_deadline)
            elif person == review.reviewer:
                msg = gettext(
                    "Dear {first_name} {last_name}, <p>you are the reviewer of the review: {review}. You can fill in the questions related to you until <b>{deadline}.</b></p>"
                ).format(
                    first_name=person.first_name,
                    last_name=person.last_name,
                    review=str(review),
                    deadline=review.review_deadline,
                )
            else:
                msg = gettext(
                    "Dear {first_name} {last_name}, <p>you are a peer of the review: {review}. You can fill in the questions related to you until <b>{deadline}.</b></p>"
                ).format(
                    first_name=person.first_name,
                    last_name=person.last_name,
                    review=str(review),
                    deadline=review.review_deadline,
                )

            review.send_review_notification(
                title=gettext("Stage 2: Fill in review - {review}").format(review=str(review)),
                message=msg,
                recipient=person.user_account,
            )


@shared_task
def send_review_report_via_mail(user_id, review_id):
    user = get_user_model().objects.get(id=user_id)
    review = Review.objects.get(id=review_id)
    pdf_content = review.generate_pdf()
    filename = f"{slugify(str(review))}.pdf"

    content_file = ContentFile(pdf_content, name=filename)
    document_type, _ = DocumentType.objects.get_or_create(name="mailing")

    document, _ = Document.objects.update_or_create(
        document_type=document_type,
        system_created=True,
        system_key=f"review-{review.id}-{filename}",
        defaults={
            "file": content_file,
            "name": filename,
            "permission_type": Document.PermissionType.PRIVATE,
            "creator": user,
        },
    )
    document.link(review)

    document.send_email(to_emails=user.email, as_link=True, subject=gettext("Review PDF - ") + review.computed_str)
