from wbcore.contrib.documents.models import Document


class DocumentMixin:
    @property
    def documents(self):
        return Document.get_for_object(self)

    def attach_document(self, document):
        document.link(self)
