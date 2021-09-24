#!/usr/bin/env python3

import os
import shutil
import tempfile

__description__ = "File management functions module"
__author__ = "Choops <choopsbd@gmail.com>"

c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"


def symlink_force(target, link_name):
    """
    Create a symbolic link link_name pointing to target.
    Overwrites link_name if it exists.
    """

    # os.replace() may fail if files are on different filesystems
    link_dir = os.path.dirname(link_name)

    while True:
        temp_link_name = tempfile.mktemp(dir=link_dir)
        try:
            os.symlink(target, temp_link_name)
            break
        except FileExistsError:
            pass
    try:
        os.replace(temp_link_name, link_name)
    except OSError:  # e.g. permission denied
        os.remove(temp_link_name)
        raise


def overwrite(src, tgt):
    """Overwrite file or folder"""

    if os.path.isdir(src):
        if os.path.isdir(tgt):
            shutil.rmtree(tgt)

        try:
            shutil.copytree(src, tgt, symlinks=True)
        except EnvironmentError:
            return False
    else:
        if os.path.exists(tgt):
            os.remove(tgt)

        try:
            shutil.copy(src, tgt, follow_symlinks=False)
        except EnvironmentError:
            return False

    return True


def rcopy(src, tgt):
    """Recursive copy"""

    for root, dirs, files in os.walk(src):
        for item in files:
            src_path = os.path.join(root, item)
            dst_path = os.path.join(tgt, src_path.replace(f"{src}/", ""))

            if os.path.exists(dst_path):
                if os.stat(src_path).st_mtime > os.stat(dst_path).st_mtime:
                    shutil.copy(src_path, dst_path)
            else:
                try:
                    shutil.copy(src_path, dst_path)
                except EnvironmentError:
                    return False

        for item in dirs:
            src_path = os.path.join(root, item)
            dst_path = os.path.join(tgt, src_path.replace(f"{src}/", ""))

            if not os.path.exists(dst_path):
                try:
                    os.makedirs(dst_path)
                except OSError:
                    return False

    return True


def rchown(path, new_owner=None, new_group=None):
    """Recursive chown"""

    shutil.chown(path, new_owner, new_group)

    for dirpath, dirs, files in os.walk(path):
        for mydir in dirs:
            shutil.chown(os.path.join(dirpath, mydir), new_owner, new_group)

        for myfile in files:
            shutil.chown(os.path.join(dirpath, myfile), new_owner, new_group)


def rchmod(path, perm):
    """Recursive chmod"""

    os.chmod(path, perm)

    for root, dirs, files in os.walk(path):
        for mydir in dirs:
            os.chmod(os.path.join(root, mydir), perm)

        for myfile in files:
            os.chmod(os.path.join(root, myfile), perm)
