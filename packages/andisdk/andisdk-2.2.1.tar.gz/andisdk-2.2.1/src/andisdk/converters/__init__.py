# Copyright (C) 2023-2024 Technica Engineering GmbH. All rights reserved.
"""
andi.converters
===============

Helper module to convert PCAP or PCAPNG files with various options.
See documentation for more details :doc:`/Tutorials/Converters`.
"""

import sys
import typing 
if not (typing.TYPE_CHECKING or ('sphinx' in sys.modules)):
    import clr
from typing import Optional,Dict,List
from pathlib import Path
import os
from .utils import AnyPath, temp_path, same_file, compress, fspath
from .andisdk_converter import andisdk_convert
from .tecmp_converter import tecmp_convert


def convert(infile: AnyPath, outfile: AnyPath, *, tecmp_mapping: Optional[Dict[int, str]] = None, drop_replay_data: Optional[bool] = False) -> None:
    """
    Args:
        infile (AnyPath): The path to the input network packet capture file.
        outfile (AnyPath): The path to the output file, including optional compression.
        tecmp_mapping (Optional[Dict[int, str]]): A dictionary mapping technique IDs to their names, optional.
        drop_replay_data (Optional[bool]): Drop messages with type replay data, optional.

    Returns:
        None
    """
    out_types = tuple(Path(outfile).suffixes)
    if not out_types:
        raise ValueError(f"Unknown output format for {outfile}")

    if out_types[-1] == '.gz':
        outtmp = fspath(Path(outfile).with_suffix(''))
        if same_file(infile, outtmp):
            # If only compression is requested, then we don't need to convert
            compress(infile)
        else:
            convert(infile, outtmp, tecmp_mapping=tecmp_mapping)
            compress(outtmp)
            os.remove(outtmp)
        return

    in_type = Path(infile).suffix.lower()
    if in_type not in (".pcap", ".pcapng"):
        raise ValueError(f"File {infile} seems to not be a PCAP(NG) file.")

    if out_types[-2:] == (".unwrap", ".pcapng"):
        tecmp_convert(infile, outfile, tecmp_mapping=tecmp_mapping, drop_replay_data=drop_replay_data)
    elif out_types[-1] == ".asc":
        if tecmp_mapping:
            with temp_path(suffix='.unwrap.pcapng') as tmpfile:
                tecmp_convert(infile, tmpfile, tecmp_mapping=tecmp_mapping, drop_replay_data=drop_replay_data)
                andisdk_convert(tmpfile, outfile)
        else:
            andisdk_convert(infile, outfile)
    else:
        raise ValueError(f"Unknown output format for {outfile}")


def archivize(infile: AnyPath, formats: List[str], *, tecmp_mapping: Optional[Dict[int, str]] = None) -> None:
    '''
    Args:
        infile (AnyPath): The path to the input network packet capture file.
        formats (List[str]): A list of file formats to convert the input file to.
        tecmp_mapping (Optional[Dict[int, str]]): A dictionary mapping technique IDs to their names, optional.

    Returns:
        None
    '''
    inpath = Path(infile)
    for suffix in formats:
        outfile = inpath.with_suffix(suffix)
        convert(infile, outfile, tecmp_mapping=tecmp_mapping)
    os.remove(infile)
