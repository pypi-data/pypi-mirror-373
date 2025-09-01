# coding:utf-8
import os
import hashlib
import argparse
import json


def calc_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def package_info(zip_file):
    zip_file = os.path.normpath(zip_file)
    if not zip_file or not os.path.isfile(zip_file):
        raise Exception("file is empty")
    base_name = os.path.basename(zip_file)
    file_md5 = calc_md5(zip_file)
    version = os.path.basename(os.path.dirname(zip_file))
    info_path = os.path.join(os.path.dirname(zip_file), "info.json")
    with open(info_path, 'w') as f:
        data = {
            'version': version,
            'md5': file_md5,
            'bin_file': base_name
        }
        json.dump(data, f, sort_keys=True, indent=4)


def main():
    parser = argparse.ArgumentParser(prog='write info to json')
    parser.add_argument('zip_file', help='foo help')
    args = parser.parse_args()
    package_info(args.zip_file)


if __name__ == "__main__":
    main()