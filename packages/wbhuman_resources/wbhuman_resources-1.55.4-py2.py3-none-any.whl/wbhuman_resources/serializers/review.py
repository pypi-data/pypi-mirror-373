from datetime import datetime

from django.db.models import Q
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers as rf_serializers
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.contrib.directory.models import Person
from wbcore.contrib.directory.serializers import PersonRepresentationSerializer

from wbhuman_resources.models import (
    Review,
    ReviewAnswer,
    ReviewGroup,
    ReviewQuestion,
    ReviewQuestionCategory,
)


class ReviewGroupRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbhuman_resources:reviewgroup-detail")

    class Meta:
        model = ReviewGroup
        fields = ("id", "name", "_detail")


class ReviewRepresentationSerializer(wb_serializers.RepresentationSerializer):
    id_repr = wb_serializers.CharField(source="id", read_only=True, label=_("ID"))
    _detail = wb_serializers.HyperlinkField(reverse_name="wbhuman_resources:review-detail")

    class Meta:
        model = Review
        fields = ("id", "id_repr", "computed_str", "_detail")


class ReviewQuestionCategoryRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = ReviewQuestionCategory
        fields = (
            "id",
            "name",
        )


class ReviewQuestionRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = ReviewQuestion
        fields = (
            "id",
            "computed_str",
            "question",
        )


class ReviewAnswerRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = ReviewAnswer
        fields = ("id",)


class ReviewGroupModelSerializer(wb_serializers.ModelSerializer):
    @wb_serializers.register_resource()
    def register_history_resource(self, instance, request, user):
        resources = {
            "review": reverse("wbhuman_resources:reviewgroup-review-list", args=[instance.id], request=request),
        }

        if Review.objects.filter(
            Q(review_group=instance) & Q(status=Review.Status.PREPARATION_OF_REVIEW) & Q(moderator=user.profile)
        ):
            resources["submitreviews"] = reverse(
                "wbhuman_resources:reviewgroup-submitreviews", args=[instance.id], request=request
            )

        return resources

    _employees = PersonRepresentationSerializer(many=True, source="employees")

    class Meta:
        model = ReviewGroup
        fields = ("id", "name", "employees", "_employees", "_additional_resources")


class ReviewModelSerializer(wb_serializers.ModelSerializer):
    @wb_serializers.register_resource()
    def register_history_resource(self, instance, request, user):
        resources = {}
        categories = instance.get_question_categories()
        if instance.status == Review.Status.PREPARATION_OF_REVIEW:
            resources["category"] = reverse("wbhuman_resources:reviewquestioncategory-list", args=[], request=request)
            resources["questionnocategory"] = reverse(
                "wbhuman_resources:review-reviewquestionnocategory-list", args=[instance.id], request=request
            )
            for category in categories:
                resources[f"questioncategory{category.id}"] = reverse(
                    "wbhuman_resources:review-reviewquestioncategory-list",
                    args=[instance.id, category.id],
                    request=request,
                )
        else:
            resources["reviewanswerquestionnocategory"] = reverse(
                "wbhuman_resources:review-reviewanswerquestionnocategory-list", args=[instance.id], request=request
            )
            for category in categories:
                resources[f"reviewanswerquestioncategory{category.id}"] = reverse(
                    "wbhuman_resources:review-reviewanswerquestioncategory-list",
                    args=[instance.id, category.id],
                    request=request,
                )
            resources["progress"] = reverse(
                "wbhuman_resources:review-progress-list", args=[instance.id], request=request
            )

        if instance.is_template and instance.review_group and instance.moderator == user.profile:
            resources["generate"] = reverse("wbhuman_resources:review-generate", args=[instance.id], request=request)

        if instance.status == Review.Status.FILL_IN_REVIEW:
            if instance.reviewee == user.profile and not instance.completely_filled_reviewee:
                resources["completelyfilledreviewee"] = reverse(
                    "wbhuman_resources:review-completelyfilled-reviewee", args=[instance.id], request=request
                )
            if instance.reviewer == user.profile and not instance.completely_filled_reviewer:
                resources["completelyfilledreviewer"] = reverse(
                    "wbhuman_resources:review-completelyfilled-reviewer", args=[instance.id], request=request
                )

        if instance.status in [Review.Status.EVALUATION, Review.Status.VALIDATION]:
            resources["rating_review_answer_key"] = (
                reverse("wbhuman_resources:review-reviewanswerpandasview-list", args=[instance.id], request=request)
                + "?answer_type=RATING"
            )
            resources["text_review_answer_key"] = (
                reverse("wbhuman_resources:review-reviewanswerpandasview-list", args=[instance.id], request=request)
                + "?answer_type=TEXT"
            )

            if instance.status == Review.Status.EVALUATION:
                if instance.reviewee == user.profile and not instance.signed_reviewee:
                    resources["signaturereviewee"] = reverse(
                        "wbhuman_resources:review-signature-reviewee", args=[instance.id], request=request
                    )
                if instance.reviewer == user.profile and not instance.signed_reviewer:
                    resources["signaturereviewer"] = reverse(
                        "wbhuman_resources:review-signature-reviewer", args=[instance.id], request=request
                    )

            if instance.status == Review.Status.VALIDATION and (
                instance.moderator == user.profile or user.has_perm("wbhuman_resources.administrate_review")
            ):
                resources["generate_pdf"] = reverse(
                    "wbhuman_resources:review-generate-pdf", args=[instance.id], request=request
                )

        return resources

    _reviewee = PersonRepresentationSerializer(source="reviewee")
    _reviewer = PersonRepresentationSerializer(source="reviewer")
    moderator = wb_serializers.PrimaryKeyRelatedField(
        default=wb_serializers.CurrentUserDefault("profile"), queryset=Person.objects.all(), label=_("Moderator")
    )
    _moderator = PersonRepresentationSerializer(source="moderator")

    _review_group = ReviewGroupRepresentationSerializer(source="review_group")

    global_rating = wb_serializers.DecimalField(
        read_only=True,
        max_digits=14,
        decimal_places=2,
        help_text=_("Only the rating questions you answered are taken into account"),
    )
    year = wb_serializers.YearField(default=lambda: datetime.now().year)
    is_template = wb_serializers.BooleanField(default=True, label=_("Is Template"))

    reviewee = wb_serializers.PrimaryKeyRelatedField(
        default=wb_serializers.DefaultAttributeFromObject(source="reviewee"),
        read_only=lambda view: not view.is_modifiable,
        queryset=Person.objects.all(),
    )
    reviewer = wb_serializers.PrimaryKeyRelatedField(
        default=wb_serializers.DefaultAttributeFromObject(source="reviewer"),
        read_only=lambda view: not view.is_modifiable,
        queryset=Person.objects.all(),
    )

    class Meta:
        model = Review
        fields = (
            "id",
            "computed_str",
            "from_date",
            "to_date",
            "review_deadline",
            "review",
            "auto_apply_deadline",
            "status",
            "reviewee",
            "_reviewee",
            "reviewer",
            "_reviewer",
            "moderator",
            "_moderator",
            "review_group",
            "_review_group",
            "is_template",
            "feedback_reviewee",
            "feedback_reviewer",
            "_additional_resources",
            "signed_reviewee",
            "signed_reviewer",
            "year",
            "type",
            "completely_filled_reviewee",
            "completely_filled_reviewer",
            "global_rating",
            "changed",
        )
        read_only_fields = (
            "signed_reviewee",
            "signed_reviewer",
            "completely_filled_reviewee",
            "completely_filled_reviewer",
        )

    def validate(self, data):
        obj = self.instance
        errors = {}
        reviewer = data.get("reviewer", obj.reviewer if obj else None)
        reviewee = data.get("reviewee", obj.reviewee if obj else None)
        if data.get("is_template", obj.is_template if obj else None):
            dict_fields = {
                "from_date": data.get("from_date", obj.from_date if obj else None),
                "to_date": data.get("to_date", obj.to_date if obj else None),
                "review_deadline": data.get("review_deadline", obj.review_deadline if obj else None),
                "reviewee": data.get("reviewee", obj.reviewee if obj else None),
                "reviewer": data.get("reviewer", obj.reviewer if obj else None),
            }
            for key, value in dict_fields.items():
                if value:
                    errors[key] = [gettext("The field has to be empty if is_template is True")]
        elif reviewer == reviewee is not None:
            errors["reviewer"] = gettext("reviewer must be different from reviewee")
            errors["reviewee"] = gettext("reviewer must be different from reviewee")

        if len(errors.keys()) > 0:
            raise rf_serializers.ValidationError(errors)

        return super().validate(data)


class ReviewListModelSerializer(ReviewModelSerializer):
    class Meta:
        model = Review
        fields = (
            "id",
            "from_date",
            "to_date",
            "review_deadline",
            "review",
            "auto_apply_deadline",
            "status",
            "reviewee",
            "_reviewee",
            "reviewer",
            "_reviewer",
            "moderator",
            "_moderator",
            "review_group",
            "_review_group",
            "is_template",
            "year",
            "type",
            "changed",
            "_additional_resources",
        )


class ReviewReadOnlyModelSerializer(ReviewModelSerializer):
    @wb_serializers.register_resource()
    def register_history_resource(self, instance, request, user):
        return {}


class ReviewQuestionCategoryModelSerializer(wb_serializers.ModelSerializer):
    @wb_serializers.register_resource()
    def register_history_resource(self, instance, request, user):
        resources = {
            "reviewquestion": reverse(
                "wbhuman_resources:reviewquestioncategory-reviewquestion-list", args=[instance.id], request=request
            ),
        }
        return resources

    class Meta:
        model = ReviewQuestionCategory
        fields = ("id", "name", "order", "weight", "_additional_resources")


class ReviewQuestionModelSerializer(wb_serializers.ModelSerializer):
    _review = ReviewRepresentationSerializer(source="review")
    category = wb_serializers.PrimaryKeyRelatedField(
        default=wb_serializers.DefaultFromKwargs("category_id"), queryset=ReviewQuestionCategory.objects.all()
    )
    _category = ReviewQuestionCategoryRepresentationSerializer(source="category")

    review_for = wb_serializers.CharField(label=_("Review For"), read_only=True)
    question = wb_serializers.TextAreaField(label=_("Question"), allow_blank=True)

    @wb_serializers.register_resource()
    def register_resource(self, instance, request, user):
        resources = {
            "review_answers_table": reverse("wbhuman_resources:reviewanswer-list", args=[], request=request)
            + f"?question={instance.id}",
        }
        return resources

    class Meta:
        model = ReviewQuestion
        fields = (
            "id",
            "review",
            "_review",
            "category",
            "_category",
            "question",
            "computed_str",
            "mandatory",
            "answer_type",
            "for_reviewee",
            "for_reviewer",
            "for_department_peers",
            "for_company_peers",
            "order",
            "weight",
            "review_for",
            "_additional_resources",
        )

    def validate(self, data):
        obj = self.instance
        for_department_peers = data.get("for_department_peers", obj.for_department_peers if obj else None)
        for_company_peers = data.get("for_company_peers", obj.for_company_peers if obj else None)
        errors = {}
        if not obj:
            qs = ReviewQuestion.objects.filter(
                Q(review=data.get("review"))
                & Q(category=data.get("category"))
                & ~Q(answer_type=data.get("answer_type"))
            )
            if qs.exists():
                errors["answer_type"] = gettext("Questions in a section must be of the same type")

        if for_department_peers and for_company_peers:
            errors["non_field_errors"] = [
                gettext(
                    "Both 'For department peers' and 'For company peers' true does not make any sense. Only 1 can be active"
                )
            ]

        if len(errors.keys()) > 0:
            raise rf_serializers.ValidationError(errors)

        return super().validate(data)


class ReviewAnswerModelSerializer(wb_serializers.ModelSerializer):
    _question = ReviewQuestionRepresentationSerializer(source="question")
    _answered_by = PersonRepresentationSerializer(source="answered_by")
    answer_number = wb_serializers.EmojiRatingField(label=_("Rating"))
    answer_text = wb_serializers.TextAreaField(label=_("Comment"), allow_blank=True, allow_null=True)
    weight = wb_serializers.DecimalField(read_only=True, max_digits=16, decimal_places=1)
    mandatory = wb_serializers.BooleanField(
        label=_("Mandatory"),
        read_only=True,
    )

    question_name = wb_serializers.TextAreaField(read_only=True, label=_("Question"))

    class Meta:
        model = ReviewAnswer
        fields = (
            "id",
            "question",
            "_question",
            "answered_by",
            "_answered_by",
            "answered_anonymized",
            "answer_number",
            "answer_text",
            "weight",
            "question_name",
            "mandatory",
        )
        read_only_fields = ("question", "answered_by", "answered_anonymized")

    def validate(self, data):
        errors = {}
        if obj := self.instance:
            if obj.question.mandatory:
                answer_number = data.get("answer_number", obj.answer_number if obj else None)
                answer_text = data.get("answer_text", obj.answer_text if obj else None)
                if not answer_text and obj.question.answer_type == ReviewQuestion.ANSWERTYPE.TEXT:
                    errors["answer_text"] = gettext(
                        "Comment cannot be empty, a response to this question is mandatory"
                    )
                if not answer_number and obj.question.answer_type == ReviewQuestion.ANSWERTYPE.RATING:
                    errors["answer_number"] = gettext(
                        "Rating cannot be empty, a response to this question is mandatory"
                    )

        if len(errors.keys()) > 0:
            raise rf_serializers.ValidationError(errors)

        return super().validate(data)
