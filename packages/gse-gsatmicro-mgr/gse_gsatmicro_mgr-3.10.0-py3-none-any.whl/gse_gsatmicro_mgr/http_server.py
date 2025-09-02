# HTTP (REST) server implementation
# Allows accessing gsemgr with an HTTP API

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

from flask import Flask, request, jsonify, abort, send_file
from . import vfs
import traceback
from markupsafe import escape
import io
import os
from gse_gsatmicro_utils import utils
from . import common
import posixpath as pp

#######################################################################################################################
# Local function and data

# Flask app instance
app = Flask("gse_httpd")
# FS instance
fs = None
# API version
api_version = "2.0"
# httpd logger
logger = utils.Logger("httpd")

# Error template to be rendered when an exception occurs
err_template = """
<html>
<head><title>Internal server error</title></head>
<body>
<h1>Internal server error</h1>
<code>
{error}
</code></body></html>
"""

# Bad request template to be rendered when a bad request occurs
bad_request_template = """
<html>
<head><title>Bad request</title></head>
<body>
{error}
</body></html>
"""

# Return the exception information as HTML formatted code
def get_exc_data():
    exc_info = traceback.format_exc()
    return "<br>\n".join([escape(e) for e in exc_info.split("\n")])

# Validate the JSON request anda returns it
# 'mandatory' is a list with the mandatory keys in the request dictionary
# 'optional' is a list with the optional keys in the request dictionary
# 'json_mode' is True if we expect the request data to be sent as JSON, False otherwise
# Returns the request data as a dictionary
def check_req(request, mandatory, optional=None, json_mode=True):
    if json_mode: # expect the request to have a "json" attribute
        if (res := getattr(request, "json", None)) == None:
            abort(400, "invalid request")
    else: # this request doesn't use JSON
        res = request
    # Either way, we expect a dictionary with all our POST data
    if not isinstance(res, dict):
        abort(400, "Invalid request")
    # Check keys
    d_set = set(list(res.keys())) # request keys
    m_set = set(mandatory) # mandatory keys
    a_set = m_set | set(optional or []) # all keys (mandatory and optional)
    if d_set - a_set: # foreign keys found
        abort(400, "Invalid request")
    if m_set - d_set: # not all mandatory keys were specified
        abort(400, "Invalid request")
    return res

# Wrap a FS API call into a function that knows how to handle VFSError
def fs_check(func):
    def wrapper(*args, **kwargs):
        try:
            # Transform "None" results to True, this lets the called know that the request succeeded, even if it didn't
            # return any data.
            if (res := func(*args, **kwargs)) == None:
                res = True
            return jsonify({"res": res})
        except vfs.VFSError as e: # catch errors from the VFS implementation
            logger.error("VFS error: {}".format(str(e)))
            return jsonify({"err": escape(str(e))})
        except Exception: # other exceptions all reported as internal server errors
            ed = get_exc_data()
            logger.error("fs_check exception: {}".format(ed))
            abort(500, ed)
    wrapper.__name__ = func.__name__
    return wrapper

# Same as abovve, but skip the JSON step
def fs_check_no_json(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception: # all exceptions are reported as internal server errors
            ed = get_exc_data()
            logger.error("fs_check_no_json exception: {}".format(ed))
            abort(500, ed)
    wrapper.__name__ = func.__name__
    return wrapper

# There are probably not needed, so they are commented for now
# Internal err (500) handler
#@app.errorhandler(500)
#def internal_error_handler(error):
#    return err_template.format(error=str(error)), 500

# Bad request (400) handler
#@app.errorhandler(400)
#def bad_request_handler(error):
#    return bad_request_template.format(error=str(error)), 400

######################################################################################################################
# File system requests

# List the content of the directory at "path". If "stat" is True, it also returns data about each item in the directory
# (see /fs/stat below for mode details). If not specified, "stat" defaults to False.
# Returns a dictionary where the keys are directory items and the values are stat data (emtpy if "stat" is False)
@app.route("/fs/list", methods=["POST"])
@fs_check
def fs_list():
    with common.cfg.ser.keep():
        req = check_req(request, ("path", ), ("stat", ))
        if not (do_stat := req.get("stat", False)) in (True, False):
            abort(400)
        path, res = req["path"], {}
        if fs.fs_find(path, must_exist=False) != "dir": # the requested path must exist
            abort(404)
        logger.debug(f"LIST {req['path']}")
        for i in fs.listdir(path):
            t, item_path = {}, pp.join(path, i)
            if do_stat:
                if (s := fs.stat(item_path)) == False: # might happen in case the device changes the FS
                    abort(404)
                t = {"kind": "dir" if fs.is_stat_dir(s[0]) else "file", "size": s[6], "readonly": fs.is_stat_ro(s[0])}
            res[i] = t
        return res

# Return information about a file system item (file or directory).
# Returns a {"kind": "file" | "dir", "size": size, "readonly": True|False} dictionary
@app.route("/fs/stat", methods=["POST"])
@fs_check
def fs_stat():
    with common.cfg.ser.keep():
        req = check_req(request, ("path", ))
        path = req["path"]
        logger.debug(f"STAT {path}")
        if fs.fs_find(path, must_exist=False) == "none": # the item must exist
            abort(404)
        res = fs.stat(path)
        return {"kind": "dir" if fs.is_stat_dir(res[0]) else "file", "size": res[6], "readonly": fs.is_stat_ro(res[0])}

# Returns the kind of item ("file, "dir" or "none") that the given path points to.
# "none" means that the item does not exist
# Returns a string that can be either "file", "dir" or "none"
@app.route("/fs/kind", methods=["POST"])
@fs_check
def fs_kind():
    req = check_req(request, ("path", ))
    logger.debug(f"FIND {req['path']}")
    return fs.fs_find(req["path"], must_exist=False)

# Return the content of file at "path"
@app.route("/fs/get", methods=["POST"])
@fs_check_no_json
def fs_get():
    with common.cfg.ser.keep():
        req = check_req(request, ("path", ))
        path = req["path"]
        logger.debug(f"GET {path}")
        if fs.fs_find(path, must_exist=False) != "file":
            abort(404)
        # Read file content and return it
        # The files are expected to be small, so no streaming is needed.
        f = fs.open(path, "rb")
        data = f.read()
        f.close()
        return send_file(io.BytesIO(data), download_name=path)

# Create a file or a directory at "path", depending on "kind" (which must be either "file" or "dir")
# Returns True for success.
# TODO: add "overwrite"
@app.route("/fs/create", methods=["POST"])
@fs_check
def fs_create():
    with common.cfg.ser.keep():
        req = check_req(request, ("path", "kind"))
        if not req["kind"] in ("file", "dir"):
            abort(400, "invalid kind")
        path = req["path"]
        logger.debug(f"CREATE {path} kind={req['kind']}")
        if req["kind"] == "dir":
            fs.mkdir(path)
        else:
            fs.mkfile(path)

# Remove a file or a directory from "path", depending on "kind" (which must be either "file" or "dir")
# Returns True for success.
@app.route("/fs/remove", methods=["POST"])
@fs_check
def fs_remove():
    with common.cfg.ser.keep():
        req = check_req(request, ("path", "kind"))
        if not req["kind"] in ("file", "dir"):
            abort(400, "invalid kind")
        path = req["path"]
        logger.debug(f"REMOVE {path} kind={req['kind']}")
        if (kind := fs.fs_find(path, must_exist=False)) == "none": # item must exist
            abort(404)
        if kind != req["kind"]: # item kind (file/dir) must match requested "kind"
            abort(400, "bad kind")
        if req["kind"] == "dir":
            fs.rmdir(path)
        else:
            fs.remove(path)

# Save data from "file" at "path", which must exist.
# Optionally, "overwrite" can be specified to overwrite existing files (defaults to True if not specified).
# Returns True for success.
@app.route("/fs/put", methods=["POST"])
@fs_check_no_json
def fs_put():
    with common.cfg.ser.keep():
        if not hasattr(request, "form"):
            abort(400, "'form' not found")
        req = check_req(request.form, ("path", "file"), ("overwrite", ), json_mode=False)
        path, fdata, overwrite = req["path"], req["file"], req.get("overwrite", True)
        logger.debug(f"PUT path={path} overwrite={overwrite}")
        with vfs.locked_vfs():
            # Does this path exist?
            kind = fs.fs_find(path, must_exist=False)
            if kind == "dir": # path is a directory, return with error
                abort(400, "path is a directory")
            elif kind == "file" and not overwrite: # proceed only if allowed to overwrite path
                abort(400, "file already exists")
            # Write data to file
            if isinstance(fdata, str):
                fdata = fdata.encode(errors='replace')
            f = fs.open(path, "wb")
            f.write(fdata)
            f.close()
        return jsonify({"res": True})

#######################################################################################################################
# Other endpoints

# Return API version
@app.route("/version", methods=["GET", "POST"])
def version():
    logger.debug("version request")
    return jsonify({"ver": api_version})

# Reset device
@app.route("/reset", methods=["GET", "POST"])
def reset():
    logger.debug("RESET")
    common.do_reset(common.cfg.ser)
    return jsonify({"res": True})

# Run the code given in "func". The syntax must be "mod_name.func_name"
@app.route("/run", methods=["POST"])
def run_code():
    try:
        req = check_req(request, ("func", ))
        parts = req["func"].split(".") # ensure mod_name.func_name syntax
        if len(parts) != 2:
            abort(400)
        logger.debug(f"RUN {req['func']}")
        res = common.run_code_clean(parts[0], parts[1])
    except:
        res = False
    return jsonify({"res": res})

#######################################################################################################################
# Commands

# 'httpd' command argparse helper
def httpd_args(parser):
    parser.add_argument("--httpd-port", help="HTTP server port", type=int, default=8080)
    parser.add_argument("--httpd-bind", help="HTTP server bind address", type=str, default="127.0.0.1")

# 'httpd' command handler
def cmd_httpd(ser, args):
    global fs
    fs = vfs.get_vfs()
    app.run(host=args.httpd_bind, port=args.httpd_port, debug=args.verbose > 0, use_reloader=False)
