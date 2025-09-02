from configurations import values


class Gleap:
    GLEAP_API_TOKEN = values.Value("", environ_prefix=None)
    GLEAP_IDENTITY_VERIFICATION_SECRET = values.Value("", environ_prefix=None)
