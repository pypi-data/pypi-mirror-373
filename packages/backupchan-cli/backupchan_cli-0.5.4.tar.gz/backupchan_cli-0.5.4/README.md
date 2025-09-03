# Backup-chan CLI

![PyPI - License](https://img.shields.io/pypi/l/backupchan-cli)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/backupchan-cli)
![PyPI - Version](https://img.shields.io/pypi/v/backupchan-cli)

This is the command-line interface program for interacting with a Backup-chan server.

## Installing

```bash
# The easy way
pip install backupchan-cli

# Installing from source
git clone https://github.com/Backupchan/cli.git backupchan-cli
cd backupchan-cli
pip install .

# Run directly from source, no installing even needed
./cli.py
```

## Configuring

The CLI has to first be configured before you can use it. Run:

```bash
# Interactive configuration.
backupchan config new -i

# Non-interactive configuration.
backupchan config new -H "http://host" -p 5050 -a "your api key"
```

Run `backupchan --help` to see all the commands you can use.

## Example usage

```bash
$ backupchan target list
Showing page 1

1. |  Classified documents
   | Alias: classified
   | ID: f81d4fae-7dec-11d0-a765-00a0c91e6bf6
   | Type: Multiple files
   | Recycle criteria: After 5 copies
   | Recycle action: Recycle
   | Location: /var/backups/classified_documents
   | Name template: Classified-Documents-$I
   | Deduplication off
=========
$ backupchan target new -n Journal -t single -c none -l /var/backups/journal -m 'journal-$D' -d --alias 'journal'
Created a new target. ID: aed76092-0052-4255-a83b-b4dbc3b2b281
$ backupchan backup upload journal ~/Documents/journal.txt
Backup uploaded.
```
