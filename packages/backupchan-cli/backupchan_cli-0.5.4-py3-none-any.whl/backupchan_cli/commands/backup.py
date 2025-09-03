import requests.exceptions
import os
import sys
import tarfile
import tempfile
import uuid
from backupchan_cli import utility
from backupchan import API, BackupchanAPIError, Backup, BackupType, SequentialFile

#
# Utilities
#

def print_backup(backup: Backup, spaces: str, show_recycled: bool, index: int):
    print(f" {index + 1}. | ID: {backup.id}")
    print(f" {spaces} | Created at: {backup.pretty_created_at()}")
    if show_recycled:
        print(f" {spaces} | Recycled: {'Yes' if backup.is_recycled else 'No'}")
    print(f" {spaces} | Size: {utility.humanread_file_size(backup.filesize)}")
    if backup.manual:
        print(f" {spaces} | Uploaded manually")
    else:
        print(f" {spaces} | Uploaded automatically")
    print("=========")

#
#
#

def setup_subcommands(subparser):
    #
    #
    #

    upload_cmd = subparser.add_parser("upload", help="Upload a backup")
    # For things like cron jobs etc. using the cli
    upload_cmd.add_argument("--automatic", "-a", action="store_true", help="Mark backup as having been added automatically")
    upload_cmd.add_argument("--sequential", "-s", action="store_true", help="Upload each file one-by-one instead of creating an archive (only when uploading directory to multi-file target)")
    upload_cmd.add_argument("target_id", type=str, help="ID of the target to upload backup to")
    upload_cmd.add_argument("filename", type=str, help="Name of the file to upload")
    upload_cmd.set_defaults(func=do_upload)

    #
    #
    #

    download_cmd = subparser.add_parser("download", help="Download a backup")
    download_cmd.add_argument("id", type=str, help="ID of the backup to dwonload")
    download_cmd.add_argument("--directory", "-d", type=str, default=".", help="Directory to save downloaded backup to")
    download_cmd.set_defaults(func=do_download)

    #
    #
    #

    delete_cmd = subparser.add_parser("delete", help="Delete an existing backup")
    delete_cmd.add_argument("id", type=str, help="ID of the backup to delete")
    delete_cmd.add_argument("--delete-files", "-d", action="store_true", help="Delete backup files as well")
    delete_cmd.set_defaults(func=do_delete)

    #
    #
    #

    recycle_cmd = subparser.add_parser("recycle", help="Recycle an existing backup")
    recycle_cmd.add_argument("id", type=str, help="ID of the backup to recycle")
    recycle_cmd.set_defaults(func=do_recycle)

    #
    #
    #

    restore_cmd = subparser.add_parser("restore", help="Restore an existing backup")
    restore_cmd.add_argument("id", type=str, help="ID of the backup to restore")
    restore_cmd.set_defaults(func=do_restore)

#
# backupchan backup upload
#

def do_upload(args, api: API):
    if os.path.isdir(args.filename):
        try:
            if args.sequential:
                sequential_upload(args, api)
                print("Backup uploaded.")
                return
            else:
                job_id = api.upload_backup_folder(args.target_id, args.filename, not args.automatic)
        except requests.exceptions.ConnectionError:
            utility.failure_network()
        except BackupchanAPIError as exc:
            utility.failure(f"Failed to upload backup: {str(exc)}")
        except Exception as exc:
            if args.sequential:
                api.seq_terminate(args.target_id)
            utility.failure(f"Client error: {str(exc)}")
    else:
        with open(args.filename, "rb") as file:
            try:
                job_id = api.upload_backup(args.target_id, file, os.path.basename(args.filename), not args.automatic)
            except requests.exceptions.ConnectionError:
                utility.failure_network()
            except BackupchanAPIError as exc:
                utility.failure(f"Failed to upload backup: {str(exc)}")
    print(f"Backup uploaded and is now being processed by job #{job_id}.")

def sequential_upload(args, api: API):
    # Ensure that it's a directory
    if not os.path.isdir(args.filename):
        utility.failure(f"Path '{args.filename}' is not a directory")

    # Build a file list
    file_list = []
    for dirpath, _, filenames in os.walk(args.filename):
        rel_dir = os.path.relpath(dirpath, args.filename)
        rel_dir = "/" if rel_dir == "." else "/" + rel_dir
        for filename in filenames:
            file_list.append(SequentialFile(rel_dir, filename, False))
    total_files = len(file_list)

    try:
        api.seq_begin(args.target_id, file_list, not args.automatic)
    except BackupchanAPIError as exc:
        if exc.status_code == 400 and "Target busy" in str(exc):
            print("Upload interrupted, continuing.")
            server_file_list = api.seq_check(args.target_id)
            already_uploaded = [file for file in server_file_list if file.uploaded]
            file_list = [file for file in file_list if SequentialFile(file.path, file.name, True) not in already_uploaded]
            total_files = len(file_list)
        else:
            raise
    for index, file in enumerate(file_list):
        full_path = os.path.join(file.path, file.name)
        print(f"Upload file {index + 1} of {total_files}: {full_path}")
        with open(os.path.join(args.filename, full_path.lstrip("/")), "rb") as file_io:
            api.seq_upload(args.target_id, file_io, file)
    api.seq_finish(args.target_id)

#
# backupchan backup download
#

def do_download(args, api: API):
    try:
        filename = api.download_backup(args.id, args.directory)
    except requests.exceptions.ConnectionError:
        utility.failure_network()
    except BackupchanAPIError as exc:
        utility.failure(f"Failed to upload backup: {str(exc)}")

    print(f"Backup saved as '{filename}'.")

#
# backupchan backup delete
#

def do_delete(args, api: API):
    delete_files = args.delete_files

    try:
        api.delete_backup(args.id, delete_files)
    except requests.exceptions.ConnectionError:
        utility.failure_network()
    except BackupchanAPIError as exc:
        if exc.status_code == 404:
            utility.failure("Backup not found")
        utility.failure(f"Failed to delete backup: {str(exc)}")

    print("Backup deleted.")

#
# backupchan backup recycle
#

def do_recycle(args, api: API):
    try:
        api.recycle_backup(args.id, True)
    except requests.exceptions.ConnectionError:
        utility.failure_network()
    except BackupchanAPIError as exc:
        if exc.status_code == 404:
            utility.failure("Backup not found")
        utility.failure(f"Failed to recycle backup: {str(exc)}")

    print("Backup recycled.")

#
# backupchan backup restore
#

def do_restore(args, api: API):
    try:
        api.recycle_backup(args.id, False)
    except requests.exceptions.ConnectionError:
        utility.failure_network()
    except BackupchanAPIError as exc:
        if exc.status_code == 404:
            utility.failure("Backup not found")
        utility.failure(f"Failed to restore backup: {str(exc)}")

    print("Backup restored.")
