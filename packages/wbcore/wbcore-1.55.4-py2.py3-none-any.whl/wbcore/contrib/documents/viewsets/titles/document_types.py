from django.utils.translation import gettext as _

from wbcore.metadata.configs.titles import TitleViewConfig


class DocumentTypeModelTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Document Types")

    def get_instance_title(self):
        return _("Document Type: {{name}}")

    def get_create_title(self):
        return _("New Document Type")
