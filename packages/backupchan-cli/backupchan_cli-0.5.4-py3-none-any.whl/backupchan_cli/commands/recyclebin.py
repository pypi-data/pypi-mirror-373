from backupchan import API
from .backup import print_backup
from backupchan_cli import utility

#
#
#

def setup_subcommands(subparser):
    view_cmd = subparser.add_parser("view", aliases=["show"], help="View recycle bin")
    view_cmd.set_defaults(func=do_view)

    clear_cmd = subparser.add_parser("clear", help="Clear recycle bin")
    clear_cmd.add_argument("--delete-files", "-d", action="store_true", help="Delete backup files as well")
    clear_cmd.set_defaults(func=do_clear)

#
# backupchan recyclebin view
#

def do_view(args, api: API):
    try:
        backups = api.list_recycled_backups()
    except requests.exceptions.ConnectionError:
        utility.failure_network()

    for index, backup in enumerate(backups):
        spaces = " " * (len(str(index + 1)) + 1)
        print_backup(backup, spaces, False, index)

#
# backupchan recyclebin clear
#

def do_clear(args, api: API):
    try:
        api.clear_recycle_bin(args.delete_files)
    except requests.exceptions.ConnectionError:
        utility.failure_network()

    print("Recycle bin cleared.")
