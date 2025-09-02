from enum import Enum


class ExitCodes(Enum):
    OK = 0
    LOADING_SUITE_ERROR = 5
    SCENARIO_CONFIG_ERROR = 6
    RUN_SCENARIO_ERROR = 7
    CONNECTION_ERROR = 8
    AUTHENTICATION_FAILED = 9
    RETRIEVE_ERROR = 10


class LoadCredentialsError(BaseException):
    pass


class LoadSuiteError(BaseException):
    pass


class LoadScenarioError(BaseException):
    pass
