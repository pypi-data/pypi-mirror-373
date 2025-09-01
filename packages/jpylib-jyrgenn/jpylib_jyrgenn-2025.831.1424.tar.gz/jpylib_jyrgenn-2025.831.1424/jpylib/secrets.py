#!/usr/bin/env python3

import os
import sys
import zlib
import errno
import fcntl
import base64
import shutil
import collections
from datetime import datetime

from jpylib import info, notice, pgetopts

# Where to look for the secrets file.
basedir = "/" if os.geteuid() == 0 else os.environ.get('HOME') or "."
default_filename = os.path.join(basedir, "etc/secrets")

# suffix of backup file
backup_suffix = ".backup"

# prefix of end line
end_prefix = "# written by putsecret() "

# Default character encoding to use; this *should* depend on the environment,
# but I am too lazy to do that now.
default_char_encoding = "utf-8"

# Be able to catch this, if nexeccary
class FileModeError(Exception):
    """An exception raised when a file has the wrong access mode."""
    pass

def checkFileMode(fname):
    """Check the file for basic suitablility as a secrets file.
    
    Return the lower file mode bits if it exists, or None.
    """
    try:
        if os.path.isdir(fname):
            raise IsADirectoryError(errno.EISDIR, fname, "must be a file")
        statinfo = os.stat(fname)
        access_mode = statinfo.st_mode & 0o777
        if statinfo.st_mode & 0x6:
            raise FileModeError(fname, "is world-accessible: 0{:o}".format(
                access_mode))
        return access_mode
    except FileNotFoundError:
        return None
    

# En- and decoder functions. The names must be {en,de}code_{tag}, so they can be
# found in globals().

def encode_b64(data):
    """Encode data in base64."""
    return base64.b64encode(data)

def decode_b64(data):
    """Decode base64-encoded data."""
    return base64.b64decode(data)

def decode_zip(data):
    """Decode a zipped string. Implies base64 encoding of zip data."""
    zipped = decode_b64(data)
    return zlib.decompress(zipped)

def encode_zip(data):
    """Zip-compress data. Implies base64 encoding of zip data."""
    zipped = zlib.compress(data)
    return encode_b64(zipped)

valid_options = set([
    name[7:] for name in globals().keys()
    if name.startswith("encode_") or name.startswith("decode_") ])

# encode/decode direction
dir_encode = 0
dir_decode = 1
de_en_prefix = ["encode_", "decode_"]


class OptionUnknownError(LookupError):
    """An exception indicating that a corresponding option was not found."""
    pass

    
def find_coder_func(option, direction, must_find=False):
    coder_name = de_en_prefix[direction] + option
    coder_func = globals().get(coder_name)
    if coder_func or not must_find:
        return coder_func
    else:
        raise OptionUnknownError("encountered unknown option", option)


def decode_val(options, value, char_encoding):
    """Decode the found value, if options are present.

    `options`        array of options
    `value`          the value to decode
    `char_encoding`  the bytes => string encoding to use.
    """
    for opt in options:
        coder_func = find_coder_func(opt, dir_decode)
        assert coder_func, "secrets:decode_val: coder_func unfound"
        data = coder_func(bytes(value, char_encoding))
        value = str(data, char_encoding)
    return value


def read_secrets(fname, get_invalids=False):
    """Read in a secrets file and return its entries.

    Return an ordered dictionary with entries key:([opts], value). If the key is
    a comment line or otherwise not a valid key:value or key:opts:value line,
    opts and value are None, or if get_invalids is false (the default), it is
    not included at all.

    Otherwise, opts is a list of options, which may be empty.

    If there are two colons in a line and the field between the colons is not
    empty, but contains no valid options, the line is treated as a key:value
    line.

    """
    entries = collections.OrderedDict()
    with open(fname) as f:
        lineno = 0
        for line in f:
            lineno += 1
            line = line.rstrip()
            if line.lstrip().startswith("#"):
                # a comment line
                if line.startswith(end_prefix):
                    # the "written by putsecret()" line, skip it
                    continue
                if get_invalids:
                    entries[line] = (None, None)
                continue
            # non-commented lines
            fields = line.split(":", 2)
            nfields = len(fields)
            assert 1 <= nfields <= 3, "unexpected # of fields: "+str(nfields)
            if nfields == 1:
                notice("{}:{}: not a valid key:opts:value line, ignored"
                       .format(fname, lineno))
                continue
            key = fields[0]
            if key in entries:
                info("{}:{}: ignoring duplicate entry for '{}'"
                     .format(fname, lineno, key))
                continue
            if nfields == 2:
                # key:value
                entries[key] = ([], fields[1])
                continue
            if nfields == 3:
                # key:[opts]:value
                if fields[1] == "":
                    # key::value
                    entries[key] = ([], fields[2])
                    continue
                opts = fields[1].split(",")
                if all([ opt in valid_options for opt in opts ]):
                    # valid options
                    entries[key] = (opts, fields[2])
                else:
                    info("{}:{}: invalid options in '{}:...', maybe should be '{}::...'"
                         .format(fname, lineno, key, key))
                    # non-valid options field, so it's key:value again
                    entries[key] = ([], ":".join(fields[1:]))
    return entries

def putsecret(key, value, fname=None, options=None,
              char_encoding=default_char_encoding):
    """Put a secret tagged with `key` into the secrets file `fname`.

    A backup copy is made as {fname}.backup. A temporary file named
    .../.{basename}.newtmp is created, which also serves as a lockfile. After
    all records are written to the temporary file, it is moved into place,
    deleting the original secrets file.

    """
    def write_line(key, opts=None, value=None):
        if opts is None:
            line = key
        else:
            line = ":".join([key, ",".join(opts), value])
        print(line, file=out)
    
    fname = fname or default_filename
    entries = collections.OrderedDict()
    try:
        shutil.copy2(fname, fname + backup_suffix)
    except FileNotFoundError:
        pass

    options = set(options or [])
    if "zip" in options:
        try:
            options.remove("b64")       # would be redundant *and* confusing
        except:
            pass
    for opt in options:
        data = bytes(value, char_encoding)
        data = find_coder_func(opt, dir_encode, must_find=True)(data)
        value = str(data, char_encoding)
    newfile = os.path.join(os.path.dirname(fname),
                           "." + os.path.basename(fname) + ".newtmp")
    try:
        os.umask(0o077)
        access_mode = checkFileMode(fname)
        with open(newfile, "x") as out:
            if access_mode is not None:
                # see that the new file has the same access mode
                os.chmod(newfile, access_mode)
            # now, read in entries, change/set new one, write out again
            try:
                entries = read_secrets(fname, get_invalids=True)
            except FileNotFoundError:
                entries = {}
            entries[key] = (options, value)
            for key, data in entries.items():
                options, value = data
                if options is not None:
                    write_line(key, options, value)
                else:
                    write_line(key)
            write_line(end_prefix+datetime.now().isoformat(timespec="seconds"))
        os.rename(newfile, fname)
    except FileExistsError:
        raise FileExistsError("temp file '{}' exists, aborting".format(newfile))
    finally:
        try:
            os.remove(newfile)
        except:
            pass


def getsecret(key, fname=None, char_encoding=None, error_exception=True):
    """Get a secret tagged with `key` from the secrets file `fname`.

    The default pathname for the secrets file is `/etc/secrets` if
    called by root, and `$HOME/etc/secrets` for normal users.

    The file consist of lines of the form `_key_:_value_`, so the key
    may not contain a colon. Whitespace is significant except at the end
    of the line, where it will be stripped, so the secret may not end
    with whitespace. You can get around these limitations by encoding
    key and/or value with e.g. base64.

    If the key is found, the value is returned. Otherwise, a `KeyError`
    exception is raised. The exception's arguments are a format string,
    the key, and the file name. (Splitting this up allows for subsequent
    i18n.)

    If the found value for the key starts with "{b64}", it will be
    base64-decoded before it is returned.

    """
    if fname is None:
        fname = default_filename
    checkFileMode(fname)
    
    data = read_secrets(fname).get(key)
    if data and data[0] is not None:
            return decode_val(*data, char_encoding or default_char_encoding)
    if error_exception:
        raise KeyError("cannot find secret for '{}' in '{}'", key, fname)
    return None


def getsecret_main():
    if not (2 <= len(sys.argv) <= 3):
        sys.exit("usage: getsecret key [filename]")
    try:
        print(getsecret(*sys.argv[1:]))
    except Exception as e:
        sys.exit("getsecret: " + e.args[0].format(*e.args[1:]))

def putsecret_main():
    ovc, args = pgetopts({
        "_help_header": "put a secret into the secrets file",
        "b": ("base64", bool, False, "encode secret with base64"),
        "z": ("zip", bool, False,
              "encode secret with zip/zlib (and base64)"),
        "o": ("options", str, None, "encoding options (valid: {})"
              .format(",".join(list(valid_options)))),
        "_arguments": ["key", "secret", "[filename]"],
        "_help_footer": "Default secrets file is '{}'"
                        .format(default_filename),
    }, sys.argv[1:])                    # needed for testing (WTF?)
    options = list(filter(None, (ovc.options or "").split(",")))
    for opt in options:
        if opt not in valid_options:
            ovc.ovc_usage("'{}' is not a valid encoding option".format(opt))
    if ovc.base64:
        options.append("b64")
    if ovc.zip:
        options.append("zip")
    putsecret(*args, options=options)
