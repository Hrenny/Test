class MyBaseFailure(Exception):
    """自定义异常类"""
    pass


class JsonpathExtractionFailed(MyBaseFailure):
    pass


class NotFoundError(MyBaseFailure):
    pass


class FileNotFound(FileNotFoundError, MyBaseFailure):
    pass


class SqlNotFound(NotFoundError):
    pass


class DataAcquisitionFailed(MyBaseFailure):
    pass


class ValueTypeError(MyBaseFailure):
    pass


class SendMessageError(MyBaseFailure):
    pass


class ValueNotFoundError(MyBaseFailure):
    pass


class AssertTypeError(MyBaseFailure):
    pass