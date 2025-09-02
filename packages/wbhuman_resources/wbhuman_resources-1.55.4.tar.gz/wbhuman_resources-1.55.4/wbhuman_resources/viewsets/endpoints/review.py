from django.db.models import Q
from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig

from wbhuman_resources.models import Review


class ReviewGroupEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return super().get_endpoint()


class ReviewEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        if "pk" in self.view.kwargs:
            obj = Review.objects.get(id=self.view.kwargs.get("pk"))
            if (moderator := obj.moderator) and (moderator != self.request.user.profile):
                return None
            if obj.status in [Review.Status.REVIEW, Review.Status.EVALUATION, Review.Status.VALIDATION]:
                return None
        # Block click on the row to access to the view if it's not an administrator and no review is linked to this person and only has read access
        elif (
            self.request.user in Review.get_administrators()
            and not self.request.user.has_perm("wbcompliance.add_review")
            and self.request.user not in Review.get_administrators()
            and self.view.get_queryset()
            .filter(
                Q(moderator=self.request.user.profile)
                | Q(reviewer=self.request.user.profile)
                | Q(reviewee=self.request.user.profile)
            )
            .count()
            == 0
        ):
            return None
        return super().get_endpoint()

    def get_delete_endpoint(self, **kwargs):
        if "pk" in self.view.kwargs:
            obj = Review.objects.get(id=self.view.kwargs.get("pk"))
            if obj.status in [Review.Status.REVIEW, Review.Status.EVALUATION, Review.Status.VALIDATION]:
                return None
            elif obj.moderator == self.request.user.profile:
                return super().get_delete_endpoint()
        return None


class ReviewReviewGroupEndpointConfig(ReviewEndpointConfig):
    def get_endpoint(self, **kwargs):
        if review_group_id := self.view.kwargs.get("review_group_id", None):
            if "pk" in self.view.kwargs:
                obj = Review.objects.get(id=self.view.kwargs.get("pk"))
                if (moderator := obj.moderator) and (moderator != self.request.user.profile):
                    return None
                if obj.status in [Review.Status.REVIEW, Review.Status.EVALUATION, Review.Status.VALIDATION]:
                    return None
            return reverse("wbhuman_resources:reviewgroup-review-list", args=[review_group_id], request=self.request)
        return None


class ReviewQuestionCategoryEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return super().get_endpoint()


class ReviewQuestionEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return super().get_endpoint()


class ReviewQuestionReviewEndpointConfig(ReviewQuestionEndpointConfig):
    def get_endpoint(self, **kwargs):
        if review_id := self.view.kwargs.get("review_id", None):
            return reverse("wbhuman_resources:review-reviewquestion-list", args=[review_id], request=self.request)
        return None

    def get_create_endpoint(self, **kwargs):
        if review_id := self.view.kwargs.get("review_id", None):
            obj = Review.objects.get(id=review_id)
            if obj.moderator == self.request.user.profile:
                return self.get_endpoint()
        return None

    def get_delete_endpoint(self, **kwargs):
        if review_id := self.view.kwargs.get("review_id", None):
            obj = Review.objects.get(id=review_id)
            if obj.moderator == self.request.user.profile:
                if "pk" in self.view.kwargs:
                    return f'{self.get_endpoint()}{self.view.kwargs["pk"]}/'
                return super().get_delete_endpoint()
        return None


class ReviewQuestionReviewNoCategoryEndpointConfig(ReviewQuestionReviewEndpointConfig):
    def get_endpoint(self, **kwargs):
        if review_id := self.view.kwargs.get("review_id", None):
            return reverse(
                "wbhuman_resources:review-reviewquestionnocategory-list", args=[review_id], request=self.request
            )
        return None


class ReviewQuestionReviewCategoryEndpointConfig(ReviewQuestionReviewEndpointConfig):
    def get_endpoint(self, **kwargs):
        if (review_id := self.view.kwargs.get("review_id", None)) and (
            category_id := self.view.kwargs.get("category_id", None)
        ):
            return reverse(
                "wbhuman_resources:review-reviewquestioncategory-list",
                args=[review_id, category_id],
                request=self.request,
            )
        return None


class ReviewQuestionReviewQuestionCategoryEndpointConfig(ReviewQuestionEndpointConfig):
    def get_endpoint(self, **kwargs):
        if category_id := self.view.kwargs.get("category_id", None):
            return reverse(
                "wbhuman_resources:reviewquestioncategory-reviewquestion-list",
                args=[category_id],
                request=self.request,
            )
        return None


class ReviewAnswerEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return super().get_endpoint()

    def get_instance_endpoint(self, **kwargs):
        if self.instance:
            obj = self.view.get_object()
            if obj.question.review.status in [
                Review.Status.PREPARATION_OF_REVIEW,
                Review.Status.REVIEW,
                Review.Status.EVALUATION,
                Review.Status.VALIDATION,
            ]:
                return None
        return super().get_endpoint()

    def get_create_endpoint(self, **kwargs):
        return None

    def get_delete_endpoint(self, **kwargs):
        return None


class ReviewAnswerReviewNoCategoryEndpointConfig(ReviewAnswerEndpointConfig):
    def get_endpoint(self, **kwargs):
        if review_id := self.view.kwargs.get("review_id", None):
            return reverse(
                "wbhuman_resources:review-reviewanswerquestionnocategory-list", args=[review_id], request=self.request
            )
        return None


class ReviewAnswerReviewQuestionCategoryEndpointConfig(ReviewAnswerEndpointConfig):
    def get_endpoint(self, **kwargs):
        if (review_id := self.view.kwargs.get("review_id", None)) and (
            category_id := self.view.kwargs.get("category_id", None)
        ):
            return reverse(
                "wbhuman_resources:review-reviewanswerquestioncategory-list",
                args=[review_id, category_id],
                request=self.request,
            )
        return None


class ReviewProgressReviewPandasEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None


class ReviewAnswerReviewPandasEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbhuman_resources:review-reviewquestion-list",
            [self.view.kwargs["review_id"]],
            request=self.request,
        )


class ReviewProgressPandasEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None

    def get_instance_endpoint(self, **kwargs):
        return reverse("wbhuman_resources:review-list", args=[], request=self.request)
