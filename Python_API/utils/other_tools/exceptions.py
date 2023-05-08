class MyBaseFailure(Exception):
    pass


class ValueNotFoundError(MyBaseFailure):
    pass


class AssertTypeError(MyBaseFailure):
    pass