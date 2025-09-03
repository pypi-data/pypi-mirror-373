# Backup-chan CLI changelog

See what's changed between versions!

## 0.5.4

* Added `show` aliases for every `view` command. This means you can type something like `backupchan target show` instead of `backupchan target view`.

## 0.5.3

* Fixed crashing when trying to upload nonexistent preset.

## 0.5.2

* Fixed handling of network errors in preset uplaods.
* Added continuing interrupted sequential uploads.

## 0.5.1

* Fixed single-file uploads raising an error.

## 0.5.0

* Added support for sequential uploads.

## 0.4.1

* Show what job is currently processing an upload.

## 0.4.0

* Added backup downloads

## 0.3.1

* Updated `backupchan-client-lib` dependency to version 0.3.2.

## 0.3.0

* Added backup presets

## 0.2.2

* Refactored to use the API's new directory upload function.

## 0.2.1

* Refactored to use the [client connection configuration library](https://github.com/Backupchan/client-config).

## 0.2.0

* Added command to view stats.

## 0.1.1

Updated the `README.md` and `pyproject.toml` file.

## 0.1.0

The first stable version.
