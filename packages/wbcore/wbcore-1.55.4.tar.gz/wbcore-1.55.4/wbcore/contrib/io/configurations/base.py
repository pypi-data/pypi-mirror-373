from configurations import values


class ImportExportBaseConfiguration:
    WBIMPORT_EXPORT_SFTPBACKEND_CLEAN_FILES = values.BooleanValue(False, environ_prefix=None)
    WBIMPORT_EXPORT_MAILBACKEND_SPAMSCORE = values.IntegerValue(None, environ_prefix=None)
    WBIMPORT_EXPORT_DEFAULT_EXPORT_PAGINATION_LIMIT = values.IntegerValue(200, environ_prefix=None)
