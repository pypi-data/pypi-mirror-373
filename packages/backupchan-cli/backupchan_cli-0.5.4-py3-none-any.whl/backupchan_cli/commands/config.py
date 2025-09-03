import os
from backupchan_config import Config
from backupchan_cli import utility

#
#
#

def setup_subcommands(subparser):
    new_cmd = subparser.add_parser("new", help="Create a new config")
    new_cmd.add_argument("--interactive", "-i", action="store_true", help="Make a new config interactively (no need for other options)")
    new_cmd.add_argument("--host", "-H", type=str, help="Hostname of Backup-chan server")
    new_cmd.add_argument("--port", "-p", type=int, help="Port of Backup-chan server")
    new_cmd.add_argument("--api-key", "-a", type=str, help="Backup-chan API key")
    new_cmd.set_defaults(func=do_new)

    view_cmd = subparser.add_parser("view", aliases=["show"], help="View current configuration")
    view_cmd.set_defaults(func=do_view)

    reset_cmd = subparser.add_parser("reset", help="Reset current configuration")
    reset_cmd.set_defaults(func=do_reset)

#
# backupchan config new
#

def do_new(args, config: Config, _):
    if args.interactive:
        if has_argument_new_args(args):
            utility.failure("Do not pass new config values as arguments when running interactively")
        interactive_new_config(config)
    else:
        if not has_argument_new_args(args):
            utility.failure("Host, port or api key argument not passed, or run interactively")
        argument_new_config(args, config)

def has_argument_new_args(args) -> bool:
    return args.host or args.port or args.api_key

def interactive_new_config(config: Config):
    host = input("Host: ").strip().lower()
    port = input("Port: ").strip().lower()
    if not utility.is_parsable_int(port):
        utility.failure("Port must be an integer number")
    api_key = input("API key (leave blank if auth is disabled): ").strip()

    config.host = host
    config.port = port
    config.api_key = api_key
    config.save_config()

    print("Configuration saved.")

def argument_new_config(args, config: Config):
    config.host = args.host
    config.port = args.port
    config.api_key = args.api_key
    config.save_config()

    print("Configuration saved.")

#
# backupchan config view
#

def do_view(args, config: Config, _):
    if config.is_incomplete():
        utility.failure(utility.NO_CONFIG_MESSAGE)

    print(f"Host: {config.host}")
    print(f"Port: {config.port}")
    print(f"API key: {config.api_key}")

#
# backupchan config reset
#

def do_reset(args, config: Config, _):
    config.reset(True)
    print("Configuration reset.")
