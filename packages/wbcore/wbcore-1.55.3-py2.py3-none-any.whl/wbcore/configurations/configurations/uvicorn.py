from configurations import values


class Uvicorn:
    UVICORN_LOOP = values.Value("auto", environ_prefix=None)
    # assert UVICORN_LOOP in ["auto", "uvloop", "asyncio"], "UVICORN_LOOP has an invalid setting"

    UVICORN_WS = values.Value("auto", environ_prefix=None)
    # assert UVICORN_WS in ["auto", "websockets", "wsproto"], "UVICORN_WS has an invalid setting"
