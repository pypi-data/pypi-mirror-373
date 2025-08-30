from cave_utils import Validator, Socket
import os, importlib

# for each file in the examples folder, load the execute_command function and call it to get example data
# Then validate the data using the Validator class


success = True
try:

    def get_examples():
        # Return all the examples in the cave_api/examples folder
        examples_location = "./test/api_examples"
        if not os.path.exists(examples_location):
            raise FileNotFoundError(f"Examples directory {examples_location} does not exist.")
        if not os.path.isdir(examples_location):
            raise NotADirectoryError(f"Examples location {examples_location} is not a directory.")
        # List all Python files in the examples directory, excluding __init__.py and other non-Python files
        return sorted(
            [
                i.replace(".py", "")
                for i in os.listdir(examples_location)
                if i.endswith(".py") and not i.startswith("__")
            ]
        )

    example_files = get_examples()
    for example_file in example_files:
        # Import the module dynamically
        module_name = f"api_examples.{example_file}"
        # Only import files that can be imported. If they fail on import, skip them
        try:
            module = importlib.import_module(module_name, package="test")
        except ImportError as e:
            continue
        # Check if the module has an `execute_command` function
        if hasattr(module, "execute_command"):
            # Call the function to get example data
            example_data = module.execute_command(
                session_data={}, socket=Socket(silent=True), command="init"
            )
            x = Validator(
                session_data=example_data,
            )
            if not x.log.log == []:
                # print(f"Validator for {module_name} failed with errors: {x.log.log}")
                success = False
        else:
            raise AttributeError(
                f"Module {module_name} does not have an `execute_command` function."
            )
    if not success:
        raise Exception(
            "Validator tests failed for one or more examples. Uncomment the print statements in test/test_validator.py to see the errors."
        )
    print(f"Validator Tests: Passed!")
except Exception as e:
    print(f"Validator Tests: Failed!")
    print(f"Error: {e}")
