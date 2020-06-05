


class MPFCSRequest:
    """
    Store request
    """
    # CONSTANTS VARIABLES
    TYPES = ['{record}', '{delete}', '{talk}', ]

    def __init__(self, request):
        self.brequset = request  # Bytes string of request
        self.request = request.decode('utf8')
        self.header = self.get_header()
        self.type = self.get_type()
        self.text = self.get_body()

    def get_header(self):
        return self.request.split('\n\r', 2)[0]

    def get_body(self):
        return self.request.split('\r\n', 2)[1] if self.type == '{talk}' else ''

    def get_params(self):
        """
        get parameters attached to header
        :return: list of params
        """
        params = self.header.split()
        if len(params) > 1:
            return params[1:]
        return []

    def get_type(self):
        """
        return type of request if type is not recognized return -1
        :param header: str
        :return: str if success int otherwise
        """
        return self.header[0] if self.header[0] in self.TYPES else -1


def response_record(params: list) -> bytes:
    """
    return
    :param params: list of params
    :return: bytes string
    """
    if params:
        return bytes("{record} " + ' '.join(params) + "\n\r")

    return bytes("{record}\n\r")


def response_message(text: str) -> bytes:
    """
    return wrapped with the header
    :param text: str
    :return: bytes string
    """
    return bytes("{message}\n\r" + text)
