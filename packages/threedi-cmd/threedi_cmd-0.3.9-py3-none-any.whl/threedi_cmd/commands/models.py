from enum import Enum


class EndpointChoices(str, Enum):
    localhost = "localhost"
    staging = "staging"
    production = "production"
