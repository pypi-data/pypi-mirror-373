import sys

from cave_utils import Arguments

try:
    # Save original sys.argv
    original_argv = sys.argv.copy()

    # Mock command-line arguments
    sys.argv = ["script_name.py", "--name", "value", "-v", "-flagonly", "pos1", "--another", "-x"]

    args = Arguments()

    # Test kwargs
    assert args.get_kwarg("name") == "value", "Failed to retrieve --name=value"
    assert (
        args.get_kwarg("nonexistent", "default") == "default"
    ), "Failed default value for missing kwarg"

    # Test flags
    assert args.has_flag("v"), "Missing -v flag"
    assert args.has_flag("flagonly"), "Missing -flagonly flag"
    assert args.has_flag("x"), "Missing -x flag"

    # Test others
    assert "pos1" in args.other, "Missing positional argument 'pos1'"

    # Test delete function
    args.delete("name")
    assert args.get_kwarg("name") is None, "Failed to delete --name"

    args.delete("v", only_flag=True)
    assert not args.has_flag("v"), "Failed to delete -v flag"

    args.delete("pos1")
    assert "pos1" not in args.other, "Failed to delete positional argument 'pos1'"

    print("Arguments Tests: Passed!")

except Exception as e:
    print("Arguments Tests: Failed!")
    print(f"Error: {e}")
    raise e

finally:
    # Restore original sys.argv
    sys.argv = original_argv
