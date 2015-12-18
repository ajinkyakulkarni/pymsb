# TODO: flesh out these errors


class PyMsbSyntaxError(Exception):
    def __init__(self, line_number, line_index, message="Syntax error occured."):
        super().__init__(message)
        self.line_number = line_number
        self.line_index = line_index
        self.message = message

    def __str__(self):
        return "{0}, {1}:\t{2}".format(self.line_number, self.line_index, self.message)


class PyMsbUnexpectedTokenError(PyMsbSyntaxError):
    def __init__(self, token):
        super().__init__(token.line_number, token.line_index, "Unexpected token {0} found.".format(token.value))
        self.token = token


class PyMsbExpectedTokenError(PyMsbSyntaxError):
    def __init__(self, line_number, line_index, *expected_token_types):
        if expected_token_types:
            super().__init__(line_number, line_index, "Expected one of " + ", ".join(expected_token_types) + ".")
        else:
            super().__init__(line_number, line_index, "Unexpected end of expression.")
        self.expected_token_types = expected_token_types


class PyMsbExpectedExpressionError(PyMsbSyntaxError):
    def __init__(self, line_number, line_index):
        super().__init__(line_number, line_index, "Expected an expression here.")


class PyMsbUnrecognizedStatementError(PyMsbSyntaxError):
    def __init__(self, line_number, line_index):
        super().__init__(line_number, line_index)


class PyMsbRuntimeError(RuntimeError):
    pass


class PyMsbMalformedArrayError(PyMsbRuntimeError):
    def __init__(self, array_name, array_value):
        super().__init__()
        self.array_name = array_name
        self.array_value = array_value