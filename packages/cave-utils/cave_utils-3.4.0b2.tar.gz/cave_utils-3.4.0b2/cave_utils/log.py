import type_enforced, os


class LogObject:
    def __init__(self):
        self.log = []

    def add(self, path, msg, level="error"):
        self.log.append({"path": path, "msg": msg, "level": level})

    def get_logs(self, level=None, max_count=None):
        if level is None:
            return self.log
        assert level in ["error", "warning"], "Invalid level, must be 'error' or 'warning'"
        logs = [i for i in self.log if i["level"] == level]
        return logs[:max_count] if max_count is not None and len(logs) > max_count else logs

    @type_enforced.Enforcer
    def print_logs(self, level: str | None = None, max_count: int | None = None):
        for i in self.get_logs(level=level, max_count=max_count):
            print(f"{i['level']}: {i['path']}\n\t{i['msg']}")

    @type_enforced.Enforcer
    def write_logs(self, path: str, level: str | None = None, max_count: int | None = None):
        if path[:1] != "/":
            path = os.getcwd() + "/" + path
        path = path.replace("/./", "/")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            for i in self.get_logs(level=level, max_count=max_count):
                f.write(f"{i['level']}: {i['path']}\n\t{i['msg']}\n")


class LogHelper:
    def __init__(self, log: LogObject, prepend_path: list):
        self.log = log
        self.prepend_path = prepend_path

    def add(self, path, msg, level="error"):
        self.log.add(path=self.prepend_path + path, msg=msg, level=level)
