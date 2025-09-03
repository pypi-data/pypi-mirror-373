from backupchan import API
from backupchan_cli import utility

#
#
#

def setup_subcommands(subparser):
    view_cmd = subparser.add_parser("view", aliases=["show"], help="View stats")
    view_cmd.set_defaults(func=do_view)

#
# backupchan stats view
#

def do_view(args, api: API):
    stats = api.view_stats()
    print(f" | Server version: {stats.program_version}")
    print(f" | Total size of all targets: {utility.humanread_file_size(stats.total_target_size)}")
    print(f" | Total size of recycle bin: {utility.humanread_file_size(stats.total_recycle_bin_size)}")
    print(f" | Total number of targets: {stats.total_targets}")
    print(f" | Total number of backups: {stats.total_backups} ({stats.total_recycled_backups} recycled)")
