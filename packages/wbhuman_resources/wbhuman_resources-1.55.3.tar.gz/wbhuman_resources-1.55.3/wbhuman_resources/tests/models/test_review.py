import pytest
from django.forms.models import model_to_dict
from rest_framework.test import APIRequestFactory

from wbhuman_resources.factories import EmployeeHumanResourceFactory
from wbhuman_resources.factories.kpi import (
    ReviewAnswerFactory,
    ReviewFactory,
    ReviewGroupFactory,
    ReviewQuestionFactory,
)
from wbhuman_resources.models.review import Review, create_review_from_template


@pytest.mark.django_db
class TestEmployeeReview:
    def test_get_reviewer(self):
        employee = EmployeeHumanResourceFactory()
        review = ReviewFactory(reviewee=employee.profile, reviewer=None)
        review2 = ReviewFactory(reviewer=None)
        assert review.reviewer
        assert review2.reviewer is None

    @pytest.mark.parametrize("with_data", [True, False])
    def test_create_review_from_template(self, with_data):
        if with_data:
            employee = EmployeeHumanResourceFactory()
            review_group = ReviewGroupFactory(employees=(employee.profile,))
            obj = ReviewFactory(review_group=review_group)
            data = {
                "from_date": obj.from_date,
                "to_date": obj.to_date,
                "review_deadline": obj.review_deadline,
                "auto_apply_deadline": obj.auto_apply_deadline,
                "employees": list(obj.review_group.employees.values_list("id", flat=True)),
            }
        else:
            data = {}

        api_request = APIRequestFactory()
        request = api_request.post("", data=data)
        template = ReviewFactory(is_template=True)
        from_date = request.POST.get("from_date", None)
        to_date = request.POST.get("to_date", None)
        review_deadline = request.POST.get("review_deadline", None)
        auto_apply_deadline = request.POST.get("auto_apply_deadline", None)
        employees = request.POST.get("employees", None)
        include_kpi = request.POST.get("include_kpi", None)
        nb_reviews = Review.objects.all().count()
        create_review_from_template(
            template.pk, from_date, to_date, review_deadline, auto_apply_deadline, employees, include_kpi
        )
        if with_data:
            assert Review.objects.all().count() == nb_reviews + 1
        else:
            assert Review.objects.all().count() == nb_reviews

    def test_clone_review(self):
        template = ReviewFactory(is_template=True)
        question = ReviewQuestionFactory(review=template)
        cloned = template.clone()
        dict_template = model_to_dict(template)
        dict_cloned = model_to_dict(cloned)
        assert cloned != template
        assert dict_template.pop("id") != dict_cloned.pop("id")
        assert dict_template == dict_cloned
        assert template.questions.count() == cloned.questions.count() == 1
        assert template.questions.first() != cloned.questions.first()

        dict_question = model_to_dict(question)
        dict_template_question = model_to_dict(template.questions.first())
        dict_cloned_question = model_to_dict(cloned.questions.first())

        assert question == template.questions.first() != cloned.questions.first()
        assert dict_question.pop("id") == dict_template_question.pop("id") != dict_cloned_question.pop("id")
        assert dict_question == dict_template_question != dict_cloned_question

    @pytest.mark.parametrize("status", Review.Status.names)
    def test_get_answer_categories_for_user(self, status, user_factory):
        review = ReviewFactory(is_template=False, status=status)
        user = user_factory()
        question1 = ReviewQuestionFactory(review=review)
        answer1 = ReviewAnswerFactory(question=question1)

        question2 = ReviewQuestionFactory(review=review)
        answer2 = ReviewAnswerFactory(question=question2, answered_by=user.profile)

        categories = review.get_answer_categories_for_user(user=user)
        if review.status in [Review.Status.FILL_IN_REVIEW, Review.Status.REVIEW]:
            assert categories.count() == 1
            assert categories.first() == answer2.question.category
        else:
            assert categories.count() == 2
            assert set(categories) == {answer1.question.category, answer2.question.category}

    def test_get_question_categories(self):
        review = ReviewFactory(is_template=False)
        question1 = ReviewQuestionFactory(review=review)

        categories = review.get_question_categories()

        assert categories.count() == 1
        assert categories.first() == question1.category
