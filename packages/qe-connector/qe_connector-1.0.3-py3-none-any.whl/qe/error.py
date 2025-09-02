class Error(Exception):
    pass


class ClientError(Error):
    def __init__(self, status_code, error_code, error_message, header, error_data=None):
        # https status code
        self.status_code = status_code
        # error code returned from server
        self.error_code = error_code
        # error message returned from server
        self.error_message = error_message
        # the whole response header returned from server
        self.header = header
        # return data if it's returned from server
        self.error_data = error_data


class APIError(Error):
    """API error matching Go's APIError struct"""
    def __init__(self, code, reason, message, trace_id=None, server_time=None):
        self.code = code
        self.reason = reason
        self.message = message
        self.trace_id = trace_id
        self.server_time = server_time
        super().__init__(self.__str__())
    
    def __str__(self):
        return f"<APIError> code={self.code}, msg={self.message}, reason={self.reason}, trace={self.trace_id}"


class ServerError(Error):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message


class ParameterRequiredError(Error):
    def __init__(self, params):
        self.params = params

    def __str__(self):
        return "%s is mandatory, but received empty." % (", ".join(self.params))


class ParameterValueError(Error):
    def __init__(self, params):
        self.params = params

    def __str__(self):
        return "the enum value %s is invalid." % (", ".join(self.params))


class ParameterTypeError(Error):
    def __init__(self, params):
        self.params = params

    def __str__(self):
        return f"{self.params[0]} data type has to be {self.params[1]}"


class ParameterArgumentError(Error):
    def __init__(self, error_message):
        self.error_message = error_message

    def __str__(self):
        return self.error_message


class WebsocketClientError(Error):
    def __init__(self, error_message):
        self.error_message = error_message

    def __str__(self):
        return self.error_message
