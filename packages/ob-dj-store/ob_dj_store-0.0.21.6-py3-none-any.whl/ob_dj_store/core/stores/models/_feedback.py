from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from ob_dj_store.core.stores.managers import FeedbackAttributeManager


class FeedbackConfig(models.Model):

    attribute = models.CharField(max_length=100, unique=True)
    attribute_label = models.CharField(max_length=200, null=True, blank=True)
    values = models.JSONField()


class Feedback(models.Model):
    class Reviews(models.TextChoices):
        GOOD = "GOOD", _("Good")
        BAD = "BAD", _("Bad")
        NOT_AVAILABLE = "NOT_AVAILABLE", _("not available")

    user = models.ForeignKey(
        get_user_model(), related_name="feedbacks", on_delete=models.CASCADE
    )
    order = models.ForeignKey(
        "stores.Order", related_name="feedbacks", on_delete=models.CASCADE,
    )
    review = models.CharField(
        max_length=100, choices=Reviews.choices, default="NOT_AVAILABLE"
    )
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class FeedbackAttribute(models.Model):
    feedback = models.ForeignKey(
        Feedback, on_delete=models.CASCADE, related_name="attributes"
    )
    config = models.ForeignKey(FeedbackConfig, on_delete=models.CASCADE)
    value = models.CharField(max_length=100, blank=True)
    review = models.CharField(max_length=100, choices=Feedback.Reviews.choices)

    objects = FeedbackAttributeManager()
