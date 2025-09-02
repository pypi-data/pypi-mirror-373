from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig


class VersionTitleConfig(TitleViewConfig):
    def get_list_title(self):
        if (content_type_id := self.view.request.GET.get("content_type", None)) and (
            object_id := self.view.request.GET.get("object_id", None)
        ):
            try:
                content_type = ContentType.objects.get(id=content_type_id)
                obj = content_type.model_class().objects.get(id=object_id)
                return _("Versions For {obj}").format(obj=str(obj))
            except Exception:
                pass
        return _("Versions")
