
#CONSTANTS VARIABLES
TYPES = ['{record}', '{delete}', '{talk}', ]


def get_header(request):
    header, body = request.split('\n\r', 2)
    return header


def get_params(header_request):
    params = header_request.split()
    return params[1:]


def get_type(header):
    """
    return type of request if type is not recognized return -1
    :param header: str
    :return: str if success int otherwise
    """
    return header[0] if header[0] in TYPES else -1




