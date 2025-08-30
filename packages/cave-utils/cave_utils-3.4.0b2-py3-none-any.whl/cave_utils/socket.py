class Socket:
    def __init__(self, silent=False):
        self.silent = silent

    def broadcast(self, *args, **kwargs):
        if not self.silent:
            print("broadcast: ", {"args": args, "kwargs": kwargs})

    def notify(self, *args, **kwargs):
        if not self.silent:
            print("notify: ", {"args": args, "kwargs": kwargs})
