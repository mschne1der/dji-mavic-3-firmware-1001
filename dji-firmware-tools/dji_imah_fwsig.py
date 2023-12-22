#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" DJI Firmware IMaH Un-signer and Decryptor tool.

Allows to decrypt and un-sign module from `.sig` file which starts with
`IM*H`. Use this tool after untarring single modules from a firmware package,
to decrypt its content.

"""

# Copyright (C) 2017  Freek van Tienen <freek.v.tienen@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
__version__ = "0.3.1"
__author__ = "Freek van Tienen, Jan Dumon, Mefistotelis @ Original Gangsters"
__license__ = "GPL"

import sys
import re
import os
import argparse
import binascii
import configparser
import itertools
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Signature import pss
from ctypes import *
from collections import OrderedDict
from time import gmtime, strftime, strptime
from calendar import timegm
from copy import copy
from os.path import basename

from Crypto.Hash import CMAC


# All found keys
keys = {
    "TBIE-170":  bytes([ # Trusted Boot Image Encryption key; published 2021-06-23 by fpv.wtf team
        0x8b, 0xcb, 0x69, 0x6a, 0x42, 0x71, 0xc8, 0x49, 0xae, 0x4d, 0x72, 0x9a, 0x3d, 0x28, 0x2e, 0x25
     ]),
    "PRAK-FAKE": # Slack community Auth Key; generated 2018-01-19 by Jan Dumon
"""-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7AF5tZo4gtcUG
n//Vmk8XnDn2LadzEjZhTbs9h0X674aBqsri+EXPU+oBvpNvoyeisfX0Sckcg2xI
D6CUQJeUD4PijT9tyhis2PRU40xEK7snEecAK25PMo12eHtFYZN8eZVeySmnlNyU
bytlUrXEfRXXKzYq+cHVlOS2IQo2OXptWB4Ovd05C4fgi4DFblIBVjE/HzW6WJCP
IDf53bnzxXW0ZTH2QGdnQVe0uYT5Bvjp8IU3HRSy1pLZ35u9f+kVLnLpRRhlHOmt
xipIl1kxSGGkBkJJB76HdtcoOJC/O95Fl/qxSKzHjlg7Ku/gcUxmMZfvBi6Qih78
krJW0A+zAgMBAAECggEBALYZbtqj8qWBvGJuLkiIYprARGUpIhXZV2E7u6j38Lqi
w13Dvpx1Xi2+LnMSbSpaO/+fwr3nmFMO28P0i8+ycqj4ztov5+N22L6A6rU7Popn
93DdaxBsOpgex0jlnEz87w1YrI9H3ytUt9RHyX96ooy7rigA6VfCLPJacrm0xOf1
OIoJeMnGTeMSQlAFR+JzU5qdHHTcWi1WFNekzBgmxIXp6zZUkep/9+mxD7V8kGT2
MsJ/6IICe4euHA9lCpctYOPEs48yZBDljQfKD5FxVMUWBbXOhoCff99HeuW/4uVj
AO2mFp293nnGIV0Ya5PyDtGd+w/n8kcehFcfbfTvzZkCgYEA4woDn+WBXCdAfxzP
yUnMXEHB6189R9FTzoDwv7q3K48gH7ptJo9gq0+eycrMjlIGRiIkgyuukXD4FHvk
kkYoQ51Xgvo6eTpADu1CffwvyTi/WBuaYqIBH/HMUvFOLZu/jmSEsusXMTDmZxb+
Wpox17h1qMtNlyIqOBLyHcmTsy8CgYEA0trrk6kwmZC2IjMLswX9uSc5t3CYuN6V
g8OsES/68jmJxPYZTj0UidXms5P+V1LauFZelBcLaQjUSSmh1S95qYwM5ooi5bjJ
HnVH/aaIJlKH2MBqMAkBx6EtXqzo/yqyyfEZvt8naM8OnqrKrvxUCfdVx0yf7M7v
wECxxcgOGr0CgYBo198En781BwtJp8xsb5/nmpYqUzjBSXEiE3kZkOe1Pcrf2/87
p0pE0efJ19TOhCJRkMK7sBhVIY3uJ6hNxAgj8SzQVy1ZfgTG39msxCBtE7+IuHZ6
xcUvM0Hfq38moJ286747wURcevBq+rtKq5oIvC3ZXMjf2e8VJeqYxtVmEQKBgAhf
75lmz+pZiBJlqqJKq6AuAanajAZTuOaJ4AyytinmxSUQjULBRE6RM1+QkjqPrOZD
b/A71hUu55ecUrQv9YoZaO3DMM2lAD/4coqNkbzL7F9cjRspUGvIaA/pmDuCS6Wf
sOEW5e7QwojkybYXiZL3wu1uiq+SLI2bRDRR1NWVAoGANAp7zUGZXc1TppEAXhdx
jlzAas7J21vSgjyyY0lM3wHLwXlQLjzl3PgIAcHEyFGH1Vo0w9d1dPRSz81VSlBJ
vzP8A7eBQVSGj/N5GXvARxUswtD0vQrJ3Ys0bDSVoiG4uLoEFihIN0y5Ln+6LZJQ
RwjPBAdCSsU/99luMlK77z0=
-----END PRIVATE KEY-----""",
}

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class PlainCopyCipher:
    def encrypt(self, plaintext):
        return plaintext
    def decrypt(self, ciphertext):
        return ciphertext

class ImgPkgHeader(LittleEndianStructure):
    _pack_ = 1
    _fields_ = [('magic', c_char * 4),              #0 'IM*H'
                ('header_version', c_uint),         #4
                ('size', c_uint),                   #8
                ('reserved', c_ubyte * 4),          #12
                ('header_size', c_uint),            #16 Length of this header and following chunk headers
                ('signature_size', c_uint),         #20 Length of RSA signature located after chunk headers
                ('payload_size', c_uint),           #24 Length of the area after signature which contains data of all chunks
                ('target_size', c_uint),            #28
                ('os', c_ubyte),                    #32
                ('arch', c_ubyte),                  #33
                ('compression', c_ubyte),           #34
                ('anti_version', c_ubyte),          #35
                ('auth_alg', c_uint),               #36
                ('auth_key', c_char * 4),           #40 Auth key identifier
                ('enc_key', c_char * 4),            #44 Encryption key identifier
                ('scram_key', c_ubyte * 16),        #48 Encrypted Scramble key; used in versions > 0
                ('name', c_char * 32),              #64 Target Module name
                ('type', c_char * 4),               #96 Target Module type identifier; used in versions > 1
                ('version', c_uint),                #100
                ('date', c_uint),                   #104
                ('encr_cksum', c_uint),             #108 Checksum of encrypted data; used in versions > 1
                ('reserved2', c_ubyte * 16),        #112
                ('userdata', c_char * 16),          #128
                ('entry', c_ubyte * 8),             #144
                ('plain_cksum', c_uint),            #152 Checksum of decrypted (plaintext) data; used in versions > 1
                ('chunk_num', c_uint),              #156 Amount of chunks
                ('payload_digest', c_ubyte * 32),   #160 SHA256 of the payload
               ]                                    #192 is the end; chunk headers start after that

    def get_format_version(self):
        if self.magic != bytes("IM*H", "utf-8"):
            return 0
        if self.header_version == 0x0000:
            return 2016
        elif self.header_version == 0x0001:
            return 2017
        elif self.header_version == 0x0002:
            return 2018
        else:
            return 0

    def set_format_version(self, ver):
        if ver == 2016:
            self.magic = bytes("IM*H", "utf-8")
            self.header_version = 0x0000
        elif ver == 2017:
            self.magic = bytes("IM*H", "utf-8")
            self.header_version = 0x0001
        elif ver == 2018:
            self.magic = bytes("IM*H", "utf-8")
            self.header_version = 0x0002
        else:
            raise ValueError("Unsupported image format version.")

    def update_payload_size(self, payload_size):
        self.payload_size = payload_size
        self.target_size = self.header_size + self.signature_size + self.payload_size
        self.size = self.target_size

    def dict_export(self):
        d = OrderedDict()
        for (varkey, vartype) in self._fields_:
            if varkey.startswith('unk'):
                continue
            v = getattr(self, varkey)
            if isinstance(v, Array) and v._type_ == c_ubyte:
                d[varkey] = bytes(v)
            else:
                d[varkey] = v
        varkey = 'name'
        d[varkey] = d[varkey].decode("utf-8")
        varkey = 'auth_key'
        d[varkey] = d[varkey].decode("utf-8")
        varkey = 'enc_key'
        d[varkey] = d[varkey].decode("utf-8")
        varkey = 'type'
        d[varkey] = d[varkey].decode("utf-8")
        return d

    def ini_export(self, fp):
        d = self.dict_export()
        fp.write("# DJI Firmware Signer main header file.\n")
        fp.write(strftime("# Generated on %Y-%m-%d %H:%M:%S\n", gmtime()))
        varkey = 'name'
        fp.write("{:s}={:s}\n".format(varkey,d[varkey]))
        varkey = 'pkg_format'
        fp.write("{:s}={:d}\n".format(varkey,self.get_format_version()))
        varkey = 'version'
        fp.write("{:s}={:02d}.{:02d}.{:02d}.{:02d}\n".format(varkey, (d[varkey]>>24)&255, (d[varkey]>>16)&255, (d[varkey]>>8)&255, (d[varkey])&255))
        varkey = 'anti_version'
        fp.write("{:s}={:02d}.{:02d}.{:02d}.{:02d}\n".format(varkey, (d[varkey]>>24)&255, (d[varkey]>>16)&255, (d[varkey]>>8)&255, (d[varkey])&255))
        varkey = 'date'
        fp.write("{:s}={:s}\n".format(varkey,strftime("%Y-%m-%d",strptime("{:x}".format(d[varkey]), '%Y%m%d'))))
        varkey = 'enc_key'
        fp.write("{:s}={:s}\n".format(varkey,d[varkey]))
        varkey = 'auth_alg'
        fp.write("{:s}={:d}\n".format(varkey,d[varkey]))
        varkey = 'auth_key'
        fp.write("{:s}={:s}\n".format(varkey,d[varkey]))
        varkey = 'os'
        fp.write("{:s}={:d}\n".format(varkey,d[varkey]))
        varkey = 'arch'
        fp.write("{:s}={:d}\n".format(varkey,d[varkey]))
        varkey = 'compression'
        fp.write("{:s}={:d}\n".format(varkey,d[varkey]))
        varkey = 'type'
        fp.write("{:s}={:s}\n".format(varkey,d[varkey]))
        varkey = 'userdata'
        fp.write("{:s}={:s}\n".format(varkey,d[varkey].decode("utf-8"))) # not sure if string or binary
        varkey = 'entry'
        fp.write("{:s}={:s}\n".format(varkey,''.join("{:02X}".format(x) for x in d[varkey])))
        #varkey = 'scram_key' # we will add the key later, as this one is encrypted
        #fp.write("{:s}={:s}\n".format(varkey,"".join("{:02X}".format(x) for x in d[varkey])))

    def __repr__(self):
        d = self.dict_export()
        from pprint import pformat
        return pformat(d, indent=0, width=160)


class ImgChunkHeader(LittleEndianStructure):
    _pack_ = 1
    _fields_ = [('id', c_char * 4),          #0
                ('offset', c_uint),          #4
                ('size', c_uint),            #8
                ('attrib', c_uint),          #12
                ('address', c_ulonglong),    #16
                ('reserved', c_ubyte * 8),   #24
               ]                             #32 is the end

    def dict_export(self):
        d = OrderedDict()
        for (varkey, vartype) in self._fields_:
            if varkey.startswith('unk'):
                continue
            v = getattr(self, varkey)
            if isinstance(v, Array) and v._type_ == c_ubyte:
                d[varkey] = bytes(v)
            else:
                d[varkey] = v
        varkey = 'id'
        d[varkey] = d[varkey].decode("utf-8")
        return d

    def ini_export(self, fp):
        d = self.dict_export()
        fp.write("# DJI Firmware Signer chunk header file.\n")
        fp.write(strftime("# Generated on %Y-%m-%d %H:%M:%S\n", gmtime()))
        varkey = 'id'
        fp.write("{:s}={:s}\n".format(varkey,d[varkey]))
        varkey = 'attrib'
        fp.write("{:s}={:04X}\n".format(varkey,d[varkey]))
        #varkey = 'offset'
        #fp.write("{:s}={:04X}\n".format(varkey,d[varkey]))
        varkey = 'address'
        fp.write("{:s}={:08X}\n".format(varkey,d[varkey]))

    def __repr__(self):
        d = self.dict_export()
        from pprint import pformat
        return pformat(d, indent=0, width=160)


class ImgRSAPublicKey(LittleEndianStructure):
    _pack_ = 1
    _fields_ = [('len', c_int),      # 0: Length of n[] in number of uint32_t
                ('n0inv', c_uint),   # 4: -1 / n[0] mod 2^32
                ('n', c_uint * 64),  # 8: modulus as little endian array
                ('rr', c_uint * 64), # 264: R^2 as little endian array
                ('exponent', c_int)] # 520: 3 or 65537


def raise_or_warn(po, ex):
    """ Raise exception, unless force-continue parameter was used.
    """
    if (po.force_continue):
        eprint("{:s}: Warning: {:s} Continuing anyway.".format(po.sigfile,str(ex)))
    else:
        raise ex


def combine_int_array(int_arr, bits_per_entry):
    """ Makes one big numer out of an array of numbers.

    Allows to make pythonic big number out of little endian number stored in parts
    as a list.
    """
    ans = 0
    for i, val in enumerate(int_arr):
        ans += (val << i*bits_per_entry)
    return ans


def get_key_data(po, pkghead, enc_k_fourcc):
    """ Returns encryption/authentication key array for given FourCC.

    Accepts both string and variants of bytes.
    """
    if hasattr(enc_k_fourcc, 'decode'):
        enc_k_str = enc_k_fourcc.decode("utf-8")
    else:
        enc_k_str = str(enc_k_fourcc)
    enc_k_select = None

    for kstr in po.key_select:
        if enc_k_str == kstr[:4]:
            enc_k_select = kstr
            break

    key_list = []
    if enc_k_select is None:
        if enc_k_str in keys:
            enc_k_select = enc_k_str
        else:
            for kstr in keys:
                if enc_k_str == kstr[:4]:
                    key_list.append(kstr)

    if enc_k_select is not None:
        # Key selection was already made
        pass
    elif len(key_list) == 1:
        # There is only one key to choose from
        enc_k_select = key_list[0]
    elif len(key_list) > 1:
        # We have multiple matching keys; we do not have enough information to auto-choose correct one
        # (the key needs to be selected based of FW package version, we only have FW module version)
        enc_k_select = key_list[0]
        if (po.show_multiple_keys_warn):
            eprint("{}: Warning: '{:s}' matches multiple keys; using first, '{:s}'".format(po.sigfile,enc_k_str,enc_k_select))
            eprint("{}: Key choices: {:s}".format(po.sigfile,", ".join(key_list)))
            po.show_multiple_keys_warn = False

    if enc_k_select in keys.keys():
        enc_key = keys[enc_k_select]
    else:
        enc_key = None
    return enc_key

def imah_get_crypto_params(po, pkghead):
    # Get the encryption key
    enc_k_str = pkghead.enc_key.decode("utf-8")
    enc_key = get_key_data(po, pkghead, enc_k_str)
    if enc_key is None:
        eprint("{}: Warning: Cannot find enc_key '{:s}'".format(po.sigfile,enc_k_str))
        return (None, None, None)
    # Prepare initial values for AES
    if   pkghead.header_version == 2:
        if (po.verbose > 3):
            print("Key encryption key:\n{:s}".format(' '.join("{:02X}".format(x) for x in enc_key)))
        crypt_mode = AES.MODE_CTR
        cipher = AES.new(enc_key, AES.MODE_ECB)
        if (po.verbose > 3):
            print("Encrypted Scramble key:\n{:s}".format(' '.join("{:02X}".format(x) for x in pkghead.scram_key)))
        crypt_key = cipher.decrypt(bytes(pkghead.scram_key))
        # For CTR mode, 12 bytes of crypt_iv will be interpreted as nonce, and remaining 4 will be initial value of counter
        crypt_iv = bytes([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    elif pkghead.header_version == 1:
        if (po.verbose > 3):
            print("Key encryption key:\n{:s}".format(' '.join("{:02X}".format(x) for x in enc_key)))
        crypt_mode = AES.MODE_CBC
        cipher = AES.new(enc_key, AES.MODE_CBC, bytes([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))
        if (po.verbose > 3):
            print("Encrypted Scramble key:\n{:s}".format(' '.join("{:02X}".format(x) for x in pkghead.scram_key)))
        crypt_key = cipher.decrypt(bytes(pkghead.scram_key))
        crypt_iv = bytes([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    else:
        crypt_mode = AES.MODE_CBC
        crypt_key = enc_key
        crypt_iv = bytes(pkghead.scram_key)
    return (crypt_key, crypt_mode, crypt_iv)

def imah_get_auth_params(po, pkghead):
    # Get the key
    auth_k_str = pkghead.auth_key.decode("utf-8")
    auth_key_data = get_key_data(po, pkghead, auth_k_str)
    if auth_key_data is None:
        eprint("{}: Warning: Cannot find auth_key '{:s}'".format(po.sigfile,auth_k_str))
        return (None)
    if isinstance(auth_key_data, str):
        auth_key = RSA.importKey(auth_key_data)
    elif len(auth_key_data) == sizeof(ImgRSAPublicKey):
        auth_key_struct = ImgRSAPublicKey()
        memmove(addressof(auth_key_struct), auth_key_data, sizeof(auth_key_struct))
        auth_key_n = combine_int_array(auth_key_struct.n, 32)
        auth_key = RSA.construct( (auth_key_n, auth_key_struct.exponent, ) )
    else:
        eprint("{}: Warning: Unrecognized format of auth_key '{:s}'".format(po.sigfile,auth_k_str))
        return (None)
    return (auth_key)

def imah_compute_checksum(po, buf, start = 0):
    cksum = start
    for i in range(0, len(buf) // 4):
        v = int.from_bytes(buf[i*4:i*4+4], byteorder='little')
        cksum += v
    # last dword
    i = len(buf) // 4
    if i*4 < len(buf):
        last_buf = buf[i*4:i*4+4] + bytes(3 * [0])
        v = int.from_bytes(last_buf[:4], byteorder='little')
        cksum += v
    return (cksum) & ((2 ** 32) - 1)

def imah_write_fwsig_head(po, pkghead, minames):
    fname = "{:s}_head.ini".format(po.mdprefix)
    fwheadfile = open(fname, "w")
    pkghead.ini_export(fwheadfile)
    # Prepare initial values for AES
    if pkghead.header_version == 0: # Scramble key is used as initial vector
        fwheadfile.write("{:s}={:s}\n".format('scramble_iv',' '.join("{:02X}".format(x) for x in pkghead.scram_key)))
    else:
        crypt_key, _, _ = imah_get_crypto_params(po, pkghead)
        if crypt_key is None: # Scramble key is used, but we cannot decrypt it
            eprint("{}: Warning: Storing encrypted scramble key due to missing crypto config.".format(po.sigfile))
            fwheadfile.write("{:s}={:s}\n".format('scramble_key_encrypted',' '.join("{:02X}".format(x) for x in pkghead.scram_key)))
        else: # Store the decrypted scrable key
            fwheadfile.write("{:s}={:s}\n".format('scramble_key',' '.join("{:02X}".format(x) for x in crypt_key)))
    # Store list of modules/chunks to include
    fwheadfile.write("{:s}={:s}\n".format('modules',' '.join(minames)))
    fwheadfile.close()

def imah_read_fwsig_head(po):
    pkghead = ImgPkgHeader()
    fname = "{:s}_head.ini".format(po.mdprefix)
    parser = configparser.ConfigParser()

    with open(fname, "r") as lines:
        lines = itertools.chain(("[asection]",), lines)  # This line adds section header to ini
        parser.read_file(lines)
    # Set magic fields properly
    pkgformat = int(parser.get("asection", "pkg_format"))
    pkghead.set_format_version(pkgformat)
    # Set the rest of the fields
    pkghead.name = bytes(parser.get("asection", "name"), "utf-8")
    pkghead.userdata = bytes(parser.get("asection", "userdata"), "utf-8")
    # The only person at Dji who knew how to store dates must have been fired
    date_val = strptime(parser.get("asection", "date"),"%Y-%m-%d")
    pkghead.date = ((date_val.tm_year // 1000) << 28) | (((date_val.tm_year % 1000) // 100) << 24) | \
            (((date_val.tm_year % 100) // 10) << 20) | ((date_val.tm_year % 10) << 16) | \
            ((date_val.tm_mon // 10) << 12) | ((date_val.tm_mon % 10) << 8) | \
            ((date_val.tm_mday // 10) << 4) | (date_val.tm_mday % 10)
    version_s = parser.get("asection", "version")
    version_m = re.search('(?P<major>[0-9]+)[.](?P<minor>[0-9]+)[.](?P<build>[0-9]+)[.](?P<rev>[0-9]+)', version_s)
    pkghead.version = ((int(version_m.group("major"),10)&0xff)<<24) + ((int(version_m.group("minor"),10)&0xff)<<16) + \
            ((int(version_m.group("build"),10)&0xff)<<8) + ((int(version_m.group("rev"),10)&0xff))
    anti_version_s = parser.get("asection", "anti_version")
    anti_version_m = re.search('(?P<major>[0-9]+)[.](?P<minor>[0-9]+)[.](?P<build>[0-9]+)[.](?P<rev>[0-9]+)', anti_version_s)
    pkghead.anti_version = ((int(anti_version_m.group("major"),10)&0xff)<<24) + ((int(anti_version_m.group("minor"),10)&0xff)<<16) + \
            ((int(anti_version_m.group("build"),10)&0xff)<<8) + ((int(anti_version_m.group("rev"),10)&0xff))
    pkghead.enc_key = bytes(parser.get("asection", "enc_key"), "utf-8")
    pkghead.auth_key = bytes(parser.get("asection", "auth_key"), "utf-8")
    pkghead.auth_alg = int(parser.get("asection", "auth_alg"))
    pkghead.os = int(parser.get("asection", "os"))
    pkghead.arch = int(parser.get("asection", "arch"))
    pkghead.compression = int(parser.get("asection", "compression"))
    pkghead.type = bytes(parser.get("asection", "type"), "utf-8")
    entry_bt = bytes.fromhex(parser.get("asection", "entry"))
    pkghead.entry = (c_ubyte * len(entry_bt)).from_buffer_copy(entry_bt)

    if po.random_scramble:
        scramble_needs_encrypt = (pkghead.header_version != 0)
        scramble_key = os.urandom(16)
        pkghead.scram_key = (c_ubyte * len(scramble_key)).from_buffer_copy(scramble_key)

    elif pkghead.header_version == 0: # Scramble key is used as initial vector
        scramble_needs_encrypt = False
        scramble_iv = bytes.fromhex(parser.get("asection", "scramble_iv"))
        pkghead.scram_key = (c_ubyte * len(scramble_iv)).from_buffer_copy(scramble_iv)

    else: # Scrable key should be encrypted
        if parser.has_option("asection", "scramble_key"):
            scramble_needs_encrypt = True
            scramble_key = bytes.fromhex(parser.get("asection", "scramble_key"))
        else: # Maybe we have pre-encrypted version?
            scramble_needs_encrypt = False
            scramble_key = bytes.fromhex(parser.get("asection", "scramble_key_encrypted"))

        if scramble_key is not None:
            pkghead.scram_key = (c_ubyte * len(scramble_key)).from_buffer_copy(scramble_key)
        else:
            eprint("{}: Warning: Scramble key not found in header and not set to ramdom; zeros will be used.".format(po.sigfile))

    minames_s = parser.get("asection", "modules")
    minames = minames_s.split(' ')
    pkghead.chunk_num = len(minames)
    pkghead.header_size = sizeof(pkghead) + sizeof(ImgChunkHeader)*pkghead.chunk_num
    pkghead.signature_size = 256
    pkghead.update_payload_size(0)

    del parser

    if scramble_needs_encrypt:
        # Get the encryption key
        enc_k_str = pkghead.enc_key.decode("utf-8")
        enc_key = get_key_data(po, pkghead, enc_k_str)
        if enc_key is None:
            eprint("{}: Warning: Cannot find enc_key '{:s}'; scramble key left unencrypted.".format(fwsigfile.name,enc_k_str))
        else:
            cipher = AES.new(enc_key, AES.MODE_CBC, bytes([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))
            crypt_key_enc = cipher.encrypt(bytes(pkghead.scram_key))
            pkghead.scram_key = (c_ubyte * 16)(*list(crypt_key_enc))

    return (pkghead, minames, pkgformat)

def imah_write_fwentry_head(po, i, e, miname, can_decrypt):
    fname = "{:s}_{:s}.ini".format(po.mdprefix,miname)
    fwheadfile = open(fname, "w")
    e.ini_export(fwheadfile)
    if not can_decrypt: # If we're exporting without decryption, we must retain decrypted size
        fwheadfile.write("{:s}={:s}\n".format('size',"{:d}".format(e.size)))
    fwheadfile.close()

def imah_read_fwentry_head(po, i, miname):
    chunk = ImgChunkHeader()
    fname = "{:s}_{:s}.ini".format(po.mdprefix,miname)
    parser = configparser.ConfigParser()
    with open(fname, "r") as lines:
        lines = itertools.chain(("[asection]",), lines)  # This line adds section header to ini
        parser.read_file(lines)
    id_s = parser.get("asection", 'id')
    chunk.id = bytes(id_s, "utf-8")
    attrib_s = parser.get("asection", 'attrib')
    chunk.attrib = int(attrib_s, 16)
    size_s = parser.get("asection", 'size',fallback="0")
    chunk.size = int(size_s,0)
    #offset_s = parser.get("asection", 'offset')
    #chunk.offset = int(offset_s, 16)
    address_s = parser.get("asection", 'address')
    chunk.address = int(address_s, 16)
    del parser
    return (chunk)

def imah_unsign(po, fwsigfile):

    # Decode the image header
    pkghead = ImgPkgHeader()
    if fwsigfile.readinto(pkghead) != sizeof(pkghead):
        raise EOFError("Could not read signed image file header.")

    # Check the magic
    pkgformat = pkghead.get_format_version()
    if pkgformat == 0:
        raise_or_warn(po, ValueError("Unexpected magic value in main header; input file is not a signed image."))

    if pkghead.size != pkghead.target_size:
        eprint("{}: Warning: Header field 'size' is different that 'target_size'; the tool is not designed to handle this.".format(fwsigfile.name))

    if not all(v == 0 for v in pkghead.reserved):
        eprint("{}: Warning: Header field 'reserved' is non-zero; the tool is not designed to handle this.".format(fwsigfile.name))

    if not all(v == 0 for v in pkghead.reserved2):
        eprint("{}: Warning: Header field 'reserved2' is non-zero; the tool is not designed to handle this.".format(fwsigfile.name))

    if pkgformat < 2018:
        if pkghead.encr_cksum != 0:
            eprint("{}: Warning: Header field 'encr_cksum' is non-zero; this is only allowed in newer formats.".format(fwsigfile.name))

        if pkghead.plain_cksum != 0:
            eprint("{}: Warning: Header field 'plain_cksum' is non-zero; this is only allowed in newer formats.".format(fwsigfile.name))

    if (po.verbose > 0):
        print("{}: Unpacking image...".format(fwsigfile.name))
    if (po.verbose > 1):
        print(pkghead)

    # Read chunk headers of the image
    chunks = []
    for i in range(0, pkghead.chunk_num):
        chunk = ImgChunkHeader()
        if fwsigfile.readinto(chunk) != sizeof(chunk):
            raise EOFError("Could not read signed image chunk {:d} header.".format(i))
        chunks.append(chunk)

    # Compute header hash and checksum; for checksum, we need a header without checksum stored
    pkghead_nosum = copy(pkghead)
    pkghead_nosum.encr_cksum = 0
    checksum_enc = imah_compute_checksum(po, bytes(pkghead_nosum))
    header_digest = SHA256.new()
    header_digest.update(bytes(pkghead))
    for i, chunk in enumerate(chunks):
        header_digest.update(bytes(chunk))
        checksum_enc = imah_compute_checksum(po, bytes(chunk), checksum_enc)
    if (po.verbose > 2):
        print("Computed header checksum 0x{:08X} and digest:\n{:s}".format(checksum_enc, ' '.join("{:02X}".format(x) for x in header_digest.digest())))

    if pkghead.signature_size != 256: # 2048 bit key length
        raise_or_warn(po, ValueError("Signed image file head signature has unexpected size."))
    head_signature = fwsigfile.read(pkghead.signature_size)
    if len(head_signature) != pkghead.signature_size:
        raise EOFError("Could not read signature of signed image file head.")

    auth_key = imah_get_auth_params(po, pkghead)
    try:
        if pkgformat >= 2018:
            mgf = lambda x, y: pss.MGF1(x, y, SHA256)
            salt_bytes = header_digest.digest_size
            header_signer = pss.new(auth_key, mask_func=mgf, salt_bytes=salt_bytes)
            # The PSS signer does not return value, just throws exception of a fail
            header_signer.verify(header_digest, head_signature)
            signature_match = True
        else:
            header_signer = PKCS1_v1_5.new(auth_key)
            signature_match = header_signer.verify(header_digest, head_signature)
    except Exception as ex:
        print("{}: Warning: Image file head signature verification caused cryptographic exception: {}".format(fwsigfile.name,str(ex)))
        signature_match = False
    if signature_match:
        if (po.verbose > 1):
            print("{}: Image file head signature verification passed.".format(fwsigfile.name))
    else:
        raise_or_warn(po, ValueError("Image file head signature verification failed."))

    # Finish computing encrypted data checksum; cannot do that during decryption as we would
    # likely miss some padding, which is also included in the checksum
    remain_enc_n = pkghead.payload_size
    while remain_enc_n > 0:
        copy_buffer = fwsigfile.read(min(1024 * 1024, remain_enc_n))
        checksum_enc = imah_compute_checksum(po, copy_buffer, checksum_enc)
        remain_enc_n -= 1024 * 1024
    checksum_enc = (2 ** 32) - checksum_enc

    if pkgformat < 2018:
        pass # No checksums are used in these formats
    elif pkghead.encr_cksum == checksum_enc:
        if (po.verbose > 1):
            print("{}: Encrypted data checksum 0x{:08X} matches.".format(fwsigfile.name, checksum_enc))
    else:
        if (po.verbose > 1):
            print("{}: Encrypted data checksum 0x{:08X}, expected 0x{:08X}.".format(fwsigfile.name, checksum_enc, pkghead.encr_cksum))
        raise_or_warn(po, ValueError("Encrypted data checksum verification failed."))

    # Prepare array of names; "0" will mean empty index
    minames = ["0"]*len(chunks)
    # Name the modules after target component
    for i, chunk in enumerate(chunks):
        if chunk.size > 0:
            d = chunk.dict_export()
            minames[i] = "{:s}".format(d['id'])
    # Rename targets in case of duplicates
    minames_seen = set()
    for i in range(len(minames)):
        miname = minames[i]
        if miname in minames_seen:
            # Add suffix a..z to multiple uses of the same module
            for miname_suffix in range(97,110):
                if miname+chr(miname_suffix) not in minames_seen:
                    break
            # Show warning the first time duplicate is found
            if (miname_suffix == 97):
                eprint("{}: Warning: Found multiple chunks '{:s}'; invalid signed image.".format(fwsigfile.name,miname))
            minames[i] = miname+chr(miname_suffix)
        minames_seen.add(minames[i])
    minames_seen = None

    imah_write_fwsig_head(po, pkghead, minames)

    crypt_key, crypt_mode, crypt_iv = imah_get_crypto_params(po, pkghead)
    if (crypt_key is not None) and (po.verbose > 2):
        print("Scramble key:\n{:s}".format(' '.join("{:02X}".format(x) for x in crypt_key)))

    # Output the chunks
    checksum_dec = 0
    num_skipped = 0
    single_cipher = None # IMaH v1 creates a new cipher for each chunk, IMaH v2 reuses a single cipher
    for i, chunk in enumerate(chunks):

        chunk_fname= "{:s}_{:s}.bin".format(po.mdprefix,minames[i])

        if (chunk.attrib & 0x01) or (pkghead.enc_key == b''): # Not encrypted chunk
            cipher = PlainCopyCipher()
            pad_cnt = 0
            if (po.verbose > 0):
                print("{}: Unpacking plaintext chunk '{:s}'...".format(fwsigfile.name,minames[i]))
            can_decrypt = True

        elif crypt_key is not None: # Encrypted chunk (have key as well)
            if crypt_mode == AES.MODE_CTR:
                if single_cipher is None:
                    init_cf = int.from_bytes(crypt_iv[12:16], byteorder='big')
                    countf = Counter.new(32, crypt_iv[:12], initial_value=init_cf)
                    cipher = AES.new(crypt_key, crypt_mode, counter=countf)
                    single_cipher = cipher
                else:
                    cipher = single_cipher
                dji_block_size = 32
            else:
                cipher = AES.new(crypt_key, crypt_mode, iv=crypt_iv)
                # the data is really padded to 32, but we do not care as we reset state for every chunk
                dji_block_size = AES.block_size
            pad_cnt = (dji_block_size - chunk.size % dji_block_size) % dji_block_size
            if (po.verbose > 0):
                print("{}: Unpacking encrypted chunk '{:s}'...".format(fwsigfile.name,minames[i]))
            can_decrypt = True

        else: # Missing encryption key
            eprint("{}: Warning: Cannot decrypt chunk '{:s}'; crypto config missing.".format(fwsigfile.name,minames[i]))
            if (not po.force_continue):
                num_skipped += 1
                continue
            if (po.verbose > 0):
                print("{}: Copying still encrypted chunk '{:s}'...".format(fwsigfile.name,minames[i]))
            cipher = PlainCopyCipher()
            pad_cnt = (AES.block_size - chunk.size % AES.block_size) % AES.block_size
            can_decrypt = False

        imah_write_fwentry_head(po, i, chunk, minames[i], can_decrypt)

        if (po.verbose > 1):
            print(str(chunk))

        # Decrypt and write the data
        fwsigfile.seek(pkghead.header_size + pkghead.signature_size + chunk.offset, 0)
        fwitmfile = open(chunk_fname, "wb")
        remain_enc_n = chunk.size + pad_cnt
        remain_dec_n = chunk.size
        if not can_decrypt: # If storing encrypted, include padding
            remain_dec_n += pad_cnt
        while remain_enc_n > 0:
            # read block limit must be a multiplication of encryption block size
            # ie AES.block_size is fixed at 16 bytes
            copy_buffer = fwsigfile.read(min(1024 * 1024, remain_enc_n))
            if not copy_buffer:
                eprint("{}: Warning: Chunk '{:s}' truncated.".format(fwsigfile.name,minames[i]))
                num_skipped += 1
                break
            remain_enc_n -= len(copy_buffer)
            copy_buffer = cipher.decrypt(copy_buffer)
            checksum_dec = imah_compute_checksum(po, copy_buffer, checksum_dec)
            if remain_dec_n >= len(copy_buffer):
                fwitmfile.write(copy_buffer)
                remain_dec_n -= len(copy_buffer)
            else:
                if (po.verbose > 2):
                    print("Chunk padding: {:s}".format(str(copy_buffer[-len(copy_buffer)+remain_dec_n:])))
                fwitmfile.write(copy_buffer[:remain_dec_n])
                remain_dec_n = 0
        fwitmfile.close()

    print("{}: Un-signed {:d} chunks, skipped/truncated {:d} chunks.".format(fwsigfile.name,len(chunks)-num_skipped, num_skipped))
    if pkgformat < 2018:
        pass # No checksums are used in these formats
    elif pkghead.plain_cksum == checksum_dec:
        if (po.verbose > 1):
            print("{}: Decrypted chunks checksum 0x{:08X} matches.".format(fwsigfile.name, checksum_dec))
    else:
        if (po.verbose > 1):
            print("{}: Decrypted chunks checksum 0x{:08X}, expected 0x{:08X}.".format(fwsigfile.name, checksum_dec, pkghead.plain_cksum))
        raise_or_warn(po, ValueError("Decrypted chunks checksum verification failed."))

def imah_sign(po, fwsigfile):
    # Read headers from INI files
    (pkghead, minames, pkgformat) = imah_read_fwsig_head(po)
    chunks = []
    # Create header entry for each chunk
    for i, miname in enumerate(minames):
        if miname == "0":
            chunk = ImgChunkHeader()
        else:
            chunk = imah_read_fwentry_head(po, i, miname)
        chunks.append(chunk)
    # Write the unfinished headers
    fwsigfile.write(bytes(pkghead))
    for chunk in chunks:
        fwsigfile.write(bytes(chunk))
    fwsigfile.write(b"\0" * pkghead.signature_size)
    # prepare encryption
    crypt_key, crypt_mode, crypt_iv = imah_get_crypto_params(po, pkghead)
    # Write module data
    checksum_dec = 0
    single_cipher = None # IMaH v1 creates a new cipher for each chunk, IMaH v2 reuses a single cipher
    payload_digest = SHA256.new()
    for i, miname in enumerate(minames):
        chunk = chunks[i]
        chunk.offset = fwsigfile.tell() - pkghead.header_size - pkghead.signature_size
        if miname == "0":
            if (po.verbose > 0):
                print("{}: Empty chunk index {:d}".format(fwsigfile.name,i))
            continue

        if (chunk.attrib & 0x01) or (pkghead.enc_key == b''): # Not encrypted chunk
            cipher = PlainCopyCipher()
            if (po.verbose > 0):
                print("{}: Packing plaintext chunk '{:s}'...".format(fwsigfile.name,minames[i]))
            can_decrypt = True

        elif crypt_key != None: # Encrypted chunk (have key as well)
            if crypt_mode == AES.MODE_CTR:
                if single_cipher is None:
                    init_cf = int.from_bytes(crypt_iv[12:16], byteorder='big')
                    countf = Counter.new(32, crypt_iv[:12], initial_value=init_cf)
                    cipher = AES.new(crypt_key, crypt_mode, counter=countf)
                    single_cipher = cipher
                else:
                    cipher = single_cipher
            else:
                cipher = AES.new(crypt_key, crypt_mode, iv=crypt_iv)
            if (po.verbose > 0):
                print("{}: Packing and encrypting chunk '{:s}'...".format(fwsigfile.name,minames[i]))
            can_decrypt = True

        else: # Missing encryption key
            eprint("{}: Warning: Cannot encrypt chunk '{:s}'; crypto config missing.".format(fwsigfile.name,minames[i]))
            raise_or_warn(po, ValueError("Unsupported encryption configuration."))
            if (po.verbose > 0):
                print("{}: Copying already encrypted chunk '{:s}'...".format(fwsigfile.name,minames[i]))
            cipher = PlainCopyCipher()
            can_decrypt = False

        if (po.verbose > 1):
            print(str(chunk))

        chunk_fname= "{:s}_{:s}.bin".format(po.mdprefix,miname)
        # Copy chunk data and compute digest
        fwitmfile = open(chunk_fname, "rb")
        # Chunks in new formats are padded with zeros and then encrypted; for older formats,
        # the padding rules are more convoluted, and also change slightly between platforms
        if pkgformat >= 2018:
            dji_block_size = 32
        else:
            dji_block_size = AES.block_size
        decrypted_n = 0
        while True:
            # read block limit must be a multiplication of encryption block size
            # ie AES.block_size is fixed at 16 bytes
            copy_buffer = fwitmfile.read(1024 * 1024)
            if not copy_buffer:
                break
            decrypted_n += len(copy_buffer)
            # Pad the payload to AES.block_size = 16
            if (len(copy_buffer) % dji_block_size) != 0:
                pad_cnt = dji_block_size - (len(copy_buffer) % dji_block_size)
                pad_buffer = b"\0" * pad_cnt
                copy_buffer += pad_buffer
            checksum_dec = imah_compute_checksum(po, copy_buffer, checksum_dec)
            copy_buffer = cipher.encrypt(copy_buffer)
            payload_digest.update(copy_buffer)
            fwsigfile.write(copy_buffer)
        fwitmfile.close()
        # Pad with zeros at end, for no real reason
        dji_block_size = 32
        if (fwsigfile.tell() - chunk.offset) % dji_block_size != 0:
            pad_cnt = dji_block_size - ((fwsigfile.tell() - chunk.offset) % dji_block_size)
            pad_buffer = b"\0" * pad_cnt
            payload_digest.update(pad_buffer) # why Dji includes padding in digest?
            fwsigfile.write(pad_buffer)
        # Update size of the chunk in header; skip that if the chunk was pre-encrypted and correct size was stored in INI
        if can_decrypt or chunk.size == 0:
            chunk.size = decrypted_n
        elif  (decrypted_n <= chunk.size) or (decrypted_n >= chunk.size + dji_block_size):
            eprint("{}: Warning: Chunk '{:s}' size from INI is incorrect, ignoring".format(fwsigfile.name,minames[i]))
            chunk.size = decrypted_n
        chunks[i] = chunk

    pkghead.update_payload_size(fwsigfile.tell() - pkghead.header_size - pkghead.signature_size)
    if pkgformat >= 2018:
        pkghead.plain_cksum = checksum_dec
        if (po.verbose > 1):
            print("{}: Decrypted chunks checksum 0x{:08X} stored".format(fwsigfile.name, checksum_dec))
    pkghead.payload_digest = (c_ubyte * 32)(*list(payload_digest.digest()))
    if (po.verbose > 2):
        print("{}: Computed payload digest:\n{:s}".format(fwsigfile.name, ' '.join("{:02X}".format(x) for x in pkghead.payload_digest)))

    # Compute encrypted data checksum; cannot do that during encryption as we
    # need header with all fields filled, except of the checksum ofc.
    checksum_enc = imah_compute_checksum(po, bytes(pkghead))
    for i, chunk in enumerate(chunks):
        checksum_enc = imah_compute_checksum(po, bytes(chunk), checksum_enc)
    if (po.verbose > 2):
        print("{}: Computed header checksum 0x{:08X}".format(fwsigfile.name, checksum_enc))

    if pkgformat >= 2018:
        fwsigfile.seek(pkghead.header_size + pkghead.signature_size, os.SEEK_SET)
        remain_enc_n = pkghead.payload_size
        while remain_enc_n > 0:
            copy_buffer = fwsigfile.read(min(1024 * 1024, remain_enc_n))
            checksum_enc = imah_compute_checksum(po, copy_buffer, checksum_enc)
            remain_enc_n -= 1024 * 1024
        checksum_enc = (2 ** 32) - checksum_enc
        pkghead.encr_cksum = checksum_enc
        if (po.verbose > 1):
            print("{}: Encrypted data checksum 0x{:08X} stored".format(fwsigfile.name, checksum_enc))

    # Write all headers again
    fwsigfile.seek(0, os.SEEK_SET)
    fwsigfile.write(bytes(pkghead))
    if (po.verbose > 1):
        print(str(pkghead))
    for chunk in chunks:
        fwsigfile.write(bytes(chunk))
        if (po.verbose > 1):
            print(str(chunk))

    # Compute header hash, and use it to sign the header
    header_digest = SHA256.new()
    header_digest.update(bytes(pkghead))
    for i, chunk in enumerate(chunks):
        header_digest.update(bytes(chunk))
    if (po.verbose > 2):
        print("{}: Computed header digest:\n{:s}".format(fwsigfile.name, ' '.join("{:02X}".format(x) for x in header_digest.digest())))

    auth_key = imah_get_auth_params(po, pkghead)
    if not hasattr(auth_key, 'd'):
        raise ValueError("Cannot compute image file head signature, auth key '{:s}' has no private part.".format(pkghead.auth_key.decode("utf-8")))

    if pkgformat >= 2018:
        mgf = lambda x, y: pss.MGF1(x, y, SHA256)
        salt_bytes = header_digest.digest_size
        header_signer = pss.new(auth_key, mask_func=mgf, salt_bytes=salt_bytes)
    else:
        header_signer = PKCS1_v1_5.new(auth_key)
    head_signature = header_signer.sign(header_digest)
    fwsigfile.write(head_signature)

def main():
    """ Main executable function.

    Its task is to parse command line options and call a function which performs requested command.
    """
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("-i", "--sigfile", default="", type=str,
          help="signed and encrypted IM*H firmware module file")

    parser.add_argument("-m", "--mdprefix", default="", type=str,
          help="file name prefix for the single un-signed and unencrypted " \
           "firmware module (defaults to base name of signed firmware file)")

    parser.add_argument("-f", "--force-continue", action="store_true",
          help="force continuing execution despite warning signs of issues")

    parser.add_argument("-r", "--random-scramble", action="store_true",
          help="while signing, use random scramble vector instead of from INI")

    parser.add_argument("-k", "--key-select", default=[], action='append',
          help=("select a specific key to be used for given four character code, "
          "if multiple keys match this fourcc"))

    parser.add_argument("-v", "--verbose", action="count", default=0,
          help="increases verbosity level; max level is set by -vvv")

    subparser = parser.add_mutually_exclusive_group(required=True)

    subparser.add_argument("-u", "--unsign", action="store_true",
          help="un-sign and decrypt the firmware module")

    subparser.add_argument("-s", "--sign", action="store_true",
          help="sign and encrypt the firmware module")

    subparser.add_argument("--version", action='version', version="%(prog)s {version} by {author}"
            .format(version=__version__,author=__author__),
          help="display version information and exit")

    po = parser.parse_args()

    if len(po.sigfile) > 0 and len(po.mdprefix) == 0:
        po.mdprefix = os.path.splitext(os.path.basename(po.sigfile))[0]
    elif len(po.mdprefix) > 0 and len(po.sigfile) == 0:
        po.sigfile = po.mdprefix + ".sig"
    po.show_multiple_keys_warn = True

    if po.unsign:

        if (po.verbose > 0):
            print("{}: Opening for extraction and un-signing".format(po.sigfile))
        fwsigfile = open(po.sigfile, "rb")

        imah_unsign(po, fwsigfile)

        fwsigfile.close();

    elif po.sign:

        if (po.verbose > 0):
            print("{}: Opening for creation and signing".format(po.sigfile))
        fwsigfile = open(po.sigfile, "w+b")

        imah_sign(po, fwsigfile)

        fwsigfile.close();

    else:

        raise NotImplementedError('Unsupported command.')

if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        eprint("Error: "+str(ex))
        #raise
        sys.exit(10)
