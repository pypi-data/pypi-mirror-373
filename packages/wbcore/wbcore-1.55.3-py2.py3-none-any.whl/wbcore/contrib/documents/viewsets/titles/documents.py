from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig


def get_object_by_content(content_type, content_id):
    return str(ContentType.objects.get_for_id(content_type).model_class().objects.get(id=content_id))


class DocumentModelTitleConfig(TitleViewConfig):
    def get_list_title(self):
        if (content_id := self.view.kwargs.get("content_id", None)) and (
            content_type := self.view.kwargs.get("content_type", None)
        ):
            return _("Documents for {object}").format(object=get_object_by_content(content_type, content_id))
        return _("Documents")

    def get_instance_title(self):
        return _("Document: {{name}}")

    def get_create_title(self):
        if (content_id := self.view.kwargs.get("content_id", None)) and (
            content_type := self.view.kwargs.get("content_type", None)
        ):
            return _("New Document for {object}").format(object=get_object_by_content(content_type, content_id))
        return _("New Document")
