import pandas as pd
from django.contrib.messages import info, warning
from django.db.models import ExpressionWrapper, F, Q, Value, functions
from django.db.models.fields import CharField
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from wbcore import viewsets
from wbcore.contrib.authentication.authentication import JWTCookieAuthentication
from wbcore.pandas import fields as pf
from wbcore.pandas.views import PandasAPIViewSet
from wbcore.utils.strings import format_number
from wbcore.utils.views import CloneMixin
from wbcore.viewsets.mixins import OrderableMixin

from wbhuman_resources.filters import (
    RatingReviewAnswerReviewFilter,
    ReviewAnswerFilter,
    ReviewFilter,
    ReviewGroupFilter,
    ReviewProgressReviewFilter,
    ReviewQuestionCategoryFilter,
    ReviewQuestionFilter,
    ReviewTemplateFilter,
)
from wbhuman_resources.models import (
    Review,
    ReviewAnswer,
    ReviewGroup,
    ReviewQuestion,
    ReviewQuestionCategory,
    create_review_from_template,
    send_review_report_via_mail,
    submit_reviews_from_group,
)
from wbhuman_resources.serializers import (
    ReviewAnswerModelSerializer,
    ReviewAnswerRepresentationSerializer,
    ReviewGroupModelSerializer,
    ReviewGroupRepresentationSerializer,
    ReviewListModelSerializer,
    ReviewModelSerializer,
    ReviewQuestionCategoryModelSerializer,
    ReviewQuestionCategoryRepresentationSerializer,
    ReviewQuestionModelSerializer,
    ReviewQuestionRepresentationSerializer,
    ReviewReadOnlyModelSerializer,
    ReviewRepresentationSerializer,
)

from .buttons import ReviewButtonConfig, ReviewGroupButtonConfig
from .display import (
    ReviewAnswerDisplayConfig,
    ReviewAnswerReviewPandasDisplayConfig,
    ReviewDisplayConfig,
    ReviewGroupDisplayConfig,
    ReviewProgressPandasDisplayConfig,
    ReviewProgressReviewPandasDisplayConfig,
    ReviewQuestionCategoryDisplayConfig,
    ReviewQuestionDisplayConfig,
    ReviewQuestionReviewDisplayConfig,
    ReviewTemplateDisplayConfig,
)
from .endpoints import (
    ReviewAnswerEndpointConfig,
    ReviewAnswerReviewNoCategoryEndpointConfig,
    ReviewAnswerReviewPandasEndpointConfig,
    ReviewAnswerReviewQuestionCategoryEndpointConfig,
    ReviewEndpointConfig,
    ReviewGroupEndpointConfig,
    ReviewProgressPandasEndpointConfig,
    ReviewProgressReviewPandasEndpointConfig,
    ReviewQuestionCategoryEndpointConfig,
    ReviewQuestionEndpointConfig,
    ReviewQuestionReviewCategoryEndpointConfig,
    ReviewQuestionReviewEndpointConfig,
    ReviewQuestionReviewNoCategoryEndpointConfig,
    ReviewQuestionReviewQuestionCategoryEndpointConfig,
    ReviewReviewGroupEndpointConfig,
)
from .titles import (
    ReviewAnswerReviewPandasTitleConfig,
    ReviewAnswerReviewTitleConfig,
    ReviewProgressPandasTitleConfig,
    ReviewProgressReviewPandasTitleConfig,
    ReviewQuestionReviewQuestionCategoryTitleConfig,
    ReviewQuestionReviewTitleConfig,
    ReviewReviewGroupTitleConfig,
    ReviewTemplateTitleConfig,
)


def apply_group_anonymized(x):
    if x["answered_by_id"] == x["reviewee"]:
        x["group_anonymized"] = "reviewee"
    elif x["answered_by_id"] == x["reviewer"]:
        x["group_anonymized"] = "reviewer"
    else:
        x["group_anonymized"] = "peers"
    return x


class ReviewGroupRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbhuman_resources:reviewgrouprepresentation"

    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    ordering_fields = ordering = ("name",)
    search_fields = ("name",)

    queryset = ReviewGroup.objects.all()
    serializer_class = ReviewGroupRepresentationSerializer


class ReviewGroupModelViewSet(viewsets.ModelViewSet):
    IDENTIFIER = "wbhuman_resources:reviewgroup"
    display_config_class = ReviewGroupDisplayConfig
    endpoint_config_class = ReviewGroupEndpointConfig
    button_config_class = ReviewGroupButtonConfig
    search_fields = ["name"]
    ordering_fields = ordering = ["name"]

    filterset_class = ReviewGroupFilter

    serializer_class = ReviewGroupModelSerializer

    queryset = ReviewGroup.objects.all()

    @action(detail=True, methods=["PATCH"], authentication_classes=[JWTCookieAuthentication])
    def submitreviews(self, request, pk):
        submit_reviews_from_group.delay(pk, request.user.id)
        return Response(
            {"__notification": {"title": gettext("Reviews successfully submitted")}},
            status=status.HTTP_200_OK,
        )


class ReviewRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbhuman_resources:reviewrepresentation"
    queryset = Review.objects.all()
    search_fields = [
        "computed_str",
        "reviewer__computed_str",
        "reviewee__computed_str",
        "moderator__computed_str",
        "review_group__name",
    ]
    ordering = ["-is_template", "-year", "computed_str"]
    serializer_class = ReviewRepresentationSerializer


class ReviewModelViewSet(CloneMixin, viewsets.ModelViewSet):
    IDENTIFIER = "wbhuman_resources:review"
    button_config_class = ReviewButtonConfig
    display_config_class = ReviewDisplayConfig
    endpoint_config_class = ReviewEndpointConfig
    queryset = Review.objects.all()
    search_fields = [
        "computed_str",
        "reviewer__computed_str",
        "reviewee__computed_str",
        "moderator__computed_str",
        "review_group__name",
    ]
    ordering = ["-year", "-to_date", "-changed"]
    ordering_fields = [
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
        "year",
        "type",
        "changed",
    ]
    filterset_class = ReviewFilter

    serializer_class = ReviewModelSerializer

    def get_serializer_class(self):
        if hasattr(self, "kwargs"):
            if review_id := self.kwargs.get("pk"):
                obj = get_object_or_404(Review, pk=review_id)
                if (
                    self.request.user.profile in [obj.moderator, obj.reviewer, obj.reviewee]
                    or self.request.user in Review.get_administrators()
                ):
                    return ReviewModelSerializer
                else:
                    return ReviewReadOnlyModelSerializer
        return ReviewListModelSerializer

    queryset = Review.objects.all()

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .annotate(
                related_to_me=Review.get_subquery_review_related_to(self.request.user.profile),
                global_rating=Review.subquery_global_rating(self.request.user.profile),
            )
        )
        access_condition = (
            Q(related_to_me__isnull=False)
            | Q(moderator=self.request.user.profile)
            | Q(reviewer=self.request.user.profile)
            | Q(reviewee=self.request.user.profile)
            | (Q(related_to_me__isnull=True) & Q(moderator=None))
        )
        if self.request.user.has_perm("wbhuman_resources.administrate_review"):
            access_condition |= Q(status=Review.Status.VALIDATION)
        if self.request.user in Review.get_administrators():
            access_condition |= ~Q(status=Review.Status.PREPARATION_OF_REVIEW)
        return qs.filter(access_condition)

    @cached_property
    def is_modifiable(self):
        if "pk" in self.kwargs and (obj := self.get_object()):
            return obj.moderator == self.request.user.profile and obj.status in [
                Review.Status.FILL_IN_REVIEW,
                Review.Status.PREPARATION_OF_REVIEW,
            ]
        return self.new_mode

    @action(detail=True, methods=["PATCH"], authentication_classes=[JWTCookieAuthentication])
    def generate(self, request, pk):
        from_date = request.POST.get("from_date", None)
        to_date = request.POST.get("to_date", None)
        review_deadline = request.POST.get("review_deadline", None)
        auto_apply_deadline = request.POST.get("auto_apply_deadline", None)
        employees = request.POST.get("employees", None)
        include_kpi = request.POST.get("include_kpi", None)
        create_review_from_template.delay(
            pk, from_date, to_date, review_deadline, auto_apply_deadline, employees, include_kpi
        )

        return Response(
            {"__notification": {"title": gettext("Review is going to be created from template: ") + str(pk)}},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["PATCH"], authentication_classes=[JWTCookieAuthentication])
    def generate_pdf(self, request, pk):
        review = Review.objects.get(id=pk)

        if review.moderator != request.user.profile and not request.user.has_perm(
            "wbhuman_resources.administrate_review"
        ):
            return Response({}, status=status.HTTP_403_FORBIDDEN)
        send_review_report_via_mail.delay(request.user.id, pk)

        return Response(
            {"__notification": {"title": gettext("PDF is going to be created and sent to you.")}},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["PATCH"], authentication_classes=[JWTCookieAuthentication])
    def signature_reviewee(self, request, pk=None):
        review = Review.objects.get(id=pk)
        review.signed_reviewee = timezone.now()
        if feedback_reviewee := request.POST.get("feedback_reviewee", ""):
            review.feedback_reviewee = feedback_reviewee
        review.save()
        return Response(
            {"__notification": {"title": gettext("Review is acknowledged by the reviewee")}},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["PATCH"], authentication_classes=[JWTCookieAuthentication])
    def signature_reviewer(self, request, pk=None):
        review = Review.objects.get(id=pk)
        review.signed_reviewer = timezone.now()
        if feedback_reviewer := request.POST.get("feedback_reviewer", ""):
            review.feedback_reviewer = feedback_reviewer
        review.save()
        return Response(
            {"__notification": {"title": gettext("Review is acknowledged by the reviewer")}},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["PATCH"], authentication_classes=[JWTCookieAuthentication])
    def completelyfilled_reviewee(self, request, pk=None):
        review = Review.objects.get(id=pk)
        review.completely_filled_reviewee = timezone.now()
        if review.completely_filled_reviewer:
            review.finalize()
        review.save()
        return Response(
            {"__notification": {"title": gettext("Reviewee has finished answering the review questions")}},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["PATCH"], authentication_classes=[JWTCookieAuthentication])
    def completelyfilled_reviewer(self, request, pk=None):
        review = Review.objects.get(id=pk)
        review.completely_filled_reviewer = timezone.now()
        if review.completely_filled_reviewee:
            review.finalize()
        review.save()
        return Response(
            {"__notification": {"title": gettext("Reviewer has finished answering the review questions")}},
            status=status.HTTP_200_OK,
        )


class ReviewReviewGroupModelViewSet(ReviewModelViewSet):
    title_config_class = ReviewReviewGroupTitleConfig
    endpoint_config_class = ReviewReviewGroupEndpointConfig

    def get_queryset(self):
        return super().get_queryset().filter(review_group__id=self.kwargs["review_group_id"])


class ReviewTemplateModelViewSet(ReviewModelViewSet):
    title_config_class = ReviewTemplateTitleConfig
    display_config_class = ReviewTemplateDisplayConfig

    filterset_class = ReviewTemplateFilter

    def get_queryset(self):
        return super().get_queryset().filter(is_template=True)

    def add_messages(
        self,
        request,
        queryset=None,
        paginated_queryset=None,
        instance=None,
        initial=False,
    ):
        message = gettext(
            "The fields <b>From</b>, <b>To</b>, <b>Deadline</b>, <b>Reviewee</b> and <b>Reviewer</b> have to be empty if <u><b> template is true </b></u> within a <b>Review Group</b>. They get filled in once the <b>Review Group</b> creates them."
        )
        if not instance:
            # TODO Show the message during the creation
            info(request, message)


class ReviewQuestionCategoryRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbhuman_resources:reviewquestioncategoryrepresentation"

    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    ordering_fields = ordering = ("name",)
    search_fields = ("name",)

    queryset = ReviewQuestionCategory.objects.all()
    serializer_class = ReviewQuestionCategoryRepresentationSerializer


class ReviewQuestionCategoryModelViewSet(OrderableMixin, viewsets.ModelViewSet):
    IDENTIFIER = "wbhuman_resources:reviewquestioncategory"
    display_config_class = ReviewQuestionCategoryDisplayConfig
    endpoint_config_class = ReviewQuestionCategoryEndpointConfig

    search_fields = ["name"]
    ordering = ["order", "name"]
    ordering_fields = ["name", "weight"]

    filterset_class = ReviewQuestionCategoryFilter

    serializer_class = ReviewQuestionCategoryModelSerializer

    queryset = ReviewQuestionCategory.objects.all()


class ReviewQuestionRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbhuman_resources:reviewquestionrepresentation"
    search_fields = ["question"]

    queryset = ReviewQuestion.objects.all()
    serializer_class = ReviewQuestionRepresentationSerializer


class ReviewQuestionModelViewSet(OrderableMixin, viewsets.ModelViewSet):
    IDENTIFIER = "wbhuman_resources:reviewquestion"
    display_config_class = ReviewQuestionDisplayConfig
    endpoint_config_class = ReviewQuestionEndpointConfig

    search_fields = ["question"]
    ordering = ["order"]
    ordering_fields = [
        "review",
        "category",
        "mandatory",
        "answer_type",
        "for_reviewee",
        "for_reviewer",
        "for_department_peers",
        "for_company_peers",
        "weight",
    ]

    filterset_class = ReviewQuestionFilter

    serializer_class = ReviewQuestionModelSerializer

    queryset = ReviewQuestion.objects.all()

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                review_for=ExpressionWrapper(
                    functions.Concat(
                        functions.Cast("for_reviewee", output_field=CharField()),
                        Value(" / "),
                        functions.Cast("for_reviewer", output_field=CharField()),
                        Value(" / "),
                        functions.Cast("for_department_peers", output_field=CharField()),
                        Value(" / "),
                        functions.Cast("for_company_peers", output_field=CharField()),
                    ),
                    output_field=CharField(),
                )
            )
        )


class ReviewQuestionReviewModelViewSet(ReviewQuestionModelViewSet):
    title_config_class = ReviewQuestionReviewTitleConfig
    endpoint_config_class = ReviewQuestionReviewEndpointConfig
    display_config_class = ReviewQuestionReviewDisplayConfig

    @cached_property
    def review(self):
        return get_object_or_404(Review, pk=self.kwargs["review_id"])

    def get_queryset(self):
        return super().get_queryset().filter(review=self.review)


class ReviewQuestionReviewNoCategoryModelViewSet(ReviewQuestionReviewModelViewSet):
    endpoint_config_class = ReviewQuestionReviewNoCategoryEndpointConfig

    def get_queryset(self):
        return super().get_queryset().filter(Q(review__id=self.kwargs["review_id"]) & Q(category=None))


class ReviewQuestionReviewCategoryModelViewSet(ReviewQuestionReviewModelViewSet):
    endpoint_config_class = ReviewQuestionReviewCategoryEndpointConfig

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(Q(review__id=self.kwargs["review_id"]) & Q(category=self.kwargs["category_id"]))
        )


class ReviewQuestionReviewQuestionCategoryModelViewSet(ReviewQuestionModelViewSet):
    title_config_class = ReviewQuestionReviewQuestionCategoryTitleConfig
    endpoint_config_class = ReviewQuestionReviewQuestionCategoryEndpointConfig

    def get_queryset(self):
        return super().get_queryset().filter(category__id=self.kwargs["category_id"])


class ReviewAnswerRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbhuman_resources:reviewanswerrepresentation"
    queryset = ReviewAnswer.objects.all()
    serializer_class = ReviewAnswerRepresentationSerializer


class ReviewAnswerModelViewSet(viewsets.ModelViewSet):
    IDENTIFIER = "wbhuman_resources:reviewanswer"
    display_config_class = ReviewAnswerDisplayConfig
    endpoint_config_class = ReviewAnswerEndpointConfig

    search_fields = ["question__question", "answered_by__computed_str", "answer_text"]
    ordering_fields = ["question", "answer_number", "answer_text", "answered_by"]

    filterset_class = ReviewAnswerFilter

    serializer_class = ReviewAnswerModelSerializer

    queryset = ReviewAnswer.objects.select_related("question").annotate(
        mandatory=F("question__mandatory"),
        weight=F("question__weight"),
        question_name=F("question__computed_str"),
    )

    def add_messages(
        self,
        request,
        queryset=None,
        paginated_queryset=None,
        instance=None,
        initial=False,
    ):
        message = gettext(
            "It is recommended to add a comment for the answers whose rating is 'very bad', 'bad' or 'very good'"
        )
        error_found = False
        qs = [instance] if instance else queryset
        for instance in qs:
            if instance.answer_number in [1, 2, 4] and not instance.answer_text:
                error_found = True
        if error_found:
            warning(request, message)


class ReviewAnswerReviewQuestionCategoryModelViewSet(ReviewAnswerModelViewSet):
    ordering = ["question__order", "question_name", "answered_by"]
    title_config_class = ReviewAnswerReviewTitleConfig
    endpoint_config_class = ReviewAnswerReviewQuestionCategoryEndpointConfig

    @cached_property
    def review(self):
        return get_object_or_404(Review, pk=self.kwargs["review_id"])

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .filter(Q(question__review=self.review) & Q(question__category=self.kwargs.get("category_id")))
        )
        if self.review.status in [Review.Status.REVIEW, Review.Status.FILL_IN_REVIEW]:
            qs = qs.filter(answered_by=self.request.user.profile)
        elif self.review.status in [Review.Status.EVALUATION, Review.Status.VALIDATION]:
            qs = (
                qs.filter(question__answer_type=ReviewQuestion.ANSWERTYPE.TEXT)
                .exclude(~Q(answered_by=F("question__review__reviewee")) & Q(answer_text=None))
                .order_by("question_name")
            )
        return qs


class ReviewAnswerReviewNoCategoryModelViewSet(ReviewAnswerReviewQuestionCategoryModelViewSet):
    endpoint_config_class = ReviewAnswerReviewNoCategoryEndpointConfig


class ReviewProgressReviewPandasViewSet(PandasAPIViewSet):
    IDENTIFIER = "wbhuman_resources:review-progress"
    queryset = ReviewAnswer.objects.all()

    display_config_class = ReviewProgressReviewPandasDisplayConfig
    title_config_class = ReviewProgressReviewPandasTitleConfig
    endpoint_config_class = ReviewProgressReviewPandasEndpointConfig

    ordering_fields = ["answered_by"]

    filterset_class = ReviewProgressReviewFilter

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(question__review=self.kwargs["review_id"])
            .annotate(answer_type=F("question__answer_type"), answered_by_name=F("answered_by__computed_str"))
        )

    def get_pandas_fields(self, request):
        fields = [
            pf.PKField("id", label=_("ID")),
            pf.CharField(key="answered_by_name", label=_("Answered By")),
            pf.FloatField(key="progress", label=_("Progress"), percent=True),
            pf.CharField(key="answered_by", label=_("Answered By")),
            pf.CharField(key="answer_type_y", label=_("Total")),
            pf.CharField(key="answer_number", label=_("Answer Number")),
            pf.TextField(key="answer_text", label=_("Answer Text")),
        ]
        return pf.PandasFields(fields=tuple(fields))

    def get_dataframe(self, request, queryset, **kwargs):
        df = pd.DataFrame()
        if queryset.exists():
            df0 = pd.DataFrame(
                queryset.values(
                    "answered_anonymized", "answered_by_name", "answer_type", "answer_number", "answer_text"
                ),
                columns=["answered_anonymized", "answered_by_name", "answer_type", "answer_number", "answer_text"],
            )
            df_rating = df0[df0["answer_type"] == "RATING"].groupby(["answered_by_name"]).count()
            df_text = df0[df0["answer_type"] == "TEXT"].groupby(["answered_by_name"]).count()
            df = pd.merge(
                df_rating[["answer_type", "answer_number"]],
                df_text[["answer_type", "answer_text"]],
                on="answered_by_name",
                how="outer",
            )
            df.fillna(0, inplace=True)
            df["progress"] = (df["answer_number"] + df["answer_text"]) / (df["answer_type_x"] + df["answer_type_y"])
            df.progress.fillna(0, inplace=True)
            df["answered_by_name"] = df.index
            df = df.sort_values(by=["progress"], ascending=False)
            df.reset_index(drop=True, inplace=True)
            df["id"] = df.index
        return df


class ReviewAnswerReviewPandasViewSet(PandasAPIViewSet):
    IDENTIFIER = "wbhuman_resources:review-reviewanswerpandasview"
    queryset = ReviewAnswer.objects.all()

    ordering_fields = ["answered_by"]

    display_config_class = ReviewAnswerReviewPandasDisplayConfig
    title_config_class = ReviewAnswerReviewPandasTitleConfig
    endpoint_config_class = ReviewAnswerReviewPandasEndpointConfig

    filterset_class = RatingReviewAnswerReviewFilter

    @cached_property
    def review(self):
        return get_object_or_404(Review, pk=self.kwargs["review_id"])

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(question__review=self.review)
            .annotate(
                answer_type=F("question__answer_type"),
                category_question=F("question__category"),
                category_question_name=F("question__category__name"),
                category_question_order=F("question__category__order"),
                question_name=F("question__question"),
                question_order=F("question__order"),
                reviewee=F("question__review__reviewee"),
                reviewer=F("question__review__reviewer"),
                weight=F("question__weight"),
            )
        )

    def get_pandas_fields(self, request):
        fields = [
            pf.PKField("id", label=_("ID")),
            pf.CharField(key="answered_by", label=_("Answered By")),
            pf.TextField(key="category_question_name", label=_("Category")),
            pf.TextField(key="question_name", label=_("Question")),
            pf.FloatField(key="weight", label=_("Weight")),
            pf.EmojiRatingField(key="reviewee", label=_("Reviewee")),
            pf.EmojiRatingField(key="reviewer", label=_("Reviewer")),
            pf.EmojiRatingField(key="peers", label=_("Peers")),
            pf.CharField(key="deviation", label=_("Deviation")),
            pf.TextField(key="comment_reviewee", label=_("Comment Reviewee")),
            pf.TextField(key="comment_reviewer", label=_("Comment Reviewer")),
            pf.TextField(key="comment_peers", label=_("Comment Peers")),
        ]
        return pf.PandasFields(fields=tuple(fields))

    def get_aggregates(self, request, df):
        if df.empty:
            return {}
        aggregates = {}
        if not df["reviewee"].isnull().all():
            index = pd.notnull(df["reviewee"])
            aggregates["reviewee"] = {
                "μ": format_number(
                    round((df["reviewee"][index] * df["weight"][index]).sum() / df["weight"][index].sum())
                ),
            }
        if not df["reviewer"].isnull().all():
            index = pd.notnull(df["reviewer"])
            aggregates["reviewer"] = {
                "μ": format_number(
                    round((df["reviewer"][index] * df["weight"][index]).sum() / df["weight"][index].sum())
                ),
            }
        if not df["peers"].isnull().all():
            index = pd.notnull(df["peers"])
            aggregates["peers"] = {
                "μ": format_number(
                    round((df["peers"][index] * df["weight"][index]).sum() / df["weight"][index].sum())
                ),
            }

        return aggregates

    def get_dataframe(self, request, queryset, **kwargs):
        df1 = pd.DataFrame()
        if queryset.exists():
            if _category_question_name := request.GET.get("category_question_name", None):
                queryset = queryset.filter(category_question_name__icontains=_category_question_name)
            if _question_name := request.GET.get("question_name", None):
                queryset = queryset.filter(question_name__icontains=_question_name)

            df = pd.DataFrame(queryset.order_by("question__category__order", "question__order").values())
            df = df.apply(lambda x: apply_group_anonymized(x), axis=1)
            df["answer_number"] = pd.to_numeric(df["answer_number"], downcast="float")
            dfx = df[(pd.isnull(df["answer_number"])) & (df["group_anonymized"] == "peers")]
            df.drop(dfx.index, inplace=True)
            df["answer_number"] = df["answer_number"].where(pd.notnull(df["answer_number"]), 0.0)
            df["weighted_score"] = df.weight.astype("float") * df.answer_number
            df["category_question_name"] = df["category_question_name"].where(
                pd.notnull(df["category_question_name"]), ""
            )
            df["category_question_order"] = df["category_question_order"].where(
                pd.notnull(df["category_question_order"]), 0
            )
            df["question_order"] = df["question_order"].where(pd.notnull(df["question_order"]), 0)
            df1 = df.pivot_table(
                index=[
                    "category_question_order",
                    "category_question_name",
                    "question_order",
                    "question_id",
                    "question_name",
                ],
                columns="group_anonymized",
                values="answer_number",
                aggfunc="mean",
            )
            df2 = df.pivot_table(
                index=[
                    "category_question_order",
                    "category_question_name",
                    "question_order",
                    "question_id",
                    "question_name",
                ],
                columns="group_anonymized",
                values=["weight", "answer_text"],
                aggfunc="sum",
            )
            df1["weight"] = df2["weight"]["reviewee"].astype(float)
            _temporary_dict = {
                "reviewee": "comment_reviewee",
                "reviewer": "comment_reviewer",
                "peers": "comment_peers",
            }
            for _key, _value in _temporary_dict.items():
                if _key in df1.columns.tolist():
                    df1[_value] = df2["answer_text"][_key].apply(lambda x: x if x not in ["0", "nan"] else None)
                else:
                    df1[_key] = None
                    df1[_value] = None
            df1["deviation_value"] = abs(df1["reviewer"] - df1["reviewee"])
            df1["deviation"] = df1["deviation_value"].apply(
                lambda x: "EQUAL" if x == 0 else "LESS" if x <= 1 else "GREAT"
            )
            df1 = df1.reset_index()
            df1["id"] = df1["question_id"]
            if _deviation := request.GET.get("deviation"):
                df1 = df1[df1["deviation"] == _deviation]
                df1 = df1.reset_index()
            df1.sort_values(by=["category_question_order", "question_order"])

            def convert_to_int(x):
                try:
                    return int(x)
                except (ValueError, TypeError):
                    return x

            df1[["reviewee", "reviewer", "peers"]] = df1[["reviewee", "reviewer", "peers"]].applymap(convert_to_int)
        return df1


class ReviewProgressPandasViewSet(PandasAPIViewSet):
    IDENTIFIER = "wbhuman_resources:reviewprogress"
    queryset = ReviewAnswer.objects.all()
    display_config_class = ReviewProgressPandasDisplayConfig
    title_config_class = ReviewProgressPandasTitleConfig
    endpoint_config_class = ReviewProgressPandasEndpointConfig

    ordering_fields = ["reviewee", "reviewer"]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(question__review__status=Review.Status.FILL_IN_REVIEW)
            .annotate(
                answer_type=F("question__answer_type"),
                answered_by_name=F("answered_by__computed_str"),
                reviewee=F("question__review__reviewee"),
                reviewer=F("question__review__reviewer"),
                review=F("question__review"),
                review_name=F("question__review__computed_str"),
            )
        )

    def get_pandas_fields(self, request):
        fields = [
            pf.PKField("id", label=_("ID")),
            pf.CharField(key="review_name", label=_("Answered By")),
            pf.FloatField(key="reviewee", label=_("Reviewee"), percent=True),
            pf.FloatField(key="reviewer", label=_("Reviewer"), percent=True),
            pf.FloatField(key="peers", label=_("Peers"), percent=True),
        ]
        return pf.PandasFields(fields=tuple(fields))

    def get_dataframe(self, request, queryset, **kwargs):
        df = pd.DataFrame()
        if queryset.exists():
            df0 = pd.DataFrame(
                queryset.values(
                    "review",
                    "review_name",
                    "reviewee",
                    "reviewer",
                    "answer_type",
                    "answered_by_name",
                    "answered_by_id",
                    "answer_text",
                    "answer_number",
                )
            )
            df0 = df0.apply(lambda x: apply_group_anonymized(x), axis=1)
            df_rating = (
                df0[df0["answer_type"] == "RATING"]
                .groupby(["review", "review_name", "group_anonymized", "answered_by_name"])
                .count()
            )
            df_text = (
                df0[df0["answer_type"] == "TEXT"]
                .groupby(["review", "review_name", "group_anonymized", "answered_by_name"])
                .count()
            )
            df = pd.merge(
                df_rating[["answer_type", "answer_number"]],
                df_text[["answer_type", "answer_text"]],
                on=["review", "review_name", "group_anonymized", "answered_by_name"],
                how="outer",
            )
            df.fillna(0, inplace=True)

            df["progress"] = (df["answer_number"] + df["answer_text"]) / (df["answer_type_x"] + df["answer_type_y"])
            df.progress.fillna(0, inplace=True)
            df = df.pivot_table(
                index=["review", "review_name"], columns="group_anonymized", values="progress", aggfunc="mean"
            )
            df = df.reset_index()
            df["id"] = df["review"]
        return df
