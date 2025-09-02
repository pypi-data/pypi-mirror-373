from django.utils.translation import gettext as _
from wbcore.metadata.configs.titles import TitleViewConfig

from wbhuman_resources.models import Review, ReviewGroup, ReviewQuestionCategory


class ReviewTemplateTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Review Templates")


class ReviewReviewGroupTitleConfig(TitleViewConfig):
    def get_list_title(self):
        if review_group_id := self.view.kwargs.get("review_group_id"):
            review_group = ReviewGroup.objects.get(id=review_group_id)
            return _("Review Group: {review_group}").format(review_group=review_group.name)
        return super().get_list_title()


class ReviewQuestionReviewQuestionCategoryTitleConfig(TitleViewConfig):
    def get_list_title(self):
        if category_id := self.view.kwargs.get("category_id"):
            category = ReviewQuestionCategory.objects.get(id=category_id)
            return _("Review Question Category: {category}").format(category=category.name)
        return super().get_list_title()


class ReviewQuestionReviewTitleConfig(TitleViewConfig):
    def get_list_title(self):
        if review_id := self.view.kwargs.get("review_id"):
            review = Review.objects.get(id=review_id)
            return _("Review: {review}").format(review=str(review))
        return super().get_list_title()


class ReviewAnswerReviewTitleConfig(TitleViewConfig):
    def get_list_title(self):
        if review_id := self.view.kwargs.get("review_id"):
            review = Review.objects.get(id=review_id)
            return _("Review: {review}").format(review=str(review))
        return super().get_list_title()


class ReviewProgressReviewPandasTitleConfig(TitleViewConfig):
    def get_list_title(self):
        if review_id := self.view.kwargs.get("review_id"):
            review = Review.objects.get(id=review_id)
            return _("Progress of the review : {review}").format(review=str(review))
        return _("Progress of the review")


class ReviewAnswerReviewPandasTitleConfig(TitleViewConfig):
    def get_list_title(self):
        if review_id := self.view.kwargs.get("review_id"):
            review = Review.objects.get(id=review_id)
            return _("Evaluation of the review : {review}").format(review=str(review))
        return _("Evaluation of the review")


class ReviewProgressPandasTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Progress of Reviews")
