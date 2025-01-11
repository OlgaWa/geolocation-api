class DBError(Exception):
    pass


class IPStackAPIConnectionError(Exception):
    pass


class AlreadyExistsError(Exception):
    pass


class NotFoundError(Exception):
    pass


class WrongDataFormatError(Exception):
    pass
