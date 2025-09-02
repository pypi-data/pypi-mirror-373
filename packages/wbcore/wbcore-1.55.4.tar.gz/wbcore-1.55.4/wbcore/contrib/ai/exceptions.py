from langchain_core.exceptions import LangChainException, OutputParserException

APIStatusErrors = [LangChainException, OutputParserException]
BadRequestErrors = []

try:
    from openai._exceptions import (
        AuthenticationError,
        BadRequestError,
        ConflictError,
        InternalServerError,
        NotFoundError,
        PermissionDeniedError,
        RateLimitError,
        UnprocessableEntityError,
    )

    APIStatusErrors.extend(
        [
            AuthenticationError,
            PermissionDeniedError,
            NotFoundError,
            ConflictError,
            UnprocessableEntityError,
            RateLimitError,
            InternalServerError,
        ]
    )
    BadRequestErrors.append(BadRequestError)
except ImportError:
    pass


try:
    from anthropic._exceptions import APIConnectionError, APIResponseValidationError, APIStatusError, BadRequestError

    APIStatusErrors.extend([APIResponseValidationError, APIStatusError, APIConnectionError])
    BadRequestErrors.append(BadRequestError)
except ImportError:
    pass
