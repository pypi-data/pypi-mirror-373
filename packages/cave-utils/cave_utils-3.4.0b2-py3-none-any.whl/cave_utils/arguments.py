import sys


class Arguments:
    def __init__(self):
        self.passed_args = list(sys.argv)
        self.populate_data()

    def populate_data(self):
        self.kwargs = {}
        self.flags = []
        self.other = []
        skip_next = True  # Skip the first argument, which is the file name
        for idx, i in enumerate(self.passed_args):
            if skip_next:
                skip_next = False
                continue
            if i.lower().startswith("--"):
                if idx + 1 >= len(self.passed_args):
                    self.flags.append(i[2:])
                    continue
                else:
                    if self.passed_args[idx + 1].lower().startswith("-"):
                        self.flags.append(i[2:])
                        continue
                self.kwargs[i[2:]] = self.passed_args[idx + 1]
                skip_next = True
            elif i.lower().startswith("-"):
                self.flags.append(i[1:])
            else:
                self.other.append(i)

    def get_kwarg(self, key, default=None):
        return self.kwargs.get(key, default)

    def has_flag(self, key):
        return key in self.flags

    def delete(self, key, silent=False, only_flag=False):
        if key not in self.kwargs and key not in self.flags and key not in self.other:
            if not silent:
                print(f"Key {key} not found in arguments")
            return
        for idx, i in enumerate(self.passed_args):
            if i == f"--{key}" or i == f"-{key}" or i == key:
                del self.passed_args[idx]
                if key in self.kwargs and not only_flag:
                    del self.passed_args[idx]
                break
        self.populate_data()

    def get_arg_list(self):
        return self.passed_args
