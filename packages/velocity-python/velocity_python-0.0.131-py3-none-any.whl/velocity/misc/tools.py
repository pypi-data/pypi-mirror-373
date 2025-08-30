import os
import hashlib


def run_once(func, *args, **kwargs):
    """
    Executes 'func(*args, **kwargs)' only once across script runs.

    The sentinel file name is automatically generated based on the function's
    module and name. If the function is a lambda, a stable hash of its bytecode
    is used in place of a function name.
    """

    def _generate_sentinel_name(_func):
        # Use __module__ to get the name of the module where _func is defined.
        module_name = getattr(_func, "__module__", "unknown_module")
        # Use __name__ to get the function name; for lambdas, this is "<lambda>"
        function_name = getattr(_func, "__name__", "unknown_func")

        if function_name == "<lambda>":
            # For lambdas, generate a stable name from a short hash of the bytecode.
            code_hash = hashlib.md5(_func.__code__.co_code).hexdigest()
            function_name = f"lambda_{code_hash[:8]}"

        return f".has_run_once_{module_name}_{function_name}"

    # Derive the sentinel filename from the function’s identity
    sentinel_file = _generate_sentinel_name(func)

    # Check if the sentinel file exists
    if os.path.exists(sentinel_file):
        print(f"Code in '{func.__name__}' has already been run. Skipping.")
    else:
        # Execute the function for the first time
        func(*args, **kwargs)
        # Create an empty sentinel file to mark as "done"
        with open(sentinel_file, "w") as f:
            f.write("")
