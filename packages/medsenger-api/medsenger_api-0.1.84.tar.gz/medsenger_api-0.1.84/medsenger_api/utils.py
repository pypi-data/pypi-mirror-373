import base64
import os
import sys
from datetime import datetime

class GrpcConnectionError(Exception):
    pass


def prepare_binary(name, data):
    import magic
    type = magic.from_buffer(data, mime=True)

    return {
        "name": name,
        "base64": base64.b64encode(data).decode('utf-8'),
        "type": type
    }


def prepare_file(filename):
    import magic
    import os

    type = magic.from_file(filename, mime=True)

    with open(filename, 'rb') as file:
        answer = {
            "name": filename.split(os.sep)[-1],
            "base64": base64.b64encode(file.read()).decode('utf-8'),
            "type": type
        }

    return answer

def gts():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S - ")

def safe(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GrpcConnectionError as e:
            raise e
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(gts(), exc_type, file_name, exc_tb.tb_lineno, e, "CRITICAL")
            return None

    wrapper.__name__ = func.__name__
    return wrapper
