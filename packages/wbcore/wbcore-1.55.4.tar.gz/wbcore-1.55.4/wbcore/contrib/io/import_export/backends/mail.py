import re
from datetime import datetime
from io import BytesIO, StringIO
from typing import Generator, Optional

from anymail.inbound import AnymailInboundMessage
from django.db.models import Model
from slugify import slugify
from wbcore.contrib.io.backends.abstract import AbstractDataBackend
from wbcore.contrib.io.backends.utils import register


#### IMPORTANT: If this class path change, it needs to be adapted also on the io.backends.handle_inbound function
@register("Default Mail", save_data_in_import_source=True, passive_only=True)
class DataBackend(AbstractDataBackend):
    def get_files(
        self,
        execution_time: datetime,
        file_name_regex: Optional[str] = None,
        message: Optional[AnymailInboundMessage] = None,
        import_credential: Optional[Model] = None,
        import_email_as_file: Optional[bool] = False,
        **kwargs,
    ) -> Generator[tuple[str, BytesIO], None, None]:
        """

        Args:
            execution_time: The time at which this import was called
            file_name_regex: The regex applied on the imported file for validation. Defaults to False.
            message: The AnymailInboundMessage received from the anymail inbounc
            import_credential: Import credential attached to the calling source. Defaults to None.
            import_email_as_file: If false, import the attachment as import source file. Otherwise, import the whole email as file
            **kwargs:

        Returns:

        """
        if message:
            if import_email_as_file:
                filename = f"{slugify(message.subject)}_{datetime.timestamp(execution_time)}.eml"
                yield filename, StringIO(message.as_string())
            elif file_name_regex:
                attachments = message.attachments
                attachments.extend(message.inline_attachments.values())

                for attachment in attachments:
                    f = attachment.as_uploaded_file()
                    f_name = attachment.get_filename()
                    result = re.findall(file_name_regex, f_name)
                    if len(result) > 0:
                        yield f_name, f.file
