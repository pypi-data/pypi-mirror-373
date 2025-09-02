# SMP commands for the GSE specific management group

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
from . import smp
from .smp_exceptions import *
from prettytable import PrettyTable
import os
import sys
from . import common
import re
from gse_gsatmicro_utils import detect_ports

#######################################################################################################################
# Command: prop get

# Python program to get all properties (global or for a single module)
get_all_props_prog = """
import props
eprint('[', end="")
try:
    it = props.iterator({root})
    for idx, p in enumerate(it):
        if idx >= {first} and idx < {last}:
            eprint("," if idx > {first} else "", end="")
            eprint(p.to_json(), end="")
except:
    eprint("false")
eprint(']')
"""

# Python program to return data for a single property
get_single_prop_prog = """
import props
try:
    p = props.get_property("{mod}", "{name}")
    eprint(p.to_json())
except:
    eprint("false")
"""

# 'prop get' command handler
def cmd_prop_get(ser, args):
    if len(args.name) > 2:
        utils.fatal("Invalid property namw")
    vals, idx, limit = [], 0, 4
    with ser.keep():
        if len(args.name) == 2:
            r = common.run_prog_json(get_single_prop_prog, mod=args.name[0], name=args.name[1])
            if r == False:
                utils.fatal("Error retriving property value")
            else:
                vals.append(r)
        else: # return properties from a single module or all modules
            mod_name = None if len(args.name) == 0 else f'"{args.name[0]}"'
            while True:
                # Request up to 'limit' props per iteration
                r = common.run_prog_json(get_all_props_prog, root=mod_name, first=idx, last=idx + limit)
                if (not isinstance(r, list)) or r == [False]:
                    utils.fatal("Error retriving properties")
                vals.extend(r)
                if len(r) < limit: # no more properties
                    break
                idx += limit
    if len(vals) == 0:
        utils.info("No properties returned")
    else:
        pt = PrettyTable()
        pt.align = "l"
        pt.field_names = ["Module", "Name", "Type", "Min", "Max", "Default", "Value"]
        for v in vals:
            low = v["l"] if v["l"] != None else "-"
            high = v["h"] if v["h"] != None else "-"
            pt.add_row((v["m"], v["n"], v["t"], low, high, v["d"], v["v"]))
        print(pt)

# 'prop get' command argparse handler
def prop_get_args(parser):
    parser.add_argument("name", nargs='*', help="Property name.\
        Use 'mod property' for a single property. \
        Use 'mod' for all module properties. \
        Without arguments, all properties are listed")

#######################################################################################################################
# Command: prop set

# Python program to set the value of a property
set_prop_program = """
import props
try:
    props.set("{mod}", "{name}", "{value}")
    eprint("true")
except:
    eprint("false")
"""

# 'props set' command handler
def cmd_prop_set(ser, args):
    if len(args.data) != 3:
        utils.fatal("Invalid syntax")
    r = common.run_prog_json(set_prop_program, mod=args.data[0], name=args.data[1], value=args.data[2])
    if r == False:
        utils.fatal("Unable to set property value")
    else:
        utils.info("Property value set")

# 'prop set' command argparse handler
def prop_set_args(parser):
    parser.add_argument("data", nargs='+', help="Use 'mod name value' to set the value of the property 'name' in module 'mod'")

#######################################################################################################################
# Command: runpy

# 'runpy' command handler
def cmd_run_python(ser, args):
    # Argument validation
    if args.code and args.file:
        utils.fatal("Use either '--file' or '--code', not both")
    if args.timeout <= 0 or args.timeout > 60:
        utils.fatal("The timeout must be between 1 and 60 seconds")
    code, f = None, None
    if args.code: # read code from command line
        code = args.code
    elif args.file: # read code from give file
        if not os.path.isfile(args.file):
            utils.fatal(f"'{args.file}' not found or not a regular file")
        else:
            f = open(args.file, "rt")
    else: # read code from stdin
        f = sys.stdin
    if f:
        code = f.read()
        if args.file is not None:
            f.close()
    if code is None or len(code) == 0:
        utils.fatal("Empty Python code")
    req_data = {"code": code, "to": args.timeout}
    resp = smp.send_request(ser, smp.OPCODE_READ, smp.GSEGroup.ID, smp.GSEGroup.CMD_RUN_PYTHON, req_data)
    if "out" in resp:
        if isinstance(out := resp["out"], bytes):
            out = out.decode("ascii")
        print(out, end="")

# 'runpy' command argparse helper
def runpy_args(parser):
    parser.add_argument("-c", "--code", help="The code to run (don't use with '--file')", required=False, default=None)
    parser.add_argument("-f", "--file", help="Run code from this file (don't use with '--code')", required=False, default=None)
    parser.add_argument("-t", "--timeout", help="Seconds to wait for the executor to become available", type=int, default=10)

#######################################################################################################################
# Command: extro

# "extro upload" command handler
def cmd_extro_upload(ser, args):
    utils.must_be_file(args.image)
    with open(args.image, "rb") as f:
        data = f.read()
    if len(data) == 0:
        utils.fatal("Attempt to upload empty EXTRO image")
    pb = common.ProgressBar()
    m_res = common.upload_romfs(data, pb.cb)
    utils.info("ROMFS image uploaded")
    if m_res != 0:
        utils.warning(f"Mounting the new FS failed with error {m_res}, a reboot is recommended")

# "extro erase" command gabdker
def cmd_extro_erase(ser, args):
    pb = common.ProgressBar()
    common.upload_romfs(b"", pb.cb)
    utils.info("ROMFS image erased")

# 'extro upload' command argparse helper
def extro_upload_args(parser):
    parser.add_argument("image", help="ROMFS image file name")

#######################################################################################################################
# Command: list

def cmd_list_devices(ser, args):
    detected = detect_ports.detect()
    if not detected:
        print("No ports detected")
    else:
        for sernum, data in detected.items():
            print(f"Serial number: {sernum}")
            for k, v in data.items():
                print(f"    {k} port: {v}")