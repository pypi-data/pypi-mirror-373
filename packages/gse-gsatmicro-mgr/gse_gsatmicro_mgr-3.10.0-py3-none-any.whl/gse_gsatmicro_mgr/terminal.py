# Small serial terminal in gsemgr

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

import threading
import queue
import click
import sys
from gse_gsatmicro_utils import utils
import os
import time
import platform

#######################################################################################################################
# Local functions and data

# Data queue for forwarding between console and serial port
data_q = queue.Queue()
# Was exit requested?
exit_req = False

# Console reader thread function
def con_read_thread(q):
    while True:
        try:
            d = click.getchar()
            if d == "\r":
                d = d + "\n"
            q.put(("stdin", d))
        except EOFError:
            global exit_req
            exit_req = True
            q.put(("stdin", None))
            break
        except KeyboardInterrupt: # send the code for CTR+C to the board
            q.put(("stdin", "\x03"))

# Console reader thread function that only looks for EOF conditions
def con_read_thread_eof_only(q):
    while True:
        try:
            d = click.getchar()
        except EOFError:
            global exit_req
            exit_req = True
            q.put(("stdin", None))
            break

# Serial reader thread function
def ser_read_thread(ser, q, watch_serial):
    while True:
        try:
            if (d := ser.read_cnt(1024, timeout=0.001)):
                q.put(("ser", d))
        except:
            ser.exit()
            # Watch for serial port reconnect if requested by the user
            if watch_serial and not exit_req:
                utils.info("Waiting for the serial port to become available again\r")
                while not os.path.exists(ser.ser_port):
                    time.sleep(0.1)
                time.sleep(0.1) # once again for good luck
                ser.init()
                utils.info(f"Re-connected to {ser.ser_port}\r")
            else:
                q.put(("ser", None))
                break

# Return the combination of keys needed to exit the terminal emulator as a string
def get_exit_keys():
    return "CTRL+Z" if platform.system() == "Windows" else "CTRL+D"

#######################################################################################################################
# Command: console

# 'console' command handler
def cmd_console(ser, args):
    # Create threads for the two readers (stdin and serial)
    ser.set_auto_close(False) # don't close the serial port automatically when not needed
    threading.Thread(target=con_read_thread, args=(data_q, ), daemon=True).start()
    threading.Thread(target=ser_read_thread, args=(ser, data_q, args.watch_serial), daemon=True).start()
    print(f"Connected to board, press {get_exit_keys()} to exit")
    while True:
        (src, d) = data_q.get()
        if d == None:
            break
        elif src =="stdin":
            ser.write(d)
        else:
            sys.stdout.write(d.decode("ascii", errors="ignore"))
            sys.stdout.flush()

# 'console' command argparse helper
def console_args(parser):
    parser.add_argument("--watch-serial", help="Reconnect to the serial port if it becomes unavailable", action="store_true",
                        default=False)

#######################################################################################################################
# Command: logs
# Like "terminal", but the flow of serial data is only from device to PC

# 'logs' command handler
def cmd_logs(ser, args):
    # Create threads for the two readers (stdin and serial)
    ser.set_auto_close(False) # don't close the serial port automatically when not needed
    threading.Thread(target=con_read_thread_eof_only, args=(data_q, ), daemon=True).start()
    threading.Thread(target=ser_read_thread, args=(ser, data_q, args.watch_serial), daemon=True).start()
    print(f"Connected to board, press {get_exit_keys()} to exit")
    while True:
        (_, d) = data_q.get()
        if d == None:
            break
        else:
            sys.stdout.write(d.decode("ascii", errors="ignore"))
            sys.stdout.flush()

# 'logs' command argparse helper
def logs_args(parser):
    parser.add_argument("--watch-serial", help="Reconnect to the serial port if it becomes unavailable", action="store_true",
                        default=False)