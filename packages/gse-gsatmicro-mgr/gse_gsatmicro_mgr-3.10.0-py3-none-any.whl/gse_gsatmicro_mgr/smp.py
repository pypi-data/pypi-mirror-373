# SMP protocol implementation and definitions

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

import base64
from crc import Calculator, Crc16
import cbor2
import secrets
from gse_gsatmicro_utils import utils
from .smp_exceptions import *
from gse_gsatmicro_utils import ser_driver

#######################################################################################################################
# Local functions and data

# Initial frame signature
initial_frame_sig = b'\x06\x09'
# Partial frame signature
partial_frame_sig = b'\x04\x14'
# Frame terminator
frame_end_char = b'\n'
# CRC calculator
try:
    crc_calc = Calculator(Crc16.CCITT)
except AttributeError:
    crc_calc = Calculator(Crc16.XMODEM)
# Default MTU value used for most commands
DEFAULT_MTU = 512

# Possible opcodes
(OPCODE_READ, OPCODE_READ_RSP, OPCODE_WRITE, OPCODE_WRITE_RSP) = range(4)
OPCODE_TO_TEXT = {
    OPCODE_READ: "READ",
    OPCODE_READ_RSP: "READ_RSP",
    OPCODE_WRITE: "WRITE",
    OPCODE_WRITE_RSP: "WRITE_RSP"
}

# Default serial response timeout (seconds)
SMP_DEFAULT_RX_TIMEOUT_S = 2

# OS/default group command IDs (only the ones that we use)
class DefaultGroup:
    ID = 0 # group ID
    NAME = "default"
    CMD_ECHO = 0
    CMD_TASK_STATS = 2
    CMD_RESET = 5
    # Used for debugging
    CMD_TO_TEXT = {CMD_ECHO: "echo", CMD_TASK_STATS: "task statistics", CMD_RESET: "reset"}

# Application/software image group command IDs (only the ones that we use)
class AppGroup:
    ID = 1 # group ID
    NAME = "application"
    CMD_IMG_STATE = 0
    CMD_IMG_UPLOAD = 1
    CMD_IMG_ERASE = 5
    # Used for debugging
    CMD_TO_TEXT = {CMD_IMG_STATE: "image state", CMD_IMG_UPLOAD: "image upload", CMD_IMG_ERASE: "image erase"}
    # Command-specific timeouts
    CMD_TIMEOUTS = {CMD_IMG_STATE: 4, CMD_IMG_UPLOAD: 10, CMD_IMG_ERASE: 20}

# File management group
class FileGroup:
    ID = 8 # group ID
    NAME = "file"
    CMD_FILE_DL_UP = 0
    CMD_FILE_STATUS = 1
    CMD_FILE_HASH = 2
    CMD_FILE_CLOSE = 4
    # Used for debugging
    CMD_TO_TEXT = {CMD_FILE_DL_UP: "file download/upload", CMD_FILE_STATUS: "file status", CMD_FILE_HASH: "file hash",
                   CMD_FILE_CLOSE: "file close"}
    # Command-specific timeouts
    CMD_TIMEOUTS = {CMD_FILE_DL_UP: 10}

# GSE-specific management group
class GSEGroup:
    ID = 64 # group ID
    NAME = "GSE"
    CMD_GET_LIMITS = 0
    CMD_RUN_PYTHON = 3
    CMD_EXTRO_START = 4
    CMD_EXTRO_DATA = 5
    CMD_FSTAT = 6
    CMD_FS_REMOVE = 7
    CMD_LIST_START = 8
    CMD_LIST_NEXT = 9
    CMD_FS_CREATE = 10
    # Used for debugging
    CMD_TO_TEXT = {CMD_GET_LIMITS: "get limits",  CMD_RUN_PYTHON: "run Python code",
                   CMD_EXTRO_START: "start to write EXTRO FS", CMD_EXTRO_DATA: "write data to EXTRO FS",
                   CMD_FSTAT: "get file/dir data", CMD_FS_REMOVE: "remove file or directory",
                   CMD_LIST_START: "start listdir", CMD_LIST_NEXT: "continue listdir",
                   CMD_FS_CREATE: "create file or directory"}
    # Command-specific timeouts
    CMD_TIMEOUTS = {CMD_RUN_PYTHON: 30, CMD_EXTRO_DATA: 20, CMD_FSTAT: 5, CMD_FS_REMOVE: 5, CMD_LIST_START: 5,
                    CMD_LIST_NEXT: 10, CMD_FS_CREATE: 5}
    # Stat values for CMD_FSTAT above
    (STAT_NOT_FOUND, STAT_FILE, STAT_DIR) = range(3)

# Map between a group ID and its class
ID_TO_GROUP = {
    DefaultGroup.ID: DefaultGroup,
    AppGroup.ID: AppGroup,
    FileGroup.ID: FileGroup,
    GSEGroup.ID: GSEGroup
}

# MCUmgr error codes and their mapping to strings
(MCUMGR_ERR_OK, MCUMGR_ERR_UNKNOWN, MCUMGR_ERR_ENOMEM, MCUMGR_ERR_EINVAL, MCUMGR_ERR_ETIMEOUT, MCUMGR_ERR_ENOENT,
    MCUMGR_ERR_EBADSTATE, MCUMGR_ERR_EMSGSIZE, MCUMGR_ERR_ENOTSUP, MCUMGR_ERR_ECORRUPT, MCUMGR_ERR_BUSY, MCUMGR_ERR_EACCESSDENIED,
    MCUMGR_ERR_UNSUPPORTED_TOO_OLD, MCUMGR_ERR_UNSUPPORTED_TOO_NEW) = range(14)
mcumgr_err_str = ["OK", "unknown error", "out of memory", "error in input value", "operation timed out", "no such file/entry",
    "current state disallows command", "response too large", "command not supported", "corrupt", "busy running another command",
    "access denied", "protocol version too old", "protocol version too new"]

# This class represents an SMP frame
class Frame:
    ENCODED_LEN = 8 # fixed length of an encoded frame (in bytes)

    def __init__(self, op, group, cmd_id):
        self.op, self.group, self.cmd_id = op, group, cmd_id
        # Default fields (not needed in the constructor)
        self.data_len = 0
        self.seq_no = 0
        # Version MUST be 0, otherwise serial recovery mode will not work (since MCUboot expects version to be 0)
        self.version = 0

    # Serialize this frame
    def to_bytes(self, data_len, seq_no=0):
        self.data_len, self.seq_no = data_len, seq_no
        res = bytes([(self.version << 3) | self.op, 0])  # protocol version 1, flags always 0
        res += data_len.to_bytes(2, 'big') # data length
        res += self.group.to_bytes(2, 'big') # group ID
        res += bytes([seq_no, self.cmd_id]) # sequence number and command ID
        return res

    # Deserialize a frame from its bytes representation
    @staticmethod
    def from_bytes(inp):
        res = Frame(inp[0] & 0x07, int.from_bytes(inp[4:6], 'big'), inp[7])
        res.data_len = int.from_bytes(inp[2:4], 'big')
        res.seq_no = inp[6]
        res.version = (inp[0] >> 3) & 0x03
        return res

    # Convert this frame to a string for easy representation
    def __str__(self):
        res = f"op={self.op} group={self.group} cmd_id={self.cmd_id}"
        res += f" data_len={self.data_len} seq_no={self.seq_no} version={self.version}"
        return res

# Return the next sequence number
def get_next_seq_no(s):
    return secrets.randbelow(256) if s == None else (s + 1) % 256

# Encode the given request, taking into account the hosts's MTU
# Returns a list of all requests that need to be sent to the device (according to the MTUs)
def encode_request(req_frame, body, mtu, seq_no, skip_if_overflow=False):
    # Body data is always CBOR-encoded if it exists
    data = cbor2.dumps(body) if body != None else b''
    # Serialize request and add the body at the end
    req = req_frame.to_bytes(len(data), seq_no) + data
    # Compute CRC16 of serialized data and append it at the end
    f = req + crc_calc.checksum(req).to_bytes(2, 'big')
    # Prepend the chunk to send with the length of the data + crc
    to_send = len(f).to_bytes(2, "big") + f
    # Convert to Base64
    to_send = base64.b64encode(to_send)
    # Split into packets of maximum "MTU" size
    res, left, wrote = [], len(to_send), 0
    while left > 0:
        crt_len = min(mtu - 3, left) # 3 = 2 bytes (header/signature) + 1 byte \n (terminator)
        # However, we need to make sure that we send a multiple of 4 bytes, otherwise the Base64 decoder goes crazy
        while crt_len % 4 != 0:
            crt_len -= 1
        sig = initial_frame_sig if len(res) == 0 else partial_frame_sig # initial or partial frame
        crt = sig + to_send[wrote : wrote + crt_len] + frame_end_char
        res.append(crt) # encode current data
        utils.debug2("Encoded request with frame signature {:04X} and length {}".format(int.from_bytes(sig, 'big'), len(crt)))
        utils.debug3("Requst data: {}".format(crt))
        left -= crt_len
        wrote += crt_len
        if left > 0 and skip_if_overflow: # stop and return False if the function would return nultiple frames and we don't want that
            return False
    if len(res) > 1:
        utils.debug("Request split in {} parts".format(len(res)))
    # Return all requests
    return res

# Send a frame with the given header and body, return the response
# Returns the response frame and the decoded body
def rxtx(ser, req_frame, body, mtu, seq_no=None, timeout=10):
    with ser.keep():
        if seq_no == None:
            seq_no = get_next_seq_no(None)
        send_data = encode_request(req_frame, body, mtu, seq_no) # encode and send the request
        for s in send_data:
            ser.write(s)
            ser.flush_output()
        # Read the response from the host
        res, expected_len = b'', None
        while expected_len == None or len(res) < expected_len:
            # Read header
            rx = ser.read_cnt(2, timeout=timeout)
            if len(rx) != 2:
                raise FrameReadError("Serial timeout reading frame header")
            if len(res) == 0: # initial or partial frame
                if rx != initial_frame_sig:
                    raise FrameReadError("invalid initial frame header")
            else:
                if rx != partial_frame_sig:
                    raise FrameReadError("invalid partial frame header")
            # Read until \n is found
            try:
                crt = ser.read_until_char(frame_end_char, timeout=10, include_char=False)
            except ser_driver.ProtocolError as e:
                raise FrameReadError("serial error reading frame body: {}".format(str(e)))
            utils.debug2("Read response frame of {} bytes".format(len(crt)))
            utils.debug3("Response data: {}".format(crt))
            # Decode this frame
            decoded = base64.b64decode(crt)
            if expected_len == None: # the first frame will encode the total length
                assert len(res) == 0
                expected_len = int.from_bytes(decoded[0:2], 'big')
            res += decoded
        # Check CRC
        data = res[2:len(res) - 2] # actual data encoded in the buffer, skipping initial length and CRC
        crc = crc_calc.checksum(data)
        if crc != int.from_bytes(res[len(res) - 2:], 'big'):
            raise InvalidFrameError("frame CRC error")
        # Check that data length matches how much we actually read
        resp_frame, resp_data = Frame.from_bytes(data[:8]), data[8:]
        if resp_frame.data_len != len(resp_data):
            raise InvalidFrameError("invalid response size")
        # Check sequence number
        if resp_frame.seq_no != seq_no:
            raise InvalidFrameError("unexpected sequence number")
        # Return the decoded frame and the decoded CBOR data
        return resp_frame, cbor2.loads(resp_data)

# Return the timeout of the given command in the given group
def get_command_timeout(group_id, cmd_id):
    group, to = ID_TO_GROUP[group_id], None
    # First check in group's CMD_TIMEOUTS if applicable
    if hasattr(group, "CMD_TIMEOUTS"):
        to = group.CMD_TIMEOUTS.get(cmd_id, None)
    # Then check the group's default timeout (if applicable)
    if to == None and hasattr(group, "DEFAULT_RX_TIMEOUT_S"):
        to = group.DEFAULT_RX_TIMEOUT_S
    # Failing that, always use the global default timeout
    if to == None:
        to = SMP_DEFAULT_RX_TIMEOUT_S
    return to

# Send the given request, check the response
# Returns the decoded response data
def send_request(ser, opcode, group_id, cmd_id, data, mtu=DEFAULT_MTU, seq_no=None, timeout=None, skip_rc_check=False):
    with ser.keep():
        group = ID_TO_GROUP[group_id]
        if seq_no == None:
            seq_no = get_next_seq_no(None)
        if timeout == None:
            timeout = get_command_timeout(group_id, cmd_id)
        utils.debug3("Timeout for command '{}' in group {} is {}".format(group.CMD_TO_TEXT[cmd_id], group.NAME, timeout))
        utils.debug2("Sending command '{}' in group {} with opcode {}, mtu={}, seq_no={}".format(group.CMD_TO_TEXT[cmd_id],
                    group.NAME, OPCODE_TO_TEXT[opcode], mtu, seq_no))
        req_frame = Frame(opcode, group_id, cmd_id)
        resp_frame, resp_data = rxtx(ser, req_frame, data, mtu, seq_no, timeout)
        resp_opcode = OPCODE_READ_RSP if opcode == OPCODE_READ else OPCODE_WRITE_RSP
        # Check fields in the response frame
        if resp_frame.op != resp_opcode:
            raise InvalidFrameError("Unexpected opcode {}, expected {}".format(OPCODE_TO_TEXT.get(resp_frame.op, "UNKNOWN")),
                                    OPCODE_TO_TEXT[opcode])
        if resp_frame.group != group_id:
            raise InvalidFrameError("Unexpected group {}, expected".format(ID_TO_GROUP.get(resp_frame.group, "UNKNOWN")),
                                    group_id)
        if resp_frame.cmd_id != cmd_id:
            raise InvalidFrameError("Unexpected command '{}', expected '{}'".format(group.CMD_TO_TEXT.get(resp_frame.cmd_id, "UNKNOWN")),
                                    group.CMD_TO_TEXT[cmd_id])
        if resp_frame.seq_no != seq_no:
            raise InvalidFrameError("Unexpected sequence number {}, expected {}".format(resp_frame.seq_no, seq_no))
        if (not skip_rc_check) and resp_data.get("rc", MCUMGR_ERR_OK) != MCUMGR_ERR_OK:
            raise InvalidResponseData("Host reported error for {}".format(group.CMD_TO_TEXT[cmd_id]), resp_data)
        utils.debug3("Raw response data: {}".format(str(resp_data)))
        return resp_data

# Decode the error code ("rc" field) in a response
# Returns num_code, the string corresponding to the error code if OK
# Returns num_code, "unknown error" string if not recognized
# Returns None, None if the error code does not exist in the response
def decode_error_in_response(data):
    num_rc = None
    rc = data.get("rc", None)
    if rc != None:
        try:
            num_rc = int(rc) # should already be an int, but just in case
            rc = mcumgr_err_str[num_rc] if num_rc < len(mcumgr_err_str) else "unknown error (code {})".format(num_rc)
        except:
            rc = None
    return num_rc, rc
