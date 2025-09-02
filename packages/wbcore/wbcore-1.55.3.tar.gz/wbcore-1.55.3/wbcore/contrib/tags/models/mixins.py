from django.db import models


class TagModelMixin(models.Model):
    tag_detail_endpoint = models.CharField(max_length=255, null=True, blank=True)
    tag_representation = models.CharField(max_length=512, null=True, blank=True)
    tags = models.ManyToManyField(
        to="tags.Tag",
        related_name="%(app_label)s_%(class)s_items",
        blank=True,
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.__class__.objects.filter(id=self.id).update(
            tag_detail_endpoint=self.get_tag_detail_endpoint(),
            tag_representation=self.get_tag_representation(),
        )

    def get_tag_detail_endpoint(self):
        raise NotImplementedError("When using Tags, you must implement get_tag_detail_endpoint")

    def get_tag_representation(self):
        raise NotImplementedError("When using Tags, you must implement get_tag_representation")

    class Meta:
        abstract = True
