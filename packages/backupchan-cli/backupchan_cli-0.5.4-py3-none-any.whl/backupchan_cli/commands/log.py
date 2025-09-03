from backupchan import API

#
#
#

def setup_subcommands(subparser):
    view_cmd = subparser.add_parser("view", aliases=["show"], help="View server's execution log")
    view_cmd.add_argument("--tail", "-t", type=int, help="Trim log to show this many last lines", default=0)
    view_cmd.set_defaults(func=do_view)

#
# backupchan log view
#

def do_view(args, api: API):
    print(api.get_log(args.tail))
