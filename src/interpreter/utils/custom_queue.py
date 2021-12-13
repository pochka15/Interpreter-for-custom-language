from queue import SimpleQueue


class CustomQueue(SimpleQueue):
    def __init__(self):
        super().__init__()
        self.first = None

    def empty(self) -> bool:
        return self.first is None

    def get(self, block=..., timeout=...):
        if self.first is None:
            return super().get(block, timeout)
        else:
            out = self.first
            if not super().empty():
                self.first = super().get(block, timeout)
            else:
                self.first = None
            return out

    def get_nowait(self):
        return super().get_nowait()

    def put(self, item, block=..., timeout=...) -> None:
        if self.empty():
            self.first = item
        else:
            super().put(item, block, timeout)

    def put_nowait(self, item) -> None:
        super().put_nowait(item)

    def peek(self):
        return self.first
