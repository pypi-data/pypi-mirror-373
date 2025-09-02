from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from wbcore import filters as wb_filters
from wbcore.contrib.directory.models import Person

from wbhuman_resources.models import (
    Review,
    ReviewAnswer,
    ReviewGroup,
    ReviewQuestion,
    ReviewQuestionCategory,
)


class ReviewGroupFilter(wb_filters.FilterSet):
    class Meta:
        model = ReviewGroup
        fields = {
            "name": ["exact", "icontains"],
        }


def get_filter_params(request, view):
    return {"related_to": request.user.profile}


def filter_default_related_to(field, request, view):
    return request.user.profile.id if request.user.profile else None


class ReviewTemplateFilter(wb_filters.FilterSet):
    related_to = wb_filters.ModelChoiceFilter(
        label=_("Related to"),
        queryset=Person.objects.all(),
        endpoint=Person.get_representation_endpoint(),
        value_key=Person.get_representation_value_key(),
        label_key=Person.get_representation_label_key(),
        method="filter_related_to",
        initial=filter_default_related_to,
    )

    def filter_related_to(self, queryset, name, value):
        if value:
            queryset = queryset.filter(Q(reviewee=value) | Q(reviewer=value) | Q(moderator=value))
        return queryset

    class Meta:
        model = Review
        fields = {
            "review": ["lte", "gte"],
            "status": ["exact"],
            "moderator": ["exact"],
            "review_group": ["exact"],
            "changed": ["lte", "gte"],
        }


class ReviewFilter(ReviewTemplateFilter):
    is_template = wb_filters.BooleanFilter(initial=False, label=_("Is Template"))

    class Meta:
        model = Review
        fields = {
            "from_date": ["lte", "gte"],
            "to_date": ["lte", "gte"],
            "review_deadline": ["lte", "gte"],
            "review": ["lte", "gte"],
            "status": ["exact"],
            "reviewee": ["exact"],
            "reviewer": ["exact"],
            "moderator": ["exact"],
            "review_group": ["exact"],
            "is_template": ["exact"],
            "year": ["exact"],
            "type": ["exact"],
            "changed": ["lte", "gte"],
        }


class ReviewQuestionCategoryFilter(wb_filters.FilterSet):
    class Meta:
        model = ReviewQuestionCategory
        fields = {
            "name": ["exact", "icontains"],
            "order": ["exact"],
            "weight": ["exact"],
        }


class ReviewQuestionFilter(wb_filters.FilterSet):
    class Meta:
        model = ReviewQuestion
        fields = {
            "review": ["exact"],
            "category": ["exact"],
            "mandatory": ["exact"],
            "answer_type": ["exact"],
            "order": ["exact"],
            "weight": ["exact"],
        }


class ReviewAnswerFilter(wb_filters.FilterSet):
    question_name = wb_filters.CharFilter(label=_("Question"), lookup_expr="icontains")

    class Meta:
        model = ReviewAnswer
        fields = {"answer_text": ["exact", "icontains"], "answered_by": ["exact"], "question": ["exact"]}
        hidden_fields = ["question"]


class ReviewProgressReviewFilter(wb_filters.FilterSet):
    class Meta:
        model = ReviewAnswer
        fields = {}


class RatingReviewAnswerReviewFilter(wb_filters.FilterSet):
    deviation = wb_filters.ChoiceFilter(
        label=_("Deviation"),
        choices=[("EQUAL", _("Equal")), ("LESS", _("Less")), ("GREAT", _("Greater"))],
        method="fake_filter",
        clearable=False,
        required=False,
    )
    category_question_name = wb_filters.CharFilter(label=_("Category"), lookup_expr="icontains")
    question_name = wb_filters.CharFilter(label=_("Question"), lookup_expr="icontains")
    answer_type = wb_filters.ChoiceFilter(
        label="Answer Type", choices=ReviewQuestion.ANSWERTYPE.choices, required=False, hidden=True
    )

    class Meta:
        model = ReviewAnswer
        fields = {}
