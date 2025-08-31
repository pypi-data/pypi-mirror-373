# encoding=utf-8

import uuid

def parse_int(value=""):
    try:
        return int(value)
    except:
        return 0


def parse_float(value=""):
    try:
        return float(value)
    except:
        return 0.0
    

def create_random_int64():
    """创建一个随机的int64值"""
    mask = (1<<64)-1
    id_value = uuid.uuid4().int
    return id_value & mask

class IntCounter:
    MAX_VALUE = 2**31 - 1

    def __init__(self, value=0):
        self.value = value

    def _reset_if_overflow(self):
        if self.value > self.MAX_VALUE:
            self.value = 0

    def add(self, value=1):
        self.value += value
        self._reset_if_overflow()

    def __radd__(self, value:int):
        self.value += value
        self._reset_if_overflow()