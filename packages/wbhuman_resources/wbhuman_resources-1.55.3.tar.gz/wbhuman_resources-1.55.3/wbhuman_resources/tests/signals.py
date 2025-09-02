from django.db import connection
from django.dispatch import receiver
from wbcore.test.signals import (
    custom_update_kwargs,
    get_custom_factory,
    get_custom_serializer,
)

from wbhuman_resources.factories import (
    DefaultPersonKPIFactory,
    ReviewQuestionNoCategoryFactory,
    ReviewTemplateFactory,
)
from wbhuman_resources.models import AbsenceRequest, ReviewQuestion
from wbhuman_resources.serializers import KPIModelSerializer
from wbhuman_resources.viewsets import (
    AbsenceTablePandasViewSet,
    AbsenceTypeCountEmployeeModelViewSet,
    KPIModelViewSet,
    ReviewAnswerReviewNoCategoryModelViewSet,
    ReviewAnswerReviewPandasViewSet,
    ReviewAnswerReviewQuestionCategoryModelViewSet,
    ReviewModelViewSet,
    ReviewProgressReviewPandasViewSet,
    ReviewQuestionReviewNoCategoryModelViewSet,
    ReviewReviewGroupModelViewSet,
    ReviewTemplateModelViewSet,
)

# =================================================================================================================
#                                              CUSTOM FACTORY
# =================================================================================================================


@receiver(get_custom_factory, sender=ReviewTemplateModelViewSet)
def receive_factory_review_template(sender, *args, **kwargs):
    return ReviewTemplateFactory


@receiver(get_custom_factory, sender=ReviewQuestionReviewNoCategoryModelViewSet)
def receive_factory_review_question_no_category(sender, *args, **kwargs):
    return ReviewQuestionNoCategoryFactory


@receiver(get_custom_factory, sender=KPIModelViewSet)
def receive_factory_kpi(sender, *args, **kwargs):
    return DefaultPersonKPIFactory


# =================================================================================================================
#                                              UPDATE KWARGS
# =================================================================================================================


@receiver(custom_update_kwargs, sender=AbsenceTypeCountEmployeeModelViewSet)
def receive_kwargs_employee_absence(sender, *args, **kwargs):
    if kwargs.get("obj_factory"):
        abs_day = kwargs.get("obj_factory")
        abs_day.request.status = AbsenceRequest.Status.APPROVED
        abs_day.request.save()
        abs_day.save()
        return {"employee_id": abs_day.request.employee.id, "request_id": abs_day.request.id}
    else:
        return {}


@receiver(custom_update_kwargs, sender=ReviewTemplateModelViewSet)
@receiver(custom_update_kwargs, sender=ReviewReviewGroupModelViewSet)
@receiver(custom_update_kwargs, sender=ReviewModelViewSet)
def receive_kwargs_review(sender, *args, **kwargs):
    if (review := kwargs.get("obj_factory")) and (user := kwargs.get("user")):
        review.moderator = user.profile
        review.save()
    return {}


@receiver(custom_update_kwargs, sender=ReviewProgressReviewPandasViewSet)
@receiver(custom_update_kwargs, sender=ReviewAnswerReviewPandasViewSet)
@receiver(custom_update_kwargs, sender=ReviewAnswerReviewNoCategoryModelViewSet)
@receiver(custom_update_kwargs, sender=ReviewAnswerReviewQuestionCategoryModelViewSet)
def receive_kwargs_review_answer_question_category(sender, *args, **kwargs):
    if question_id := kwargs.get("question_id"):
        question = ReviewQuestion.objects.get(id=question_id)
        if question.category:
            return {"review_id": question.review.id, "category_id": question.category.id}
        else:
            return {"review_id": question.review.id}
    return {}


@receiver(custom_update_kwargs, sender=AbsenceTablePandasViewSet)
def receive_kwargs_employee_human_resource_absence(sender, *args, **kwargs):
    return {"request_id": None, "profile": None, "user": None, "obj_factory": None}


# =================================================================================================================
#                                              UPDATE SERIALIZER
# =================================================================================================================


@receiver(get_custom_serializer, sender=KPIModelViewSet)
def receive_serializer_kpi(sender, *args, **kwargs):
    return KPIModelSerializer


def app_pre_migration(sender, app_config, **kwargs):
    cur = connection.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")
