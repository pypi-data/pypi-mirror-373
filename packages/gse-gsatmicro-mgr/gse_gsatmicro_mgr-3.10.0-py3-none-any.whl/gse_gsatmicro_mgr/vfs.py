# "Virtual file system" functions, used to access files on the devices over gsemgr

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

from . import common
from gse_gsatmicro_utils import utils
import stat
import os
import hashlib
import io
from threading import RLock
from contextlib import contextmanager
from . import smp
from . import common
import posixpath as pp

#######################################################################################################################
# Local functions and data

# Recursive lock for VFS operations
vfs_lock = RLock()
# Maximum time to wait to obtain the lock
MAX_LOCK_TIMEOUT_S = 3
# Single VFS instance
vfs_inst = None
# Logger instance
logger = utils.Logger("vfs")

# A VFS exception with an optional extra error code
class VFSError(Exception):
    def __init__(self, msg, code=None):
        super().__init__(msg)
        self.msg, self.code = msg, code

# Lists the content of "path" on the device
def do_ls(path, max_limit):
    with common.cfg.ser.keep():
        res, err_code = [], 0
        try:
            # Initiate listdir operation
            smp.send_request(common.cfg.ser, smp.OPCODE_READ, smp.GSEGroup.ID, smp.GSEGroup.CMD_LIST_START, {"f": path})
            # List all the items in the directory
            while True:
                crt = smp.send_request(common.cfg.ser, smp.OPCODE_READ, smp.GSEGroup.ID, smp.GSEGroup.CMD_LIST_NEXT, {"m": max_limit},
                    skip_rc_check=True)
                if (err_code := crt["rc"]) < 0: # device returned error
                    break
                res.extend(crt["l"])
                if err_code == 1: # we are done
                    break
        except Exception:
            raise VFSError(f"Invalid ls() response from device ({path})")
        finally: # terminate operation no matter what
            smp.send_request(common.cfg.ser, smp.OPCODE_READ, smp.GSEGroup.ID, smp.GSEGroup.CMD_LIST_NEXT, {"m": 0}, skip_rc_check=True)
        if err_code < 0:
            raise VFSError(f"Error {err_code} in ls() response from device ({path})")
        return res

# Remove file or directory
def do_rm(path):
    try:
        res = smp.send_request(common.cfg.ser, smp.OPCODE_READ, smp.GSEGroup.ID, smp.GSEGroup.CMD_FS_REMOVE, {"f": path}, skip_rc_check=True)
    except:
        raise VFSError(f"Invalid rm() response from device ({path})")
    if res["rc"] != 0:
        raise VFSError(f"Unable to remove {path}")

# Create a new file or directory
def do_create(path, is_file):
    try:
        res = smp.send_request(common.cfg.ser, smp.OPCODE_READ, smp.GSEGroup.ID, smp.GSEGroup.CMD_FS_CREATE,
            {"f": path, "t": smp.GSEGroup.STAT_FILE if is_file else smp.GSEGroup.STAT_DIR}, skip_rc_check=True)
    except:
        raise VFSError(f"Invalid create() response from device ({path})")
    if res["rc"] != 0:
        raise VFSError(f"Unable to create {path}")

# Return information about the given FS item
def do_stat(path, must_succeed=True):
    try:
        res = smp.send_request(common.cfg.ser, smp.OPCODE_READ, smp.GSEGroup.ID, smp.GSEGroup.CMD_FSTAT, {"f": path}, skip_rc_check=True)
    except:
        raise VFSError(f"Invalid stat() response from device ({path})")
    if must_succeed and res.get('t', smp.GSEGroup.STAT_NOT_FOUND) == smp.GSEGroup.STAT_NOT_FOUND: # path not found
        raise VFSError(f"Unable to stat {path}")
    return res

# Decorator used for a function that needs to obtain the VFS lock
def locked(func):
    def wrapper(*args, **kwargs):
        if vfs_lock.acquire(timeout=MAX_LOCK_TIMEOUT_S) == False:
            raise VFSError("Unable to obtain VFS lock")
        try:
            return func(*args, **kwargs)
        finally:
            vfs_lock.release()
    return wrapper

#######################################################################################################################
# Public interface

# A "file-like" class for our pseudo-files, used for transferring files to/from the device
class GsemgrFile:

    # Read/write/create/append flags
    (F_READ, F_WRITE, F_CREATE, F_TRUNCATE, F_APPEND, F_MUST_EXIST, F_TRUNCATE) = (1, 2, 4, 8, 16, 32, 64)

    @locked
    def __init__(self, fs, filename, mode):
        with common.cfg.ser.keep():
            logger.debug(f"Open file {filename} in mode {mode}")
            self.name = filename = pp.normpath(filename)
            self.mode, self.data = self.decode_mode(mode), b""
            must_be_writeable = (self.mode & self.F_WRITE) != 0
            if self.mode & self.F_MUST_EXIST: # "filename" must exist and must be a regular file
                fs.fs_find(filename, must_be="file", writeable=must_be_writeable)
                if (self.mode & self.F_TRUNCATE) == 0:
                    self.download_file()
            else: # this must be a new file
                logger.debug2(f"Create file {filename}")
                assert self.mode & self.F_CREATE != 0
                # Create a new File with the path part (which must exist and must be writeable) as a parent
                pname, fname = pp.split(filename)
                if not fname:
                    raise VFSError(f"Invalid file name ({filename})")
                fs.fs_find(pname, must_be="dir", writeable=must_be_writeable)
            # Hash the current content to check if anything changes
            self.init_hash = hashlib.sha256(self.data).digest()
            # At this point, current file data is in "data"
            self.closed, self.total, self.crt = False, len(self.data), 0
            # Prevent the serial port from closing until the file is closed or garbage collected
            common.cfg.ser.acquire()
            self.acquired = True

    # Release serial port if needed
    def __del__(self):
        if self.acquired:
            common.cfg.ser.release()
            self.acquired = False

    @locked
    # Download the file from the device
    def download_file(self):
        logger.debug2(f"Download file {self.name}")
        res, data = True, io.BytesIO()
        try:
            common.download_file(self.name, data, True)
        except:
            res = False
        if not res:
            raise VFSError(f"Device file download error ({self.name})")
        self.data = data.getvalue()

    @locked
    # Upload the file to the device
    def upload_file(self, data):
        logger.debug2("Upload {len(data)} bytes to file {self.name}")
        res = True
        try:
            common.upload_file(self.name, data, True)
        except:
            res = False
        if not res:
            raise VFSError(f"Device file upload error ({self.name})")

    # Check the given open mode and return its corresponding bitwise OR of the F_xxx flags above
    def decode_mode(self, mode):
        # Check mode string. Currently only binary mode is supported
        mode = mode.replace("+b", "b+")
        if mode.find("b") == -1:
            raise VFSError(f"ASCII open mode is not supported ({mode})")
        mode = mode.replace("b", "")
        # Check the other parts of "mode"
        if (not mode) or mode == "r":
            res = self.F_READ | self.F_MUST_EXIST
        elif mode == "r+":
            res = self.F_READ | self.F_WRITE | self.F_MUST_EXIST
        elif mode =="w":
            res = self.F_WRITE | self.F_CREATE | self.F_TRUNCATE
        elif mode == "w+":
            res = self.F_READ | self.F_WRITE | self.F_CREATE | self.F_TRUNCATE
        elif mode == "a":
            res = self.F_WRITE | self.F_CREATE | self.F_APPEND
        elif mode == "a+":
            res = self.F_READ | self.F_WRITE | self.F_CREATE | self.F_APPEND
        else:
            raise VFSError(f"Invalid open mode ({mode})")
        return res

    # Read from file
    def read(self, size=-1):
        if self.closed:
            raise VFSError(f"File closed ({self.name})")
        if self.mode & self.F_READ == 0:
            raise VFSError(f"File not opened for reading ({self.name})")
        if size in (-1, None):
            size = self.total - self.crt
        logger.debug3(f"Read {size} bytes from {self.name}")
        res = self.data[self.crt:self.crt + size]
        self.crt += size
        return res

    # Write to file
    def write(self, data):
        logger.debug3(f"Write {len(data)} bytes to {self.name}")
        if self.closed:
            raise VFSError(f"File closed ({self.name})")
        if self.mode & self.F_WRITE == 0:
            raise VFSError(f"File not opened for writing ({self.name})")
        if self.mode & self.F_APPEND:
            self.crt = len(self.data)
        self.data = self.data[:self.crt] + data + self.data[self.crt + len(data):]
        self.crt += len(data)
        return len(data)

    # Seek in file
    def seek(self, offset, whence=os.SEEK_SET):
        if whence == os.SEEK_SET:
            new_pos = offset
        elif whence == os.SEEK_CUR:
            new_pos = self.crt + offset
        else:
            new_pos = len(self.data) - offset
        if new_pos < 0 or new_pos >= len(self.data):
            raise VFSError(f"Invalid seek position ({self.name})")
        self.crt = new_pos
        return new_pos

    # Return the current file position
    def tell(self):
        return self.crt

    # Truncate file at the given size
    def truncate(self, _):
        raise VFSError(f"truncate() not implemented ({self.name})")

    # Close the file
    def close(self):
        logger.debug(f"Close file {self.name}")
        if self.closed:
            raise VFSError(f"File already closed ({self.name})")
        # If the file needs to be created, upload it
        upload = (self.mode & self.F_CREATE) != 0
        # Otherwise, if the file was opened in write mode, its content might have to be updated
        if not upload:
            upload = (self.mode & self.F_WRITE) != 0 and (hashlib.sha256(self.data).digest() != self.init_hash)
        if upload:
            self.upload_file(self.data)
        self.closed = True
        if self.acquired: # release serial port if needed
            common.cfg.ser.release()
            self.acquired = False

# Implementation of a "file system" over gsemgr, used by the FTP server and other services
class GsemgrFS:
    def __init__(self, listdir_limit):
        self.listdir_limit = listdir_limit

    # Find the given entry in the FS, optionally making sure that it is of the given kind
    # Return the entry kind ("file", "dir" or "none")
    @locked
    def fs_find(self, path, must_exist=True, must_be=None, writeable=False):
        logger.debug3(f"fs_find {path} must_exist={must_exist} must_be={must_be} writeable={writeable}")
        path = pp.normpath(path)
        if path in (None, "", "/"):
            s = {"t": smp.GSEGroup.STAT_DIR, "s": 0, "ro": True}
        else:
            s = do_stat(path, must_succeed=False)
        if s['t'] == smp.GSEGroup.STAT_NOT_FOUND:
            kind = "none"
        else:
            kind = "dir" if s['t'] == smp.GSEGroup.STAT_DIR else "file"
        if must_be == "file" and kind != "file":
            raise VFSError(f"Not a regular file ({path})")
        if must_be == "dir" and kind != "dir":
            raise VFSError(f"Not a directory ({path})")
        if must_exist and kind == "none":
            raise VFSError(f"Path not found ({path})")
        if writeable and s['ro']:
            raise VFSError(f"Path is readonly ({path})")
        return kind

    # Returns True if the given file stat indicates a directory, False otherwise
    def is_stat_dir(self, s):
        return (s & stat.S_IFDIR) != 0

    # Returns True if the given stat refers to a readonly path, False otherwise
    def is_stat_ro(self, s):
        return (s & stat.S_IWUSR) == 0

    # Return the mode (st_mode) stat() for the given path
    def get_mode(self, r_stat):
        is_dir = r_stat['t'] == smp.GSEGroup.STAT_DIR
        mode = stat.S_IFDIR if is_dir else stat.S_IFREG
        mode |= stat.S_IRGRP | stat.S_IRUSR | stat.S_IROTH # read permissions
        if not r_stat['ro']: # write permissions only if this is not a read-only entry
            mode |= stat.S_IWGRP | stat.S_IWUSR | stat.S_IWOTH
        if is_dir: # "execute" permissions to change into a directory
            mode |= stat.S_IXGRP | stat.S_IXUSR | stat.S_IXOTH
        return mode

    @locked
    def listdir(self, path):
        logger.debug2(f"listdir {path}")
        with common.cfg.ser.keep():
            self.fs_find(path, must_be="dir")
            return do_ls(path, self.listdir_limit)

    @locked
    def isdir(self, path):
        logger.debug2(f"isdir {path}")
        return self.fs_find(path, must_exist=False) == "dir"

    @locked
    def isfile(self, path):
        logger.debug2(f"isfile {path}")
        return self.fs_find(path, must_exist=False) == "file"

    @locked
    def stat(self, path):
        path = pp.normpath(path)
        logger.debug2(f"stat {path}")
        res = do_stat(path)
        return os.stat_result((self.get_mode(res), 0, 0, 1, 0, 0, res['s'], 0, 0, 0))

    @locked
    def open(self, filename, mode):
        filename = pp.normpath(filename)
        logger.debug2(f"Open {filename} from VFS")
        return GsemgrFile(self, filename, mode)

    @locked
    def getsize(self, path):
        logger.debug2(f"getszize {path}")
        res = do_stat(pp.normpath(path))
        return res['s']

    def getmtime(self, _):
        return 0

    def getctime(self, _):
        return 0

    @locked
    def exists(self, path):
        logger.debug2(f"exists {path}")
        return self.fs_find(path, must_exist=False) != "none"

    @locked
    def remove(self, path):
        logger.debug2(f"remove {path}")
        with common.cfg.ser.keep():
            self.fs_find(path, must_be="file", writeable=True)
            do_rm(path)

    @locked
    def rmdir(self, path):
        logger.debug2(f"rmdir {path}")
        with common.cfg.ser.keep():
            self.fs_find(path, must_be="dir", writeable=True)
            do_rm(path)

    @locked
    def mkdir(self, path):
        path = pp.normpath(path)
        logger.debug2(f"mkdir {path}")
        with common.cfg.ser.keep():
            if self.exists(path):
                raise VFSError(f"{path} already exists")
            (parent, _) = pp.split(path)
            self.fs_find(parent, must_be="dir", writeable=True)
            do_create(path, False)

    # Create a new empty file
    @locked
    def mkfile(self, path):
        path = pp.normpath(path)
        logger.debug2(f"mkfile {path}")
        with common.cfg.ser.keep():
            if self.exists(path):
                raise VFSError(f"{path} already exists")
            (parent, _) = pp.split(path)
            self.fs_find(parent, must_be="dir", writeable=True)
            do_create(path, True)

# Return the single VFS instance, creating it first it needed
def get_vfs():
    global vfs_inst
    if vfs_inst == None:
        # Maximum number of entries to request in a single listdir() call
        listdir_max = int(utils.get_config_entry(common.cfg.cfg, "config", "listdir_max", must_exist=False) or 8)
        utils.debug2(f"Listdir limit set to {listdir_max}")
        vfs_inst = GsemgrFS(listdir_max)
    return vfs_inst

# Context manager that executes the given code in a VFS lock
# Useful for "more atomic" operations (for example: list and stat at the same time)
# Use carefully, because the code could potentially take a lot of time to run
@contextmanager
def locked_vfs():
    if vfs_lock.acquire(timeout=MAX_LOCK_TIMEOUT_S) == False:
        raise VFSError("Unable to obtain VFS lock")
    try:
        yield get_vfs()
    finally:
        vfs_lock.release()