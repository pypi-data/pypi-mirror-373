from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from ob_dj_store.core.stores.managers import FavoriteExtraManager, FavoriteManager
from ob_dj_store.utils.model import DjangoModelCleanMixin


class Favorite(DjangoModelCleanMixin, models.Model):
    """
    Favorite model to handle user's favorites
    """

    user = models.ForeignKey(
        get_user_model(), related_name="favorites", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200, null=True, blank=True)
    name_arabic = models.CharField(max_length=200, null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey("content_type", "object_id")
    object_id = models.PositiveIntegerField()
    extra_info = models.TextField(blank=True, null=True)
    # Audit fields
    created_on = models.DateTimeField(auto_now_add=True)
    objects = FavoriteManager()

    class Meta:
        verbose_name = _("favorite")
        verbose_name_plural = _("favorites")
        unique_together = (("name", "user"),)

    def __str__(self):
        return f"{self.user} favorites {self.content_object}"

    @classmethod
    def add_favorite(cls, content_object, user, name, extra_info=None, extras=[]):
        content_type = ContentType.objects.get_for_model(type(content_object))
        favorite = Favorite(
            user=user,
            content_type=content_type,
            object_id=content_object.pk,
            content_object=content_object,
            extra_info=extra_info,
            name=name,
        )
        favorite.save()
        for extra in extras:
            extra_content_type = ContentType.objects.get_for_model(type(extra))
            favorite.extras.create(
                content_type=extra_content_type,
                object_id=extra.id,
                content_object=extra,
            )
        return favorite

    def update_favorite(self, name, extra_info=None, extras=[]):
        from ob_dj_store.core.stores.models._favorite import FavoriteExtra

        self.name = name
        if extra_info:
            self.extra_info = extra_info
        self.save()
        FavoriteExtra.objects.filter(favorite=self).delete()
        for extra in extras:
            extra_content_type = ContentType.objects.get_for_model(type(extra))
            self.extras.create(
                content_type=extra_content_type,
                object_id=extra.id,
                content_object=extra,
            )
        return self


class FavoriteExtra(DjangoModelCleanMixin, models.Model):
    favorite = models.ForeignKey(
        Favorite, related_name="extras", on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey("content_type", "object_id")
    object_id = models.PositiveIntegerField()

    # audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = FavoriteExtraManager()

    def __str__(self):
        return f"{self.content_object}"
