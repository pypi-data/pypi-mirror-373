class KitchenPreviewOutdatedException(Exception):
    def __init__(self, message):
        super(KitchenPreviewOutdatedException, self).__init__(message)


class ValidationException(Exception):
    pass


class MongoDbConnectionParams(Exception):
    pass


class MongoDbConnectionParamsInvalidExtraParams(Exception):
    def __init__(self, extra_params):
        example = """'{"authSource": "$external", "authenticationMechanism": "PLAIN"}'"""
        message = f"Error loading extra_params={extra_params}.\nExpects json object like {example}"
        super().__init__(message)
