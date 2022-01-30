class ParameterError(Exception):
    def __init__(self, valid_parameters, bad_parameter):
        self.valid_parameters = valid_parameters
        self.bad_parameter = bad_parameter

    def __str__(self):
        return repr(f"""Valid Option: {self.valid_parameters}. Option Provided: {self.bad_parameter}""")


class MissingCredentialsError(Exception):
    def __init__(
        self,
    ):
        pass

    def __str__(self):
        return repr(
            f"""Your credentials are missing. Try KonoPyUtil.set_credentials() to set an environment variable named DB_CREDENTIALS."""
        )
