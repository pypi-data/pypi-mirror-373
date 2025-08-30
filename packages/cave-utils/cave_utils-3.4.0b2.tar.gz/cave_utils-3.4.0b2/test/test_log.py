from cave_utils.api import LogObject
import os

x = LogObject()

try:
    x.add(path=["test"], msg="Some test error", level="error")
    x.add(path=["test"], msg="Some test warning", level="warning")
    expected = {
        "log": [
            {"path": ["test"], "msg": "Some test error", "level": "error"},
            {"path": ["test"], "msg": "Some test warning", "level": "warning"},
        ]
    }
    if x.__dict__ != expected:
        raise ValueError(f"Expected {expected}, but got {x.__dict__}")
    # Try writing logs to a file
    x.write_logs(path="./logs/test_log.txt")
    # Delete the log file after writing
    if os.path.exists("./logs/test_log.txt"):
        os.remove("./logs/test_log.txt")
        # Remove the logs directory if empty
        if not os.listdir("./logs"):
            os.rmdir("./logs")
    else:
        raise FileNotFoundError("Log file was not created as expected.")
    print("LogObject Tests: Passed!")
except Exception as e:
    print("LogObject Tests: Failed!")
    print(f"Error: {e}")
    raise e
