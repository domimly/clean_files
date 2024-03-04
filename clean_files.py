#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict
from datetime import datetime
import hashlib
from pathlib import Path

DEFAULT_CONFIG_PATH = Path.home() / ".clean_files"
DEFAULT_CONFIG = {
    'permissions': '644',
    'temporary_suffixes': ['~', '.tmp'],
    'forbidden_characters': [
        ':', '"', ':', '*', '?', '$', '#', '\'', '|', '\\'
    ],
    'default_character': '_'
}


def ask(prompt):
    while True:
        choice = input(f"{prompt} ({'y/n'}): ").lower()
        if choice in ("yes", "y", "Y"):
            return True
        if choice in ("no", "n", "N"):
            return False


def move_file(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    src.rename(dst)
    print(f"{src}: moved to {dst}")


def get_files_recursively(dir_path):
    return [entry for entry in dir_path.rglob('*') if entry.is_file()]


def get_hash(file):
    hasher = hashlib.md5()
    with open(file, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_modification_date(file):
    return datetime.fromtimestamp(file.stat().st_mtime)


def get_permissions(file):
    return file.stat().st_mode & 0o777


def find_oldest(files):
    return min(files, key=get_modification_date)


def find_newest(files):
    return max(files, key=get_modification_date)


def find_duplicates(dirs):
    files = []
    for dir in dirs:
        files.extend(get_files_recursively(dir))

    files_hash = defaultdict(list)
    for file in files:
        files_hash[get_hash(file)].append(file)

    duplicate_files = [
        files for files in files_hash.values() if len(files) > 1
        ]

    return duplicate_files


def duplicates(dirs, action):
    duplicated_list = find_duplicates(dirs)
    for duplicates in duplicated_list:
        oldest = find_oldest(duplicates)
        if action.lower() == 'y' or (action.lower() == 'ask' and ask(
            f'files: {[str(file) for file in duplicates]} '
            f'have the same content - '
            f'only keep the oldest one: {str(oldest)}?'
        )):
            for file in duplicates:
                if file != oldest:
                    file.unlink()
                    print(f'file: {str(file)} removed')


def empty(dirs, action):
    for dir in dirs:
        for file in get_files_recursively(dir):
            if file.stat().st_size == 0:
                if action.lower() == 'y' or (action.lower() == 'ask' and ask(
                    f'file: {str(file)} is empty - delete?'
                )):
                    file.unlink()
                    print(f'file: {str(file)} removed')


def temporary(dirs, suffixes_list, action):
    for dir in dirs:
        for file in get_files_recursively(dir):
            if file.name.endswith(tuple(suffixes_list)):
                if action.lower() == 'y' or (action.lower() == 'ask' and ask(
                    f'file: {str(file)} is temporary - delete?'
                )):
                    file.unlink()
                    print(f'file: {str(file)} removed')


def find_same_name(dirs):
    files = []
    for dir in dirs:
        files.extend(get_files_recursively(dir))

    files_names = defaultdict(list)
    for file in files:
        files_names[file.name].append(file)

    duplicate_names = [
        files for files in files_names.values() if len(files) > 1
        ]

    return duplicate_names


def same_name(dirs, action):
    duplicated_list = find_same_name(dirs)
    for duplicated in duplicated_list:
        newest = find_newest(duplicated)
        if action.lower() == 'y' or (action.lower() == 'ask' and ask(
            f'files: {[str(file) for file in duplicated]} '
            f'have the same name - '
            f'only keep the newest one: {str(newest)}?'
        )):
            for file in duplicated:
                if file != newest:
                    file.unlink()
                    print(f'file: {str(file)} removed')


def permissions(dirs, permissions, action):
    for dir in dirs:
        for file in get_files_recursively(dir):
            if get_permissions(file) != permissions:
                if action.lower() == 'y' or (action.lower() == 'ask' and ask(
                    f'file: {str(file)} has unusual permissions:'
                    f'{oct(get_permissions(file))} - change to default:'
                    f'{oct(permissions)}?'
                )):
                    file.chmod(permissions)
                    print(
                        f'permissions changed for file: {str(file)} '
                        f'to default permissions: {oct(get_permissions(file))}'
                    )


def find_forbidden_characters(dirs, forbidden_characters):
    files = []
    for dir in dirs:
        files.extend(get_files_recursively(dir))

    forbidden_characters_files = []
    for file in files:
        for character in forbidden_characters:
            if character in file.name:
                forbidden_characters_files.append(file)

    return forbidden_characters_files


def forbidden_characters(
    dirs,
    forbidden_characters,
    default_character,
    action
):
    forbidden_characters_files = find_forbidden_characters(
        dirs, forbidden_characters
    )
    for file in forbidden_characters_files:
        new_name = file.name
        for character in forbidden_characters:
            new_name = new_name.replace(character, default_character)
        new_path = str(file).replace(file.name, new_name)
        if action.lower() == 'y' or (action.lower() == 'ask' and ask(
            f'file: {str(file)} contains forbidden characters in file name - '
            f'change to: {new_name}?'
        )):
            file.rename(new_path)
            print('changed file name')


def find_missing(dirs):
    main_dir_files_hash = set()
    for file in get_files_recursively(dirs[0]):
        main_dir_files_hash.add(get_hash(file))

    missing = []
    for dir in dirs[1:]:
        for file in get_files_recursively(dir):
            hash = get_hash(file)
            if hash not in main_dir_files_hash:
                new_location = Path(str(file).replace(str(dir), str(dirs[0])))
                missing.append((file, new_location))

    return missing


def missing(dirs, action):
    missing = find_missing(dirs)
    for entry in missing:
        file, new_location = entry
        if action.lower() == 'y' or (action.lower() != 'n' and ask(
            f'file: {str(file)} does not exist in main catalogue - '
            f'move to: {str(new_location)}?'
        )):
            move_file(file, new_location)


def parse_args():
    parser = argparse.ArgumentParser(
        description='perform chosen actions to clean up a set of directories'
    )
    parser.add_argument(
        "--main-dir",
        help="main directory to clean up and move all the files to",
        required=True)
    parser.add_argument(
        "--dir",
        help="additional directory to clean up", action='append')
    parser.add_argument(
        "--config-file",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"use custom config file instead of default {DEFAULT_CONFIG_PATH}"
    )

    parser.add_argument(
        "--missing-in-main-dir",
        help="find files that are not present in the main directory",
        nargs='?', default='n', const='ask', choices=('y', 'n', 'ask')
    )
    parser.add_argument(
        "--same-content",
        help="find sets of files with the same content",
        nargs='?', default='n', const='ask', choices=('y', 'n', 'ask')
    )
    parser.add_argument(
        "--same-name",
        help="find sets of files with the same name",
        nargs='?', default='n', const='ask', choices=('y', 'n', 'ask')
    )
    parser.add_argument(
        "--temporary",
        help="find temporary files",
        nargs='?', default='n', const='ask', choices=('y', 'n', 'ask')
    )
    parser.add_argument(
        "--empty",
        help="find files that are empty",
        nargs='?', default='n', const='ask', choices=('y', 'n', 'ask')
    )
    parser.add_argument(
        "--unusual-permissions",
        help="find files with unusual access permissions",
        nargs='?', default='n', const='ask', choices=('y', 'n', 'ask')
    )
    parser.add_argument(
        "--forbidden-name",
        help="find files with special characters in their filename",
        nargs='?', default='n', const='ask', choices=('y', 'n', 'ask')
    )
    return parser.parse_args()


def main():
    args = parse_args()
    main_dir = Path(args.main_dir)
    other_dirs = [Path(s) for s in args.dir] if args.dir else []
    all_dirs = [main_dir] + other_dirs

    config = DEFAULT_CONFIG
    if args.config_file.exists():
        config.update(json.load(open(args.config_file)))
    perms = int(config["permissions"], base=8)

    if args.missing_in_main_dir != 'n':
        missing(all_dirs, args.missing_in_main_dir)
    if args.same_content != 'n':
        duplicates(all_dirs, args.same_content)
    if args.same_name != 'n':
        same_name(all_dirs, args.same_name)
    if args.empty != 'n':
        empty(all_dirs, args.empty)
    if args.unusual_permissions != 'n':
        permissions(all_dirs, perms, args.unusual_permissions)
    if args.forbidden_name != 'n':
        forbidden_characters(
            all_dirs,
            config["forbidden_characters"],
            config["default_character"],
            args.forbidden_name
        )
    if args.temporary != 'n':
        temporary(all_dirs, config["temporary_suffixes"], args.temporary)


if __name__ == '__main__':
    main()
