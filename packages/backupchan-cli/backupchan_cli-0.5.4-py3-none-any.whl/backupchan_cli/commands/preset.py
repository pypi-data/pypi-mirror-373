from backupchan_cli import utility
from backupchan import API
from backupchan_presets import Presets, PresetError
import requests

#
#
#

def setup_subcommands(subparser):
    #
    #
    #
    
    list_cmd = subparser.add_parser("list", help="List all presets")
    list_cmd.set_defaults(func=do_list)

    #
    #
    #

    new_cmd = subparser.add_parser("new", help="Create a new preset")
    new_cmd.add_argument("name", type=str, help="Name of the new preset. Must be unique.")
    new_cmd.add_argument("location", type=str, help="Path to file or directory to back up")
    new_cmd.add_argument("target_id", type=str, help="ID of the target to upload backups to")
    new_cmd.set_defaults(func=do_new)

    #
    #
    #

    delete_cmd = subparser.add_parser("delete", help="Delete an existing preset")
    delete_cmd.add_argument("name", type=str, help="Name of the preset to delete")
    delete_cmd.set_defaults(func=do_delete)

    #
    #
    #

    upload_cmd = subparser.add_parser("upload", help="Upload a backup according to an existing preset")
    upload_cmd.add_argument("name", type=str, help="Name of the preset to use")
    upload_cmd.add_argument("--automatic", "-a", action="store_true", help="Mark this backup as automatic")
    upload_cmd.add_argument("--sequential", "-s", action="store_true", help="Upload sequentially")
    upload_cmd.set_defaults(func=do_upload)

    #
    #
    #

    reset_cmd = subparser.add_parser("reset", help="Delete all existing presets")
    reset_cmd.set_defaults(func=do_reset)

#
# backupchan preset list
#

def do_list(args, presets: Presets, _):
    if len(presets) == 0:
        print("There are no presets.")

    for preset_name in presets:
        preset = presets[preset_name]
        print(f" | '{preset_name}' - location: '{preset.location}', target: '{preset.target_id}'")

#
# backupchan preset new
#

def do_new(args, presets: Presets, _):
    presets.add(args.name, args.location, args.target_id)
    presets.save()
    print("Preset saved.")

#
# backupchan preset delete
#

def do_delete(args, presets: Presets, _):
    presets.remove(args.name)
    presets.save()
    print("Preset deleted.")

#
# backupchan preset upload
#

def do_upload(args, presets: Presets, api: API):
    if args.name not in presets:
        utility.failure(f"Preset '{args.name}' not found")

    if args.sequential:
        try:
            for index, total_files, filename in presets[args.name].seq_upload(api, not args.automatic):
                print(f"Upload file {index + 1} of {total_files}: {filename}")
        except requests.exceptions.ConnectionError:
            utility.failure_network()
        except BackupchanAPIError as exc:
            utility.failure(f"Failed to upload backup: {str(exc)}")
        except Exception as exc:
            api.seq_terminate(args.target_id)
            utility.failure(f"Client error: {str(exc)}")
        print("Backup uploaded.")
    else:
        job_id = presets[args.name].upload(api, not args.automatic)
        print(f"Backup uploaded with preset '{args.name}' and is now being processed by job #{job_id}.")

#
# backupchan preset reset
#

def do_reset(args, _, __):
    Presets().save()
    print(f"Presets reset.")
