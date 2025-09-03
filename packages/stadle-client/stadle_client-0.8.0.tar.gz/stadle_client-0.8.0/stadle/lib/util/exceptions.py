class StadleMessageError(Exception):
    "Base for agg->client rejection errors"
    pass

class MaxAgentsReachedError(StadleMessageError):
    "Raised when connection to agg fails due to max_agents being surpassed"
    pass

class MaxRoundReachedError(StadleMessageError):
    "Raised when connection to agg fails due to max_rounds being surpassed"
    pass

class MaxSizeReachedError(StadleMessageError):
    "Raised when agg model submission fails due to max_model_size being surpassed"
    pass

class AggRejectionError(StadleMessageError):
    "Raised when agg refuses message for other reason (such as not_opt)"
    pass