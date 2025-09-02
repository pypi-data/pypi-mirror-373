# Quick upload/download script and other related FS operations

# GSE Proprietary Software License
# Copyright (c) 2025 Global Satellite Engineering, LLC. All rights reserved.
# This software and associated documentation files (the "Software") are the proprietary and confidential information of Global Satellite Engineering, LLC ("GSE"). The Software is provided solely for the purpose of operating applications distributed by GSE and is subject to the following conditions:

# 1. NO RIGHTS GRANTED: This license does not grant any rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell the Software.
# 2. RESTRICTED ACCESS: You may only access the Software as part of a GSE application package and only to the extent necessary for operation of that application package.
# 3. PROHIBITION ON REVERSE ENGINEERING: You may not reverse engineer, decompile, disassemble, or attempt to derive the source code of the Software.
# 4. PROPRIETARY NOTICES: You must retain all copyright, patent, trademark, and attribution notices present in the Software.
# 5. NO WARRANTIES: The Software is provided "AS IS", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement.
# 6. LIMITATION OF LIABILITY: In no event shall GSE be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the Software or the use or other dealings in the Software.
# 7. TERMINATION: This license will terminate automatically if you fail to comply with any of the terms and conditions of this license. Upon termination, you must destroy all copies of the Software in your possession.

# THE SOFTWARE IS PROTECTED BY UNITED STATES COPYRIGHT LAW AND INTERNATIONAL TREATY. UNAUTHORIZED REPRODUCTION OR DISTRIBUTION IS SUBJECT TO CIVIL AND CRIMINAL PENALTIES.

from gse_gsatmicro_utils import utils
import os
import tempfile
import sys

#######################################################################################################################
# Local functions and data

# True if cross-compilation must be skipped, False otherwise
skip_cc = False

# Program to run when cleaning a directory or removing a file is requested
clean_prog = """
import os
import cgse

if cgse.is_dir("{0}"):
    for f in os.listdir("{0}"):
        full_f = "{0}/" + f
        if cgse.is_file(full_f):
            os.remove(full_f)
            print("Removed {{}}".format(full_f))
elif cgse.is_file("{0}"):
    os.remove("{0}")
    print("Removed {0}")
else:
    print("{0} not found")
"""

# Program to run when listing of a directory is requested
ls_prog = """
import os
import cgse

def one(f):
    s = os.stat(f)
    print("f=", s)

if cgse.is_file("{0}"):
    l = ["{0}"]
elif cgse.is_dir("{0}"):
    l = ["{0}/" + e for e in os.listdir("{0}")]
else:
    print("{0} not found")
for f in l:
    s = os.stat(f)
    if s[0] & 0x4000:
        print(f + "/ (directory)")
    else:
        print("{{}} ({{}} bytes)".format(f, s[6]))
"""

# Program that creates a file if it doesn't exist
create_prog = """
import cgse

if not cgse.is_file("{0}"):
    with open("{0}", "wb") as f:
        pass
    print("Created file {0}")
"""

# Run the given program and return its output
def remote_run(prog):
    # Write source to a temporary file
    (hnd, tempname) = tempfile.mkstemp(text=True, suffix='.py')
    f = os.fdopen(hnd, "wt")
    f.write(prog)
    f.close()
    res, out, err = utils.run_command(f"gsemgr runpy -f {tempname}", must_succeed=False, silent=True)
    os.remove(tempname)
    if res != 0:
        utils.error(f"gsemgr returned error {res}")
        utils.fatal(err.decode("ascii"))
    return out.decode('ascii')

# Display program usage
def print_help():
    print("""Arguments: [-h] [--cfg-path CFG_PATH] [-l LS] [-c CLEAN] [-u UPLOAD] [-d DOWNLOAD] [-n NEW] [--reset]

gsemgr file system quick actions

options:
  -h, --help            show this help message and exit
  --cfg-path CFG_PATH   Path to config file
  -l LS, --ls LS        List the given item (file or directory)
                        Can be given more than once
  -c CLEAN, --clean CLEAN
                        Remove the given file or all the files in the given directory
                        Can be given more than once
  -u UPLOAD, --upload UPLOAD
                        File(s) to upload
                        Can be given more than once
                        Can be given as local_name:name_on_target (with out without full path)
  -d DOWNLOAD, --download DOWNLOAD
                        File(s) to download
                        Can be given more than once
  -n NEW, --new NEW
                        Create the given file if it doesn't exist
                        Can be given more than once
  --reset               Software reset board""")

# Chek the program arguments and return a list of actions to perform
def check_args():
    def ensure_more(c):
        nonlocal idx, args
        if idx >= len(args) - 1:
            utils.fatal(f"'{c}' needs an argument")
    def process_one(short, long):
        nonlocal idx, args, res
        if args[idx] in (short, long):
            ensure_more(long)
            res.append((long, args[idx + 1]))
            idx += 2
            return True
        return False
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print_help()
        return []
    res, idx = [], 0
    while idx < len(args):
        if args[idx] == "--reset": # this terminates the sequence
            if idx < len(args) - 1:
                utils.warning("All actions after '--reset' will be ignored")
            res.append(("--reset", None))
            break
        elif process_one("-l", "--ls"):
            continue
        elif process_one("-c", "--clean"):
            continue
        elif process_one("-u", "--upload"):
            continue
        elif process_one("-d", "--download"):
            continue
        elif process_one("-n", "--new"):
            continue
        elif args[idx] == "--cfg-path":
            ensure_more("--cfg-path")
            os.environ["GSE_TOOLS_CONFIG_FILE"] = args[idx + 1]
            idx += 2
        elif args[idx] == "--nocc":
            global skip_cc
            skip_cc = True
            idx += 1
        else:
            utils.fatal(f"Unknown argument {args[idx]}")
    return res

#######################################################################################################################
# Public interface

# Entry point
def main():
    for (act, d) in check_args():
        if act == "--ls":
            utils.info(f"Remote list {d}")
            out = remote_run(ls_prog.format(d))
            print(out)
        elif act == "--clean":
            utils.info(f"Cleaning remote directory/removing remote file {d}")
            out = remote_run(clean_prog.format(d))
            print(out)
        elif act == "--upload":
            parts = d.split(':')
            if not os.path.isfile(parts[0]):
                utils.warning(f"Skipping {d} since it's not a file")
            else:
                if len(parts) == 1:
                    remote_path = f'/lfs/{os.path.split(parts[0])[-1]}'
                elif parts[1][0] == '/':
                    remote_path = parts[1]
                else:
                    remote_path = f'/lfs/{parts[1]}'
                utils.info(f"Upload {parts[0]} to {remote_path}")
                # Prepare gsemgr command
                cmd = ["gsemgr", "file", "upload"]
                if skip_cc:
                    cmd.append("--nocc")
                cmd.extend(["-o", remote_path, parts[0]])
                utils.run_command(cmd, must_succeed=True, silent=True)
        elif act == "--download":
            local_fc = os.path.split(d)[-1]
            utils.info(f"Download {d} to {local_fc}")
            cmd = f"gsemgr file download -o {local_fc} --overwrite {d}"
            res, _, __ = utils.run_command(cmd, must_succeed=False, silent=True)
            if res != 0:
                utils.warning(f"Error downloading {d}")
        elif act == "--new":
            utils.info(f"Creating file {d}")
            out = remote_run(create_prog.format(d))
            print(out)
        elif act == "--reset":
            utils.info("Resetting board (software reset)")
            utils.run_command("gsemgr reset", must_succeed=True, silent=True)

if __name__ == "__main__":
    main()
