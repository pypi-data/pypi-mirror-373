

class MangledMessageError(ValueError):
    def __init__(self, ctx):
        self._ctx = ctx


class JSONParseError(MangledMessageError):
    def __init__(self, ctx):
        super(JSONParseError, self).__init__(ctx)
