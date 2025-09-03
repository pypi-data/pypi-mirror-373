from .commands import config, target, backup, log, recyclebin, stats, preset
from .utility import failure, NO_CONFIG_MESSAGE
from backupchan_config import Config, ConfigException
from backupchan_presets import Presets
from backupchan import API
import argparse

def main():
    parser = argparse.ArgumentParser(prog="backupchan")
    subparsers = parser.add_subparsers(dest="command")

    config_parser = subparsers.add_parser("config")
    config_sub = config_parser.add_subparsers(dest="subcommand", help="View and edit configuration")
    config.setup_subcommands(config_sub)

    target_parser = subparsers.add_parser("target")
    target_sub = target_parser.add_subparsers(dest="subcommand", help="View and manage targets")
    target.setup_subcommands(target_sub)

    backup_parser = subparsers.add_parser("backup")
    backup_sub = backup_parser.add_subparsers(dest="subcommand", help="Add and manage backups")
    backup.setup_subcommands(backup_sub)

    log_parser = subparsers.add_parser("log")
    log_sub = log_parser.add_subparsers(dest="subcommand", help="View the execution log")
    log.setup_subcommands(log_sub)

    recycle_bin_parser = subparsers.add_parser("recyclebin")
    recycle_bin_sub = recycle_bin_parser.add_subparsers(dest="subcommand", help="View and clear the recycle bin")
    recyclebin.setup_subcommands(recycle_bin_sub)

    stats_parser = subparsers.add_parser("stats")
    stats_sub = stats_parser.add_subparsers(dest="subcommand", help="View statistics")
    stats.setup_subcommands(stats_sub)

    preset_parser = subparsers.add_parser("preset")
    preset_sub = preset_parser.add_subparsers(dest="subcommand", help="View, manage and run backup presets")
    preset.setup_subcommands(preset_sub)

    backup_presets = Presets()
    backup_presets.load()

    app_config = Config()
    try:
        app_config.read_config()
    except ConfigException:
        app_config.reset()
        pass

    api = None if app_config.is_incomplete() else API(app_config.host, app_config.port, app_config.api_key)

    args = parser.parse_args()
    if hasattr(args, "func"):
        if args.command != "config" and app_config.is_incomplete():
            failure(NO_CONFIG_MESSAGE)

        if args.command == "preset":
            args.func(args, backup_presets, api)
        elif args.command == "config":
            args.func(args, app_config, api)
        else:
            args.func(args, api)
    else:
        parser.print_help()

    return 0
