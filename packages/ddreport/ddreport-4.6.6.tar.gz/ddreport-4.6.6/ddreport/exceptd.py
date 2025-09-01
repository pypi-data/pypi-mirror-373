from .handle import Process


class RaiseInfo(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ExceptInfo:
    def __init__(self, q_data, e_data=None):
        self.P = Process()
        self.P.data_process(q_data, e_data)

    def raised(self):
        raise RaiseInfo(self.P)
