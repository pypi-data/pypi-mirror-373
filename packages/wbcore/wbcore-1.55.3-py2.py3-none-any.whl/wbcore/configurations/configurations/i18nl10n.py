from configurations import values


class I18NL10N:
    MODELTRANS_AVAILABLE_LANGUAGES = ["en", "de", "fr"]
    TIME_ZONE = values.Value("Europe/Berlin", environ_prefix=None)
    LANGUAGE_CODE = values.Value("en-us", environ_prefix=None)
    USE_TZ = values.BooleanValue(True, environ_prefix=None)
    USE_I18N = values.BooleanValue(
        True, environ_prefix=None
    )  # Setting to True lead to a big performance hit when resolver needs to translate url
