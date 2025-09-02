from typing import TYPE_CHECKING, Optional

from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from wbcore.contrib.color.enums import WBColor
from wbcore.enums import Operator, Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display import (
    Display,
    Inline,
    Layout,
    Page,
    Style,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.operators import default
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbhuman_resources.models import Review, ReviewQuestion

if TYPE_CHECKING:
    from wbhuman_resources.viewsets.review import ReviewAnswerReviewPandasViewSet


def get_legends(model=None):
    list_format = []
    if model:
        for _status, color in model.Status.get_color_map():
            list_format.append(dp.LegendItem(icon=color, label=_status.label, value=_status.value))
    return [dp.Legend(key="status", items=list_format)]


def get_list_formatting(model=None):
    color_conditions = []
    if model:
        for _status, color in model.Status.get_color_map():
            color_conditions.append(
                dp.FormattingRule(condition=("==", _status.name), style={"backgroundColor": color})
            )
    return [
        dp.Formatting(column="status", formatting_rules=color_conditions),
    ]


class ReviewGroupDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label=_("Name")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [["name", "employees"], [repeat_field(2, "review_section")]],
            [create_simple_section("review_section", _("Review"), [["review"]], "review", collapsed=False)],
        )


class ReviewDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="year", label=gettext_lazy("Year"), width=Unit.PIXEL(80)),
                dp.Field(key="type", label=gettext_lazy("Type"), width=Unit.PIXEL(100)),
                dp.Field(key="reviewee", label=gettext_lazy("Reviewee"), width=Unit.PIXEL(150)),
                dp.Field(key="reviewer", label=gettext_lazy("Reviewer"), width=Unit.PIXEL(150)),
                dp.Field(key="moderator", label=gettext_lazy("Moderator"), width=Unit.PIXEL(150)),
                dp.Field(key="from_date", label=gettext_lazy("From"), width=Unit.PIXEL(140)),
                dp.Field(key="to_date", label=gettext_lazy("To"), width=Unit.PIXEL(140)),
                dp.Field(key="review_deadline", label=gettext_lazy("Deadline"), width=Unit.PIXEL(140)),
                dp.Field(key="status", label=gettext_lazy("Status"), width=Unit.PIXEL(150)),
                dp.Field(key="review", label=gettext_lazy("Review date"), width=Unit.PIXEL(140)),
                dp.Field(key="is_template", label=gettext_lazy("Is Template"), width=Unit.PIXEL(100)),
                dp.Field(key="changed", label=gettext_lazy("Changed"), width=Unit.PIXEL(140)),
                dp.Field(key="review_group", label=gettext_lazy("Group"), width=Unit.PIXEL(150)),
            ],
            legends=get_legends(Review),
            formatting=get_list_formatting(Review),
        )

    def get_main_information_page(self):
        grid_areas = [
            ["year", "type", repeat_field(2, "status")],
            ["review_group", "is_template", "moderator", "auto_apply_deadline"],
        ]
        if self.view.kwargs.get("pk"):
            instance = self.view.get_object()
            if not instance.is_template:
                grid_areas = [
                    ["year", "type", repeat_field(2, "status")],
                    ["from_date", "to_date", "review_deadline", "review"],
                    ["reviewee", "reviewer", "moderator", "auto_apply_deadline"],
                ]
            if instance.status != Review.Status.PREPARATION_OF_REVIEW:
                if self.request.user.profile in [instance.reviewer, instance.reviewee]:
                    grid_areas.append(
                        ["completely_filled_reviewee", "completely_filled_reviewer", repeat_field(2, "global_rating")]
                    )
                else:
                    grid_areas.append(
                        ["completely_filled_reviewee", "completely_filled_reviewer", repeat_field(2, ".")]
                    )

                if instance.status in [Review.Status.EVALUATION, Review.Status.VALIDATION]:
                    grid_areas.append([repeat_field(2, "signed_reviewee"), repeat_field(2, "signed_reviewer")])
                    grid_areas.append([repeat_field(2, "feedback_reviewee"), repeat_field(2, "feedback_reviewer")])

        return Page(
            title=_("Main Information"),
            layouts={
                default(): Layout(
                    grid_template_areas=grid_areas,
                ),
            },
        )

    def get_answers_page(self, instance):
        nb_columns = 4
        grid_areas = []
        sections = []
        inlines = []
        grid_template_rows = []
        if instance.status == Review.Status.PREPARATION_OF_REVIEW:
            grid_areas.append([repeat_field(nb_columns, "category_section")])
            sections.append(
                create_simple_section(
                    "category_section", _("Question Categories"), [["category"]], "category", collapsed=True
                )
            )
            categories = instance.get_question_categories()
            total, count = categories.count() + 1, 0
            for count, category in enumerate(categories, start=1):
                category_key = f"questioncategory{category.id}"
                grid_areas.append([repeat_field(nb_columns, f"{category_key}_section")])
                sections.append(
                    create_simple_section(
                        f"{category_key}_section",
                        ("({count}/{total}). {title}").format(count=count, total=total, title=category.name),
                        [[category_key]],
                        category_key,
                        collapsed=True,
                    )
                )

            grid_areas.append([repeat_field(nb_columns, "questionnocategory_section")])
            sections.append(
                create_simple_section(
                    "questionnocategory_section",
                    _("({count}/{total}). No Question Category").format(count=count + 1, total=total),
                    [["questionnocategory"]],
                    "questionnocategory",
                    collapsed=False,
                )
            )

        elif instance.status in [Review.Status.FILL_IN_REVIEW, Review.Status.REVIEW]:
            categories = instance.get_answer_categories_for_user(self.request.user)
            total, count = categories.count(), 0
            if no_category := ReviewQuestion.objects.filter(review=instance, category=None).exists():
                total += 1

            for count, category in enumerate(categories, start=1):
                category_key = f"reviewanswerquestioncategory{category.id}"
                grid_areas.append([repeat_field(nb_columns, f"{category_key}_section")])
                sections.append(
                    create_simple_section(
                        f"{category_key}_section",
                        ("({count}/{total}). {title}").format(count=count, total=total, title=category.name),
                        [[category_key]],
                        category_key,
                        collapsed=True,
                    )
                )

            if no_category:
                grid_areas.append([repeat_field(nb_columns, "reviewanswerquestionnocategory_section")])
                sections.append(
                    create_simple_section(
                        "reviewanswerquestionnocategory_section",
                        _("({count}/{total}). No Question Category").format(count=count + 1, total=total),
                        [["reviewanswerquestionnocategory"]],
                        "reviewanswerquestionnocategory",
                        collapsed=False,
                    )
                )

        elif instance.status in [Review.Status.EVALUATION, Review.Status.VALIDATION]:
            grid_areas += [
                [repeat_field(nb_columns, "rating_review_answer_section")],
                [repeat_field(nb_columns, "text_review_answer_inline")],
            ]
            sections.append(
                create_simple_section(
                    key="rating_review_answer_section",
                    title=_("Review of questions to be answered on a scale of 1 to 4"),
                    grid_template_areas=[["rating_review_answer_key"]],
                    inline_key="rating_review_answer_key",
                    collapsed=False,
                )
            )
            inlines.append(Inline(key="text_review_answer_inline", endpoint="text_review_answer_key"))
            grid_template_rows += [Style.MAX_CONTENT, Style.fr(1)]

        return Page(
            title=_("Q&A"),
            layouts={
                default(): Layout(
                    grid_template_areas=grid_areas,
                    sections=sections,
                    inlines=inlines,
                    grid_template_rows=grid_template_rows,
                ),
            },
        )

    def get_instance_display(self) -> Display:
        pages = []
        if self.view.kwargs.get("pk"):
            instance = self.view.get_object()
            pages.append(self.get_answers_page(instance))
        pages.append(self.get_main_information_page())
        return Display(pages=pages)


class ReviewTemplateDisplayConfig(ReviewDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="year", label=_("Year")),
                dp.Field(key="type", label=_("Type")),
                dp.Field(key="moderator", label=_("Moderator")),
                dp.Field(key="auto_apply_deadline", label=_("Auto Apply Deadline")),
                dp.Field(key="status", label=_("Status")),
                dp.Field(key="review", label=_("Review")),
                dp.Field(key="review_group", label=_("Group")),
                dp.Field(key="changed", label=_("Changed")),
            ],
            formatting=get_list_formatting(Review),
        )


class ReviewQuestionCategoryDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label=_("Name"), width=Unit.PIXEL(1000)),
                dp.Field(key="weight", label=_("Weight"), width=Unit.PIXEL(150)),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [["name", "weight"], [repeat_field(2, "question_section")]],
            [
                create_simple_section(
                    "question_section", _("Question"), [["reviewquestion"]], "reviewquestion", collapsed=False
                )
            ],
        )


class ReviewQuestionDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="question", label=gettext_lazy("Question"), width=Unit.PIXEL(600)),
                dp.Field(key="answer_type", label=gettext_lazy("Type"), width=Unit.PIXEL(200)),
                dp.Field(key="mandatory", label=gettext_lazy("Mandatory"), width=Unit.PIXEL(200)),
                dp.Field(
                    key="review_for",
                    label=gettext_lazy("Reviewee/ Reviewer/ Department/ Company"),
                    width=Unit.PIXEL(260),
                ),
                dp.Field(key="weight", label=gettext_lazy("Weight")),
                dp.Field(key="category", label=gettext_lazy("Category"), width=Unit.PIXEL(200), hide=True),
                dp.Field(key="review", label=gettext_lazy("Review"), hide=True),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["answer_type", "category", "review"],
                ["mandatory", "for_reviewee", "for_reviewer"],
                ["weight", "for_department_peers", "for_company_peers"],
                [repeat_field(3, "question")],
            ]
        )


class ReviewQuestionReviewDisplayConfig(ReviewQuestionDisplayConfig):
    def get_instance_display(self) -> Display:
        if self.view.review.status in [Review.Status.EVALUATION, Review.Status.VALIDATION]:
            return create_simple_display(
                [["review_answers_table"]],
                inlines=[Inline(key="review_answers_table", endpoint="review_answers_table")],
            )
        return super().get_instance_display()


class ReviewAnswerDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        FIELDS = [
            dp.Field(key="question_name", label=_("Question"), width=Unit.PIXEL(720)),
            dp.Field(key="mandatory", label=_("Mandatory"), width=Unit.PIXEL(80)),
        ]
        if self.view.get_queryset().filter(question__answer_type=ReviewQuestion.ANSWERTYPE.RATING):
            FIELDS += [dp.Field(key="answer_number", label=_("Rating"), width=Unit.PIXEL(170))]

        FIELDS += [dp.Field(key="answer_text", label=_("Comment"), width=Unit.PIXEL(720))]

        if review_id := self.view.kwargs.get("review_id"):
            review = Review.objects.get(id=review_id)
            if review.status in [Review.Status.EVALUATION, Review.Status.VALIDATION]:
                FIELDS = [
                    dp.Field(key="question_name", label=_("Question"), width=Unit.PIXEL(740)),
                    dp.Field(key="answered_by", label=_("Answered By"), width=Unit.PIXEL(140)),
                    dp.Field(key="answer_text", label=_("Comment"), width=Unit.PIXEL(740)),
                ]
        return dp.ListDisplay(fields=FIELDS)

    def get_instance_display(self) -> Display:
        grid_fields = [[repeat_field(2, "question_name")], ["mandatory", "."]]
        if self.view.kwargs.get("pk", None):
            instance = self.view.get_object()
            if instance.question.answer_type == ReviewQuestion.ANSWERTYPE.RATING:
                grid_fields += [[repeat_field(2, "answer_number")]]
        grid_fields += [[repeat_field(2, "answer_text")]]
        return create_simple_display(grid_fields)


class ReviewProgressReviewPandasDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        _fields = [
            dp.Field(key="answered_by_name", label=_("Answered By")),
            dp.Field(key="progress", label=_("Progress")),
        ]
        return dp.ListDisplay(fields=_fields)


class ReviewAnswerReviewPandasDisplayConfig(DisplayViewConfig):
    view: "ReviewAnswerReviewPandasViewSet"

    def _get_formatting_rules(self):
        return [
            dp.Formatting(
                column="deviation",
                formatting_rules=[
                    dp.FormattingRule(
                        style={
                            "backgroundColor": WBColor.YELLOW_LIGHT.value,
                        },
                        condition=dp.Condition(operator=Operator.EQUAL, value="LESS"),
                    ),
                    dp.FormattingRule(
                        style={
                            "backgroundColor": WBColor.GREEN_LIGHT.value,
                        },
                        condition=dp.Condition(operator=Operator.EQUAL, value="EQUAL"),
                    ),
                    dp.FormattingRule(
                        style={
                            "backgroundColor": WBColor.RED_LIGHT.value,
                        },
                        condition=dp.Condition(operator=Operator.EQUAL, value="GREAT"),
                    ),
                ],
            )
        ]

    def _get_legends(self):
        return [
            dp.Legend(
                key="deviation",
                items=[
                    dp.LegendItem(
                        icon=WBColor.RED_LIGHT.value,
                        label=_("Great Difference"),
                        value="GREAT",
                    ),
                    dp.LegendItem(
                        icon=WBColor.YELLOW_LIGHT.value,
                        label=_("Little Difference"),
                        value="LESS",
                    ),
                    dp.LegendItem(
                        icon=WBColor.GREEN_LIGHT.value,
                        label=_("Equal"),
                        value="EQUAL",
                    ),
                ],
            ),
        ]

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        hide_rating = self.request.GET.get("answer_type") == ReviewQuestion.ANSWERTYPE.TEXT
        fields = [
            dp.Field(key="category_question_name", label=_("Category"), width=Unit.PIXEL(200), hide=True),
            dp.Field(key="question_name", label=_("Question"), width=Unit.PIXEL(780)),
        ]
        if self.view.review.moderator == self.view.request.user.profile:
            fields.append(dp.Field(key="weight", label=_("Weight")))
        fields += [
            dp.Field(key="reviewee", label=_("Reviewee"), hide=hide_rating),
            dp.Field(key="reviewer", label=_("Reviewer"), hide=hide_rating),
            dp.Field(key="peers", label=_("Peers"), hide=True),
            dp.Field(key="comment_reviewee", label=_("Reviewee"), width=Unit.PIXEL(450)),
            dp.Field(key="comment_reviewer", label=_("Reviewer"), width=Unit.PIXEL(450)),
            dp.Field(key="comment_peers", label=_("Peers"), width=Unit.PIXEL(450), hide=True),
        ]
        return (
            dp.ListDisplay(fields=fields)
            if hide_rating
            else dp.ListDisplay(fields=fields, formatting=self._get_formatting_rules(), legends=self._get_legends())
        )


class ReviewProgressPandasDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        _fields = [
            dp.Field(key="review_name", label=_("Review"), width=Unit.PIXEL(800)),
            dp.Field(key="reviewee", label=_("Reviewee")),
            dp.Field(key="reviewer", label=_("Reviewer")),
            dp.Field(key="peers", label=_("Peers")),
        ]
        return dp.ListDisplay(fields=_fields)
