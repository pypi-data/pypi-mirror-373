from django.db.models.signals import m2m_changed

from wbcore.dispatch import receiver_inherited_through_models

from .models.mixins import TagModelMixin


@receiver_inherited_through_models(m2m_changed, sender=TagModelMixin, through_field_name="tags")
def pre_add_tags(sender, instance, action, pk_set, **kwargs):
    from django.contrib.contenttypes.models import ContentType

    from wbcore.contrib.tags.models.tags import Tag

    if action == "post_add" and pk_set:
        content_type = ContentType.objects.get_for_model(instance)
        for tag_id in pk_set:
            tag = Tag.objects.get(id=tag_id)
            if tag.content_type and tag.content_type != content_type:
                instance.tags.remove(tag)
