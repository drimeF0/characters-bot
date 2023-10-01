from typing import Any


class FixedSizeArray:
    def __init__(self, max_size, on_pop_func=None):
        self.max_size = max_size
        self.arr = []
        self.on_pop_func = on_pop_func if on_pop_func else lambda x: None

    def append(self, item):
        if len(self.arr) >= self.max_size:
            self.on_pop_func(self.arr.pop(0))
        self.arr.append(item)
    
    def clear(self):
        self.arr.clear()

def split_command(message):
    cmd = message.text.split(" ",1)
    if len(cmd) <= 1:
        return
    return cmd