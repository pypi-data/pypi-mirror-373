from mchplnet.interfaces.abstract_interface import InterfaceABC


class LNetLin(InterfaceABC):
    def is_open(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def __init__(self, params=dict):
        pass

    def write(self, data):
        pass

    def read(self):
        pass
