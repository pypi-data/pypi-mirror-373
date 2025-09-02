class Computed:
    empty = type('empty', (), {})

    def __init__(self, func):
        self.func = func
        self.value = self.empty

    def __call__(self):
        if self.value is self.empty:
            self.value = self.func()
        return self.value
