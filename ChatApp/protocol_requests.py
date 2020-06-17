CODEC = 'utf8'


class MPFCS:
    """
    Store request
    """
    # CONSTANTS VARIABLES
    TYPES = []

    def __init__(self, request):
        self.brequset = request  # Bytes string of request
        self.request = request.decode(CODEC)
        # print("GOT MESSAGE", request, "END")
        self.header = self.get_header()
        self.type = self.get_type()
        self.text = self.get_body()

    def get_header(self):
        return self.request.split('\n\r', 2)[0]

    def get_body(self):
        return self.request.split('\n\r', 2)[1] if self.type == '{talk}' else ''

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
        :return: str if success int otherwise
        """
        header = self.header.split()
        return header[0] if header[0] in self.TYPES else -1


class MPFCSRequest(MPFCS):
    TYPES = ['{record}', '{delete}', '{talk}', '{quit}', '{info}']

    def __init__(self, request):
        super().__init__(request)


class MPFCSResponse(MPFCS):
    TYPES = ['{record}', '{message}', '{update}', '{quit}', '{info}']

    def __init__(self, request):
        super().__init__(request)

    def get_body(self):
        return self.request.split('\n\r', 2)[1] if self.type == '{message}' else ''


def response_record(params=()) -> bytes:
    """
    return
    :param params: list of params
    :return: utf8 bytes string
    """
    if params:
        return bytes("{record} " + ' '.join(params) + "\n\r", CODEC)

    return bytes("{record}\n\r", CODEC)


def response_message(text: str) -> bytes:
    """
    return wrapped with the header
    :param text: str
    :return: utf8 bytes string
    """
    return bytes("{message}\n\r" + text, CODEC)


def response_info(info_dict) -> bytes:
    """
    return wrapped dict with header
    :param json: str
    :return: uts8 bytes string
    """
    header = '{info}\n\r'
    body = str(info_dict)
    return bytes(header + body, CODEC)

