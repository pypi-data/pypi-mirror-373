from ..exception import *

class Response:
    def __init__(self):
        self.raw_data_response = None
        self.raw_error_response = None
        self.error_code = None
        self.error_text = None

    def get_raw_data_response(self):
        return self.raw_data_response

    def set_raw_data_response(self, s: str):
        self.raw_data_response = s
        self.raw_error_response = None
        self.error_code = None
        self.error_text = None
        return self

    def get_raw_error_response(self):
        return self.raw_error_response

    def set_raw_error_response(self, s: str):
        # In format "AT1234-meaning of error code : <any other text>"
        self.raw_error_response = s
        self.raw_data_response = None

        error_code_segment = self.raw_error_response[:self.raw_error_response.index(":")].strip()
        separated_by_hyphen = error_code_segment.split("-")
        self.error_code = separated_by_hyphen[0].strip()

        self.error_text = self.raw_error_response.replace(f"{error_code_segment}:", "").strip()
        return self

    def is_error(self):
        return self.raw_error_response is not None

    def get_error_code(self):
        return self.error_code

    def get_error_text(self):
        return self.error_text

    def __str__(self):
        if self.is_error():
            return f"error:{self.raw_error_response}"
        else:
            return f"data:{self.raw_data_response}"

    def get_exception(self):
        if not self.is_error():
            return None

        if self.error_code == "AT0001":
            return AtServerRuntimeException(self.error_text)
        elif self.error_code == "AT0003":
            return AtInvalidSyntaxException(self.error_text)
        elif self.error_code == "AT0005":
            return AtBufferOverFlowException(self.error_text)
        elif self.error_code == "AT0006":
            return AtOutboundConnectionLimitException(self.error_text)
        elif self.error_code == "AT0007":
            return AtSecondaryNotFoundException(self.error_text)
        elif self.error_code == "AT0008":
            return AtHandShakeException(self.error_text)
        elif self.error_code == "AT0009":
            return AtUnauthorizedException(self.error_text)
        elif self.error_code == "AT0010":
            return AtInternalServerError(self.error_text)
        elif self.error_code == "AT0011":
            return AtInternalServerException(self.error_text)
        elif self.error_code == "AT0012":
            return AtInboundConnectionLimitException(self.error_text)
        elif self.error_code == "AT0013":
            return AtBlockedConnectionException(self.error_text)
        elif self.error_code == "AT0015":
            return AtKeyNotFoundException(self.error_text)
        elif self.error_code == "AT0016":
            return AtInvalidAtKeyException(self.error_text)
        elif self.error_code == "AT0021":
            return AtSecondaryConnectException(self.error_text)
        elif self.error_code == "AT0022":
            return AtIllegalArgumentException(self.error_text)
        elif self.error_code == "AT0023":
            return AtTimeoutException(self.error_text)
        elif self.error_code == "AT0024":
            return AtServerIsPausedException(self.error_text)
        elif self.error_code == "AT0401":
            return AtUnauthenticatedException(self.error_text)

        return AtNewErrorCodeException(self.error_code, self.error_text)
