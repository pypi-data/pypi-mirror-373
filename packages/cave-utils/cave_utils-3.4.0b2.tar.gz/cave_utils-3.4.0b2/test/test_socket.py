from cave_utils import Socket

try:
    socket = Socket(silent=True)  # Create a silent socket instance for testing
    socket.broadcast("Test broadcast message", {"key": "value"})
    socket.notify("Test notify message", {"key": "value"})
    print("Socket Tests: Passed!")
except Exception as e:
    print("Socket Tests: Failed!")
    print(f"Error: {e}")
    raise e
