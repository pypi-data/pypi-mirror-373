from .generator import Genertore_Devices

class Tik:
    def __init__(self):
        self.instance = Genertore_Devices()

    def GetVar(self):
        return self.instance.GetVar()


