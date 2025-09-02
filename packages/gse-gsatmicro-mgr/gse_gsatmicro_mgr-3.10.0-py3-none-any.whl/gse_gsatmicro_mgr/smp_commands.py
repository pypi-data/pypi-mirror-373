# Actual implementation of SMP commands

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

from . import smp
from gse_gsatmicro_utils import utils
from .smp_exceptions import *
from prettytable import PrettyTable
import json
import binascii
import os
import hashlib
import io
import tempfile
from . import common
import argparse
import re

#######################################################################################################################
# Local functions and data

# Receive the list of images on the device (image list)
# Returns the list_of_images
# The same function can be used to activate ("test") images with OPCODE_WRITE
def get_image_list(ser, opcode=smp.OPCODE_READ, data={}):
    resp_data = smp.send_request(ser, opcode, smp.AppGroup.ID, smp.AppGroup.CMD_IMG_STATE, data)
    if not 'images' in resp_data:
        raise InvalidResponseData("Unexpected response to 'image state'", resp_data)
    img_info = resp_data["images"]
    if not img_info:
        return []
    # Organize image information by image number and make it more user-friendly
    img_ids, t = {}, "Image 0"
    for i in img_info:
        if "image" in i:
            t = "Image {}".format(i["image"])
            i.pop("image")
        if "hash" in i: # binary values are not serializable via JSON
            i["hash"] = binascii.hexlify(i["hash"]).decode("ascii")
        # Turn active, confirmed, pending and permanent into flags
        flags = []
        for k in ("active", "confirmed", "pending", "permanent"):
            if k in i:
                if i[k]:
                    flags.append(k)
                i.pop(k)
        i["flags"] = flags
        if t in img_ids:
            img_ids[t].append(i)
        else:
            img_ids[t] = [i]
    # Sort the data for this image ID by slot number
    for v in img_ids.values():
        v.sort(key = lambda d: d["slot"])
    return img_ids

#######################################################################################################################
# Command: reset

# 'reset' command handler
def cmd_reset(ser, args):
    common.do_reset(ser)
    utils.info("Done")

#######################################################################################################################
# Command: echo

# 'echo' command handler
def cmd_echo(ser, args):
    resp_data = smp.send_request(ser, smp.OPCODE_WRITE, smp.DefaultGroup.ID, smp.DefaultGroup.CMD_ECHO, {"d": args.echo})
    if not 'r' in resp_data:
        raise InvalidResponseData("Unexpected response to 'echo'", resp_data)
    utils.info("Received: {}".format(resp_data["r"]))

# 'echo' command argparse helper
def echo_args(parser):
    parser.add_argument("echo", help="Echo the given string")

#######################################################################################################################
# Command: threads

# 'threads' command handler
def cmd_threads(ser, args):
    resp_data = smp.send_request(ser, smp.OPCODE_READ, smp.DefaultGroup.ID, smp.DefaultGroup.CMD_TASK_STATS, None)
    if not 'tasks' in resp_data:
        raise InvalidResponseData("Unexpected response to 'task statistics'", resp_data)
    t_info = resp_data["tasks"]
    # Prepare table data:
    #   - remove "state" field if it exists (not interesting)
    #   - multiply stack size/usage by 4, since the report lists 32-bit words
    for n, d in t_info.items():
        if "state" in d:
            del d["state"]
        if "stksiz" in d:
            d["stksiz"] *= 4
        if "stkuse" in d:
            d["stkuse"] *= 4
    if args.json:
        print(json.dumps(t_info))
    else:
        pt = PrettyTable()
        pt.align = "l"
        pt.field_names = ["name", *list(t_info[list(t_info.keys())[0]])]
        # Prepare tab data for tabulate function
        for n, d in t_info.items():
            pt.add_row([n, *d.values()])
        print(pt)

# 'threads' command argparse helper
def threads_args(parser):
    parser.add_argument("--json", help="Display thread information in JSON format", action="store_true", default=False)

#######################################################################################################################
# Command: image list

# 'image list' command handler
def cmd_image_list(ser, args):
    img_ids = get_image_list(ser)
    if args.json:
        print(json.dumps(img_ids))
    elif not img_ids:
        utils.warning("No images reported by the device. This shouldn't be happening.")
    else:
        # Get all fields in all values and print them in the same order always
        fields = None
        for v in img_ids.values():
            for e in v:
                if fields == None:
                    fields = set(e.keys())
                else:
                    fields = fields.union(e.keys())
        # 'slot' must be the first fields
        fields = ["slot"] + sorted(list(fields.difference(["slot"])))
        # Print information in the order in "fields" for all images
        for img, img_info in img_ids.items():
            print(img)
            for i in img_info:
                for f in fields:
                    if f == "slot":
                        print("  Slot {}".format(i[f]))
                    elif f in i:
                        print("    {}: {}".format(f, i[f] if f != "flags" else " ".join(i[f])))

# 'image list' command argparse helper
def image_list_args(parser):
    parser.add_argument("--json", help="Display image information in JSON format", action="store_true", default=False)

#######################################################################################################################
# Command: image upload

# Upload the given image in the given slot
def upload_image(ser, image, slot, mtu, in_recovery):
    with open(image, "rb") as f:
        file_data = f.read()
    with ser.keep():
        # Compute image hash
        h = hashlib.sha256()
        h.update(file_data)
        h = h.digest()
        utils.info("Uploading image {} ({} bytes) to slot {}".format(image, len(file_data), slot))
        utils.info("Image SHA256 is {}".format(binascii.hexlify(h).decode('ascii')))
        # Figure out how much data we can send in a single package, based on the MTU.
        # Since the first and next packages are different, we need different values to maximize speed
        img_info = {"image": slot, "len": len(file_data), "off": 0, "sha": h, "data": b''}
        first_available = common.get_available_space_for_data(mtu, img_info, "data")
        utils.debug2("Available size for data in first request: {}".format(first_available))
        # And now for the next package
        img_info = {"off": len(file_data), "data": b''}
        # Recovery mode seems to require the slot number at all times, but keeping the slot in at all times introuces bugs
        # in normal mode, so we need this condition here
        if in_recovery:
            img_info["image"] = slot
        next_available = common.get_available_space_for_data(mtu, img_info, "data")
        utils.debug2("Available size for data in the next requests: {}".format(next_available))
        # There's that, now lets send some data!
        off, seq_no, pb = 0, smp.get_next_seq_no(None), common.ProgressBar()
        pb.start(len(file_data))
        while off < len(file_data):
            if off == 0:
                img_info = {"image": slot, "len": len(file_data), "off": 0, "sha": h, "data": file_data[:first_available]}
            else:
                img_info = {"off": off, "data": file_data[off:off + next_available]}
                if in_recovery:
                    img_info["image"] = slot
            # Send current request
            to = smp.get_command_timeout(smp.AppGroup.ID, smp.AppGroup.CMD_IMG_UPLOAD) if off == 0 else 5
            resp_data = smp.send_request(ser, smp.OPCODE_WRITE, smp.AppGroup.ID, smp.AppGroup.CMD_IMG_UPLOAD, img_info, mtu, seq_no, timeout=to)
            if not 'off' in resp_data:
                raise InvalidResponseData("Unexpecte response to 'image upload'", resp_data)
            # Read back offset from MCU and use it as the new offset value
            mcu_off = resp_data["off"]
            pb.update(mcu_off - off)
            off = mcu_off
            seq_no = smp.get_next_seq_no(seq_no)
        pb.close()
        utils.info("Done uploading {}".format(image))

# 'image upload' command handler
def cmd_image_upload(ser, args):
    with ser.keep():
        # Argument validation
        imgs = 0
        if args.app_core != None:
            if not os.path.isfile(args.app_core):
                utils.fatal("{} not found or not a file".format(args.app_core))
            imgs += 1
        if args.net_core != None:
            if not os.path.isfile(args.net_core):
                utils.fatal("{} not found or not a file".format(args.net_core))
            imgs += 1
        if imgs == 0:
            utils.fatal("You must specify -a/--app-core, -n/--net-core or both")
        utils.info("Checking for MCUboot recovery mode")
        upload_mtu, in_recovery = common.get_upload_mtu(ser)
        # We don't automatically reset in recovery mode when uploading the net core, since MCUboot needs time to upload the image to the net core
        if in_recovery and args.net_core != None and args.reset:
            utils.warning("Ignoring '--reset' when uploading the net core image in recovery mode")
            args.reset = False
        slots = {}
        if args.net_core != None:
            slots[3 if in_recovery else 1] = args.net_core # correct slot for net core depending on mode: 1 in normal mode, 3 in recovery mode
        if args.app_core != None:
            slots[1 if in_recovery else 0] = args.app_core # correct slot for app core depending on mode: 0 in normal mode, 1 in recovery mode
        # Upload all relevant images
        for slot, image in slots.items():
            upload_image(ser, image, slot, upload_mtu, in_recovery)
        if args.upload_only:
            return
        needs_reset = False
        if in_recovery:
            if args.net_core != None:
                utils.info("Net core image uploaded, wait for 'Net core update done' message from MCUboot before resetting the board")
            needs_reset = True
        else:
            # We still have to mark the new image(s) as "pending" for the next reboot
            # Get list of images again to obtain the proper hash
            img_ids = get_image_list(ser)
            for slot in slots:
                hash_to_activate = None
                if slot == 1: # uploading to the net core
                    # Unlike the app core, we'll have a single image here and that is the image that we need to activate
                    img_data = img_ids["Image 1"]
                    assert len(img_data) == 1
                    utils.info("Activating net core image with hash {}".format(img_data[0]["hash"]))
                    hash_to_activate = img_data[0]["hash"]
                else:
                    img_data = img_ids["Image 0"]
                    assert len(img_data) == 2
                    # Get hashes/slot
                    hashes = {}
                    for i in img_data:
                        hashes[i["slot"]] = i["hash"]
                    assert len(hashes) == 2
                    if hashes[0] == hashes[1]:
                        utils.info("The new app core image is identical to the current image, activation not needed")
                    else: # we always need to mark image in slot 1
                        utils.info("Activating app core image with hash {}".format(hashes[1]))
                        hash_to_activate = hashes[1]
                if hash_to_activate != None:
                    needs_reset = True
                    get_image_list(ser, opcode=smp.OPCODE_WRITE, data={"hash": binascii.unhexlify(hash_to_activate), "confirm": False})
        if args.reset:
            if needs_reset:
                utils.info("Resetting device to activate the new image(s)")
                common.do_reset(ser)
            else:
                utils.info("Skipping reset since no image(s) need to be activated")
        elif needs_reset and (not in_recovery or (args.net_core == None)):
            utils.info("Done, reset device to activate the new image(s)")

# 'image upload' command argparse helper
def image_upload_args(parser):
    parser.add_argument("-a", "--app-core", help="app core update image", default=None)
    parser.add_argument("-n", "--net-core", help="met core update image", default=None)
    parser.add_argument("--upload-only", help="Just upload the image, don't mark it as 'pending' for the next reboot", action="store_true", default=False)
    parser.add_argument("--reset", help="Reset the device after the new image is activated", action="store_true", default=False)

#######################################################################################################################
# Command: image erase

# 'image erase' handler
def cmd_image_erase(ser, args):
    utils.info("Erasing slot {}, this might take a while".format(args.slot))
    resp_data = smp.send_request(ser, smp.OPCODE_WRITE, smp.AppGroup.ID, smp.AppGroup.CMD_IMG_ERASE, {"slot": args.slot}, skip_rc_check=True)
    if "rc" in resp_data:
        _, rc = smp.decode_error_in_response(resp_data)
        utils.fatal("Unable to erase slot {}: error is '{}', extra reason is '{}'".format(args.slot, rc, resp_data.get("rsn", "none")))
    utils.info("Done")

# 'image erase' command argparse helper
def image_erase_args(parser):
    parser.add_argument("-s", "--slot", help="Slot number to erase", type=int, default=1)

#######################################################################################################################
# Command: image activate

# 'image activate' handler
def cmd_image_activate(ser, args):
    try:
        sha = binascii.unhexlify(args.sha256)
    except:
        utils.fatal("Invalid hash '{}'".format(args.sha256))
    get_image_list(ser, opcode=smp.OPCODE_WRITE, data={"hash": sha, "confirm": False})
    utils.info("Done")

# 'image activate' command argparse helper
def image_activate_args(parser):
    parser.add_argument("sha256", help="SHA256 of image to activate (use 'image list' to get hash)")

#######################################################################################################################
# Command: file status

# 'file status' command handler
def cmd_file_status(ser, args):
    with ser.keep():
        resp_data = smp.send_request(ser, smp.OPCODE_READ, smp.FileGroup.ID, smp.FileGroup.CMD_FILE_STATUS, {"name": args.file},
                                     skip_rc_check=True)
        if not "len" in resp_data:
            rc, _ = smp.decode_error_in_response(resp_data)
            if rc == smp.MCUMGR_ERR_ENOENT:
                utils.error("File not found on target")
                return
            raise InvalidResponseData("Unexpected response to 'file status'", resp_data)
        utils.info("File exists, length is {} bytes".format(resp_data["len"]))
        # Also get hash if available
        try:
            resp_data = smp.send_request(ser, smp.OPCODE_READ, smp.FileGroup.ID, smp.FileGroup.CMD_FILE_HASH, {"name": args.file})
            if "type" in resp_data:
                utils.info("{} of file is {}".format(resp_data["type"], resp_data["output"]))
        except InvalidResponseData:
            pass

# 'file status' command argparse handler
def file_status_args(parser):
    parser.add_argument("file", help="Full path of file on target")

#######################################################################################################################
# Command: file download

# Run the actual download command, write the output to the given stream
# Returns True for success or False for error (file not found)
def do_download(ser, fname, f):
    pb = common.ProgressBar()
    try:
        common.download_file(fname, f, False, pb.cb)
        return True
    except:
        return False

# 'file download' command handler
def cmd_file_download(ser, args):
    # Argument validation
    output = args.output if args.output != None else args.file.split('/')[-1]
    if os.path.exists(output) and not args.overwrite:
        utils.error("Destination {} exists and --overwrite not given, aborting".format(output))
        return
    utils.info("Writing to {}".format(output))
    with open(output, "wb") as f:
        if do_download(ser, args.file, f):
            utils.info("Download complete")
        else:
            utils.error("Download failed")

# 'file download' command argparse handler
def file_download_args(parser):
    parser.add_argument("file", help="Full path of file on target")
    parser.add_argument("-o", "--output", help="Path to local file", default=None)
    parser.add_argument("--overwrite", help="Overwrite destination if it exists", action="store_true", default=False)

# Cleanup function for both file upload/download commands
# It tells the MCU to close all file handles related to these commands
def file_up_dl_cleanup(ser, args):
    smp.send_request(ser, smp.OPCODE_WRITE, smp.FileGroup.ID, smp.FileGroup.CMD_FILE_CLOSE, {}, skip_rc_check=True)

#######################################################################################################################
# Command: file upload

# 'file upload' command handler
def cmd_file_upload(ser, args):
    if not os.path.isfile(args.file):
        utils.fatal("{} not found or not a regular file".format(args.file))
    # Cross compile Python files if the GSEMGR_MPY_CC environment variable is set and points to the cross compiler
    # and if the (hidden) "nocc" command line option is not set
    if args.file.endswith(".py") and args.output.endswith(".py") and (not args.nocc) and \
        (cc_path := utils.find_mpy_cross()) != None:
        with tempfile.TemporaryDirectory() as tmpdirname:
            fname = utils.cross_compile(args.file, tmpdirname, mpy_cross=cc_path)
            with open(fname, "rb") as f:
                file_data = f.read()
        # Change output extension to ".mpy" to keep the embedded interpreter happy
        args.output = re.sub(r"\.py$", ".mpy", args.output)
    else:
        with open(fname := args.file, "rb") as f:
            file_data = f.read()
    utils.info("Uploading file {} ({} bytes)".format(fname, len(file_data)))
    pb = common.ProgressBar()
    common.upload_file(args.output, file_data, False, pb.cb)
    utils.info("File uploaded")

# 'file upload' command argparse handler
def file_upload_args(parser):
    parser.add_argument("file", help="File to upload")
    parser.add_argument("-o", "--output", help="Full path to file on target", required=True)
    parser.add_argument("--nocc", action="store_true", help=argparse.SUPPRESS, default=False)

#######################################################################################################################
# Command: file cat (actually just a download to a string)

# 'file cat' command handler
def cmd_file_cat(ser, args):
    with io.BytesIO() as f:
        if do_download(ser, args.file, f):
            f.seek(0)
            fdata = f.read()
            print(fdata if args.binary else fdata.decode('ascii'))

# 'file cat' command argparse handler
def file_cat_args(parser):
    parser.add_argument("file", help="Full path of file on target")
    parser.add_argument("--binary", help="Display contents in binary mode", action="store_true", default=False)
