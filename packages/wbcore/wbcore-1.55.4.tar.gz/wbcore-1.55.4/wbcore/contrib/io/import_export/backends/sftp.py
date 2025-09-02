import io
import logging
import re
from datetime import datetime
from io import BytesIO
from typing import Generator, Optional

import fabric
from django.conf import settings
from paramiko.ssh_exception import SSHException
from wbcore.contrib.io.backends.abstract import AbstractDataBackend
from wbcore.contrib.io.backends.utils import register
from wbcore.contrib.io.models import ImportCredential

logger = logging.getLogger("io")


@register("SFTP", save_data_in_import_source=True, passive_only=True)
class DataBackend(AbstractDataBackend):
    def __init__(
        self,
        import_credential: Optional[ImportCredential] = None,
        **kwargs,
    ):
        if not import_credential:
            raise ValueError("The sftp backend needs an import credential")

        self.username = import_credential.username
        self.password = import_credential.password
        self.host = import_credential.additional_resources.get("host", "")
        self.port = import_credential.additional_resources.get("port", "")
        super().__init__(**kwargs)

    def get_files(
        self,
        execution_time: datetime,
        sftp_folder,
        file_name_regex: Optional[str] = None,
        cleanup_files: Optional[bool] = getattr(settings, "WBIMPORT_EXPORT_SFTPBACKEND_CLEAN_FILES", False),
        **kwargs,
    ) -> Generator[tuple[str, BytesIO], None, None]:
        # Create Connection to the SFTP Server
        with fabric.Connection(
            host=self.host, port=self.port, user=self.username, connect_kwargs={"password": self.password}
        ) as conn:
            try:
                sftp = conn.sftp()
                # Change working directory
                sftp.chdir(sftp_folder)

                # Filter all the files we need
                file_names = sftp.listdir()
                if file_name_regex:
                    # Compile the regex for later filtering the files
                    file_names = filter(lambda x: re.match(file_name_regex, x), file_names)

                for file_name in file_names:
                    # Create a Buffer where we write the file to
                    sftp_file = io.BytesIO()
                    sftp.getfo(file_name, sftp_file)
                    yield file_name, sftp_file

                    if cleanup_files:
                        # Delete the file from the server
                        sftp.remove(file_name)
            except SSHException as e:
                logger.warning(
                    f"While fetching file from data backend {self.data_backend}, we encountered a SSH Exception: {e}"
                )
