import sys

NO_CONFIG_MESSAGE = "No configuration. Run `backupchan config new' to configure."

def is_parsable_int(number_str: str) -> bool:
    try:
        int(number_str)
        return True
    except ValueError:
        return False

def failure(message: str):
    print(f"{message}. Halting.", file=sys.stderr)
    sys.exit(1)

def failure_network():
    failure("Failed to connect to server")

SIZE_UNITS = [
    "B", "KiB", "MiB", "GiB", "TiB"
]

def humanread_file_size(size: float):
    i = 0
    while size > 1024:
        size /= 1024
        i += 1
    return f"{size:.2f} {SIZE_UNITS[i]}"

def required_args(args_object, *args):
    for arg in args:
        if not getattr(args_object, arg):
            failure(f"Argument '{arg}' is required")
