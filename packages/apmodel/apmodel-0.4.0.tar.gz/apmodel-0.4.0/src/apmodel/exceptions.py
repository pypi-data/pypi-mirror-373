class ActivityPubModelError(Exception):
    pass

class ModelParsingError(ActivityPubModelError):
    pass

class MissingField(ActivityPubModelError):
    pass

class InvalidField(ActivityPubModelError):
    pass