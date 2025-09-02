# Implementation of FTP server for the device file system(s)

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

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.filesystems import AbstractedFS, FilesystemError
import errno
from . import vfs
import os
import posixpath as pp

# Check the given exception and transform it into an exception that is understood by the FTP server if needed
def check_exc(e):
    if isinstance(e, vfs.VFSError):
        if e.code != None:
            raise OSError(e.code, e.msg)
        else:
            raise FilesystemError(e.msg)
    else:
        raise e

# Exception adapter decorator: change VFSError to FilesysytemError or OSError as needed
def exc_adapter(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            check_exc(e)
    return wrapper

# Implementation of a "file system" over gsemgr, used by the FTP server for various file I/O operations
class EmulatedFS(AbstractedFS):
    def __init__(self, _, cmd_channel):
        super().__init__("/", cmd_channel)
        self.vfs = vfs.get_vfs()

    def full_path(self, path):
        return pp.normpath(pp.join(self.cwd, path))

    @exc_adapter
    def chdir(self, path):
        path = self.full_path(path)
        self.vfs.fs_find(path, must_be="dir")
        self.cwd = path

    @exc_adapter
    def listdir(self, path):
        path = self.full_path(path)
        return self.vfs.listdir(path)

    @exc_adapter
    def isdir(self, path):
        path = self.full_path(path)
        return self.vfs.isdir(path)

    @exc_adapter
    def isfile(self, path):
        path = self.full_path(path)
        return self.vfs.isfile(path)

    @exc_adapter
    def stat(self, path):
        path = self.full_path(path)
        return self.vfs.stat(path)

    def lstat(self, path):
        return self.stat(path)

    def islink(self, _):
        return False

    @exc_adapter
    def open(self, filename, mode):
        filename = self.full_path(filename)
        return self.vfs.open(filename, mode)

    @exc_adapter
    def getsize(self, path):
        path = self.full_path(path)
        return self.vfs.getsize(path)

    def getmtime(self, _):
        return 0

    def realpath(self, path):
        return path

    @exc_adapter
    def lexists(self, path):
        path = self.full_path(path)
        return self.vfs.exists(path)

    def readlink(self, path):
        return path

    @exc_adapter
    def remove(self, path):
        path = self.full_path(path)
        return self.vfs.remove(path)

    @exc_adapter
    def rmdir(self, path):
        path = self.full_path(path)
        return self.vfs.rmdir(path)

    def rename(self, src, dst):
        raise OSError(errno.ENOSYS, "rename not implemented", src)

    def chmod(self, path, mode):
        raise OSError(errno.ENOSYS, "chmod not implemented", path)

    def utime(self, path, timeval):
        raise OSError(errno.ENOSYS, "utime not implemented", path)

    @exc_adapter
    def mkdir(self, path):
        path = self.full_path(path)
        return self.vfs.mkdir(path)

#######################################################################################################################
# Commands

# 'ftpd' command argparse helper
def ftpd_args(parser):
    parser.add_argument("--ftpd-port", help="FTP server port", type=int, default=2121)
    parser.add_argument("-t", "--timeout", help="Seconds to wait for a response from the device", type=int, default=10)

# 'ftpd' command handler
def cmd_ftpd(ser, args):
    # Authorize the anonymous user to perform most operations, except the ones that are not (yet) supported (direct append,
    # changing file permissions, changing access time)
    authorizer = DummyAuthorizer()
    authorizer.add_anonymous("/", perm="elrdfmw")

    # Instantiate FTP handler class
    handler = FTPHandler
    handler.authorizer = authorizer

    # Define a customized banner (string returned when client connects)
    handler.banner = "GSatCore virtual FTP server ready"
    handler.abstracted_fs = EmulatedFS
    handler.passive_ports = range(60000, 65535)

    # Instantiate FTP server class and listen on all interfaces, port 2121
    server = FTPServer(('', args.ftpd_port), handler)

    # Set a limit for connections
    # It's hard to figure out a good number for this, but it should be fairly low
    server.max_cons = 20

    # start ftp server
    server.serve_forever()
