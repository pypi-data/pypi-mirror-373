#!/usr/bin/python3
# encoding: utf-8
# SPDX-FileCopyrightText: 2024 FC (Fay) Stegerman <flx@obfusk.net>
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import struct
import zipfile

from collections import namedtuple
from typing import BinaryIO, Optional

ZipData = namedtuple("ZipData", ("cd_offset", "eocd_offset", "cd_and_eocd"))

DEFAULT_PAGE_SIZE = 4


class Error(RuntimeError):
    """Error
    """
    pass


def zipalign(
    input_apk: str,
    output_apk: str,
    *,
    page_align: bool = False,
    page_size: Optional[int] = None,
    pad_like_apksigner: bool = False,
    replace: bool = False,
    copy_extra: bool = False,
    update_lfh: bool = True,
) -> None:
    """zipalign

    Args:
        input_apk (str): input APK
        output_apk (str): output APK path
        page_align (bool, optional): Align page. Defaults to False.
        page_size (Optional[int], optional): page size. Defaults to None.
        pad_like_apksigner (bool, optional): pad like apksigner. Defaults to False.
        replace (bool, optional): replace. Defaults to False.
        copy_extra (bool, optional): copy extra. Defaults to False.
        update_lfh (bool, optional): update lfh. Defaults to True.
    """
    with zipfile.ZipFile(input_apk, "r") as zf:
        infos = zf.infolist()
    zdata = zip_data(input_apk)
    offsets = {}
    with open(input_apk, "rb") as fhi, open(output_apk, "w+b") as fho:
        for info in sorted(infos, key=lambda info: info.header_offset):
            off_i = fhi.tell()
            if info.header_offset > off_i:
                extra_bytes = info.header_offset - off_i
                if copy_extra:
                    fho.write(fhi.read(extra_bytes))
                else:
                    fhi.seek(extra_bytes, os.SEEK_CUR)
            hdr = fhi.read(30)
            if hdr[:4] != b"\x50\x4b\x03\x04":
                raise Error("Expected local file header signature")
            n, m = struct.unpack("<HH", hdr[26:30])
            hdr += fhi.read(n + m)
            if info.filename in offsets:
                raise Error(f"Duplicate ZIP entry: {info.filename!r}")
            offsets[info.filename] = off_o = fho.tell()
            if info.compress_type == 0:
                hdr = _align_zip_entry(
                    info,
                    hdr,
                    n,
                    m,
                    off_o,
                    page_align=page_align,
                    page_size=page_size,
                    pad_like_apksigner=pad_like_apksigner,
                    replace=replace,
                )
            if info.flag_bits & 0x08:
                fhi.seek(info.compress_size, os.SEEK_CUR)
                data_descriptor = fhi.read(12)
                if data_descriptor[:4] == b"\x50\x4b\x07\x08":
                    data_descriptor += fhi.read(4)
                fhi.seek(-(info.compress_size + len(data_descriptor)), os.SEEK_CUR)
                if update_lfh:
                    hdr = hdr[:14] + data_descriptor[-12:] + hdr[26:]
            else:
                data_descriptor = b""
            fho.write(hdr)
            _copy_bytes(fhi, fho, info.compress_size + len(data_descriptor))
        extra_bytes = zdata.cd_offset - fhi.tell()
        if copy_extra:
            _copy_bytes(fhi, fho, extra_bytes)
        else:
            fhi.seek(extra_bytes, os.SEEK_CUR)
        cd_offset = fho.tell()
        for info in infos:
            hdr = fhi.read(46)
            if hdr[:4] != b"\x50\x4b\x01\x02":
                raise Error("Expected central directory file header signature")
            n, m, k = struct.unpack("<HHH", hdr[28:34])
            hdr += fhi.read(n + m + k)
            off = int.to_bytes(offsets[info.filename], 4, "little")
            hdr = hdr[:42] + off + hdr[46:]
            fho.write(hdr)
        eocd_offset = fho.tell()
        fho.write(zdata.cd_and_eocd[zdata.eocd_offset - zdata.cd_offset :])
        fho.seek(eocd_offset + 8)
        fho.write(
            struct.pack("<HHLL", len(offsets), len(offsets), eocd_offset - cd_offset, cd_offset)
        )


# NB: doesn't sync local & CD headers!
def _align_zip_entry(
    info: zipfile.ZipInfo,
    hdr: bytes,
    n: int,
    m: int,
    off_o: int,
    *,
    page_align: bool = False,
    page_size: Optional[int] = None,
    pad_like_apksigner: bool = False,
    replace: bool = False,
) -> bytes:
    """_align_zip_entry

    Args:
        info (zipfile.ZipInfo): _description_
        hdr (bytes): _description_
        n (int): _description_
        m (int): _description_
        off_o (int): _description_
        page_align (bool, optional): _description_. Defaults to False.
        page_size (Optional[int], optional): _description_. Defaults to None.
        pad_like_apksigner (bool, optional): _description_. Defaults to False.
        replace (bool, optional): _description_. Defaults to False.

    Returns:
        bytes: _description_
    """
    psize = DEFAULT_PAGE_SIZE if page_size is None else page_size
    align = psize * 1024 if page_align and info.filename.endswith(".so") else 4
    new_off = 30 + n + m + off_o
    old_xtr = hdr[30 + n : 30 + n + m]
    new_xtr = b""
    while len(old_xtr) >= 4:
        hdr_id, size = struct.unpack("<HH", old_xtr[:4])
        if size > len(old_xtr) - 4:
            break
        if not (hdr_id == 0 and size == 0):
            if hdr_id == 0xD935:
                if size >= 2:
                    align = int.from_bytes(old_xtr[4:6], "little")
            else:
                new_xtr += old_xtr[: size + 4]
        old_xtr = old_xtr[size + 4 :]
    if replace or new_off % align != 0:
        if pad_like_apksigner:
            pad = (align - (new_off - m + len(new_xtr) + 6) % align) % align
            xtr = new_xtr + struct.pack("<HHH", 0xD935, 2 + pad, align) + pad * b"\x00"
        else:
            pad = (align - (new_off - m + len(new_xtr)) % align) % align
            xtr = new_xtr + pad * b"\x00"
        m_b = int.to_bytes(len(xtr), 2, "little")
        hdr = hdr[:28] + m_b + hdr[30 : 30 + n] + xtr
    return hdr


def _copy_bytes(fhi: BinaryIO, fho: BinaryIO, size: int, blocksize: int = 4096) -> None:
    """_copy_bytes

    Args:
        fhi (BinaryIO): _description_
        fho (BinaryIO): _description_
        size (int): _description_
        blocksize (int, optional): _description_. Defaults to 4096.

    Raises:
        Error: _description_
    """
    while size > 0:
        data = fhi.read(min(size, blocksize))
        if not data:
            break
        size -= len(data)
        fho.write(data)
    if size != 0:
        raise Error("Unexpected EOF")


def zip_data(apkfile: str, count: int = 1024) -> ZipData:
    """zip_data

    Args:
        apkfile (str): _description_
        count (int, optional): _description_. Defaults to 1024.

    Raises:
        Error: _description_

    Returns:
        ZipData: _description_
    """
    with open(apkfile, "rb") as fh:
        fh.seek(-min(os.path.getsize(apkfile), count), os.SEEK_END)
        data = fh.read()
        pos = data.rfind(b"\x50\x4b\x05\x06")
        if pos == -1:
            raise Error("Expected end of central directory record (EOCD)")
        fh.seek(pos - len(data), os.SEEK_CUR)
        eocd_offset = fh.tell()
        fh.seek(16, os.SEEK_CUR)
        cd_offset = int.from_bytes(fh.read(4), "little")
        fh.seek(cd_offset)
        cd_and_eocd = fh.read()
    return ZipData(cd_offset, eocd_offset, cd_and_eocd)


# vim: set tw=80 sw=4 sts=4 et fdm=marker :
