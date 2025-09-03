import requests
from backupchan_cli import utility
from .backup import print_backup
from backupchan import API, BackupType, BackupRecycleCriteria, BackupTarget, BackupRecycleAction, BackupchanAPIError

#
# Utilities
#

def print_target(target: BackupTarget, spaces: str | None, index: int):
    prefix = "" if spaces is None else f" {spaces} | "
    if spaces is None:
        print(f"Name: {target.name}")
    else:
        print(f" {index + 1}. |  {target.name}")
    if target.alias is not None:
        print(f"{prefix}Alias: {target.alias}")
    print(f"{prefix}ID: {target.id}")
    print(f"{prefix}Type: {HR_TYPES[target.target_type]}")
    print(f"{prefix}Recycle criteria: {hr_recycle_criteria(target)}")
    if target.recycle_criteria != BackupRecycleCriteria.NONE:
        print(f"{prefix}Recycle action: {HR_RECYCLE_ACTIONS[target.recycle_action]}")
    print(f"{prefix}Location: {target.location}")
    print(f"{prefix}Name template: {target.name_template}")
    print(f"{prefix}Deduplication {'on' if target.deduplicate else 'off'}")
    print("=========")

#
#
#


def setup_subcommands(subparser):
    #
    #
    #

    list_cmd = subparser.add_parser("list", help="List all targets")
    list_cmd.add_argument("--page", "-p", type=int, default=1, help="Page in the list")
    list_cmd.set_defaults(func=do_list)

    #
    #
    #

    view_cmd = subparser.add_parser("view", aliases=["show"], help="View a specific target")
    view_cmd.add_argument("id", type=str, help="ID of the target to view")
    view_cmd.add_argument("--include-recycled", "-r", action="store_true", help="Include recycled backups too")
    view_cmd.set_defaults(func=do_view)

    #
    #
    #

    new_cmd = subparser.add_parser("new", help="Create a new target")
    new_cmd.add_argument("--name", "-n", type=str, help="Name of the new target")
    new_cmd.add_argument("--type", "-t", type=lambda t: BackupType(t), choices=list(BackupType), help="Type of the new target")
    new_cmd.add_argument("--recycle-criteria", "-c", type=lambda c: BackupRecycleCriteria(c), choices=list(BackupRecycleCriteria), help="Recycle criteria")
    new_cmd.add_argument("--recycle-value", "-v", type=int, help="Recycle value (optional if criteria is none)")
    new_cmd.add_argument("--recycle-action", "-a", type=lambda a: BackupRecycleAction(a), choices=list(BackupRecycleAction), help="Recycle action")
    new_cmd.add_argument("--location", "-l", type=str, help="Location of the new target")
    new_cmd.add_argument("--name-template", "-m", type=str, help="Name template for backups. Must include either $I or $D, or both.")
    new_cmd.add_argument("--deduplicate", "-d", action="store_true", help="(optional) Enable deduplication")
    new_cmd.add_argument("--alias", type=str, help="(optional) Target alias. It can be used as the ID.")
    new_cmd.set_defaults(func=do_new)

    #
    #
    #

    delete_cmd = subparser.add_parser("delete", help="Delete an existing target")
    delete_cmd.add_argument("id", type=str, help="ID of the target to delete")
    delete_cmd.add_argument("--delete-files", "-d", action="store_true", help="Delete backup files as well")
    delete_cmd.set_defaults(func=do_delete)

    #
    #
    #

    edit_cmd = subparser.add_parser("edit", help="Edit an existing target")
    edit_cmd.add_argument("id", type=str, help="ID of the target to edit")
    edit_cmd.add_argument("--name", "-n", type=str, help="New name of the target")
    edit_cmd.add_argument("--recycle-criteria", "-c", type=lambda c: BackupRecycleCriteria(c), choices=list(BackupRecycleCriteria), help="New recycle criteria")
    edit_cmd.add_argument("--recycle-value", "-v", type=int, help="New recycle value")
    edit_cmd.add_argument("--recycle-action", "-a", type=lambda a: BackupRecycleAction(a), choices=list(BackupRecycleAction), help="New recycle action")
    edit_cmd.add_argument("--location", "-l", type=str, help="New location of the target")
    edit_cmd.add_argument("--name-template", "-m", type=str, help="New name template of the target")
    edit_cmd.add_argument("--toggle-deduplication", "-d", action="store_true", help="Toggle target deduplication")
    edit_cmd.add_argument("--alias", type=str, help="Target alias")
    edit_cmd.add_argument("--remove-alias", action="store_true", help="Remove alias from the target if it has one")
    edit_cmd.set_defaults(func=do_edit)

    #
    #
    #

    delete_backups_cmd = subparser.add_parser("deletebackups", help="Delete all backups of a target")
    delete_backups_cmd.add_argument("id", type=str, help="ID of the target to delete backups of")
    delete_backups_cmd.add_argument("--delete-files", "-d", action="store_true", help="Delete backup files as well")
    delete_backups_cmd.set_defaults(func=do_delete_backups)

#
# Value to human-readable string conversions and lookup tables
#

HR_TYPES = {
    BackupType.SINGLE: "Single file",
    BackupType.MULTI: "Multiple files"
}

HR_RECYCLE_ACTIONS = {
    BackupRecycleAction.DELETE: "Delete",
    BackupRecycleAction.RECYCLE: "Recycle"
}

def hr_recycle_criteria(target: BackupTarget) -> str:
    if target.recycle_criteria == BackupRecycleCriteria.NONE:
        return "None"
    elif target.recycle_criteria == BackupRecycleCriteria.AGE:
        return f"After {target.recycle_value} days"
    elif target.recycle_criteria == BackupRecycleCriteria.COUNT:
        return f"After {target.recycle_value} copies"
    return "(broken value)"

#
# backupchan target list
#

def do_list(args, api: API):
    try:
        targets = api.list_targets(args.page)
    except requests.exceptions.ConnectionError:
        utility.failure_network()

    print(f"Showing page {args.page}\n")

    if not targets:
        print("There are no targets.")
        return

    for index, target in enumerate(targets):
        spaces = " " * (len(str(index + 1)) + 1)
        print_target(target, spaces, index)

#
# backupchan target view
#

def do_view(args, api: API):
    try:
        target, backups = api.get_target(args.id)
    except requests.exceptions.ConnectionError:
        utility.failure_network()
    except BackupchanAPIError as exc:
        if exc.status_code == 404:
            utility.failure("Target not found")
        raise

    print_target(target, None, 0)

    if len(backups) == 0:
        print("This target has no backups.")
        return
    elif args.include_recycled:
        print("Backups:")
    else:
        print("Backups (pass -r to view recycled ones too):")
    print()

    if not args.include_recycled:
        backups = [backup for backup in backups if not backup.is_recycled]

    for index, backup in enumerate(backups):
        spaces = " " * (len(str(index + 1)) + 1)
        print_backup(backup, spaces, args.include_recycled, index)

#
# backupchan target new
#

def do_new(args, api: API):
    utility.required_args(args, "name", "type", "recycle_criteria", "location", "name_template")

    name = args.name
    target_type = args.type
    recycle_criteria = args.recycle_criteria
    location = args.location
    name_template = args.name_template
    deduplicate = args.deduplicate
    alias = args.alias

    recycle_value = 0
    recycle_action = BackupRecycleAction.RECYCLE
    if args.recycle_criteria != BackupRecycleCriteria.NONE:
        utility.required_args(args, "recycle_value", "recycle_action")
        recycle_value = args.recycle_value
        recycle_action = args.recycle_action

    try:
        target_id = api.new_target(name, target_type, recycle_criteria, recycle_value, recycle_action, location, name_template, deduplicate, alias)
    except requests.exceptions.ConnectionError:
        utility.failure_network()
    except BackupchanAPIError as exc:
        utility.failure(f"Failed to create new target: {str(exc)}")

    print(f"Created new target. ID: {target_id}")

#
# backupchan target delete
#

def do_delete(args, api: API):
    delete_files = args.delete_files

    try:
        api.delete_target(args.id, delete_files)
    except requests.exceptions.ConnectionError:
        utility.failure_network()
    except BackupchanAPIError as exc:
        utility.failure(f"Failed to delete target: {str(exc)}")
    print("Target deleted.")

#
# backupchan target edit
#

def do_edit(args, api: API):
    target_id = args.id

    try:
        target = api.get_target(target_id)[0]
    except requests.exceptions.ConnectionError:
        utility.failure_network()
    except BackupchanAPIError as exc:
        if exc.status_code == 404:
            utility.failure("Target not found")
        raise

    name = args.name or target.name
    recycle_criteria = args.recycle_criteria or target.recycle_criteria
    recycle_value = args.recycle_value or target.recycle_value
    recycle_action = args.recycle_action or target.recycle_action
    location = args.location or target.location
    name_template = args.name_template or target.name_template
    deduplicate = target.deduplicate
    if args.toggle_deduplication:
        deduplicate = not deduplicate
    alias = (None if args.remove_alias else args.alias) or target.alias

    try:
        api.edit_target(target_id, name, recycle_criteria, recycle_value, recycle_action, location, name_template, deduplicate, alias)
    except requests.exceptions.ConnectionError:
        utility.failure_network()
    except BackupchanAPIError as exc:
        utility.failure(f"Failed to edit target: {str(exc)}")

    print("Target edited.")

#
# backupchan target deletebackups
#

def do_delete_backups(args, api: API):
    delete_files = args.delete_files

    try:
        api.delete_target_backups(args.id, delete_files)
    except requests.exceptions.ConnectionError:
        utility.failure_network()
    except BackupchanAPIError as exc:
        utility.failure(f"Failed to delete target backups: {str(exc)}")
    print("Target backups deleted.")
