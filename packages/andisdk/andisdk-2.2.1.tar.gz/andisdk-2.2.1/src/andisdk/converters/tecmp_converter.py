import sys 
from contextlib import contextmanager
import json
import os
from os import fspath
from platform import system
import stat
from subprocess import check_call
from typing import Optional,Dict
from .utils import AnyPath, temp_path
from os.path import join, exists

@contextmanager
def make_map_file(tecmp_mapping: Optional[Dict[int, str]]):
    tecmp_mapping = tecmp_mapping or dict()
    with temp_path(suffix=".json") as tmpfile:
        mappings = list()
        for (chl_id, inf_name) in tecmp_mapping.items():
            mappings.append(dict(
                when=dict(chl_id=chl_id),
                change=dict(inf_name=inf_name)
            ))
        with open(tmpfile, 'w', encoding='utf-8') as f:
            data = dict(version=1, mappings=mappings)
            json.dump(data, f, indent=4)

        yield tmpfile

def _resolve_executable_path():
    """Helper function to find the correct executable path."""

    executable_name = 'tecmp_converter'
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    alternative_path = join(pkg_dir, '..', 'dlls', 'lib', 'site-packages', 'andi', 'converters', 'binConverter')
    system_name = system().lower()
    executable_path = join(pkg_dir, 'binConverter', system_name, executable_name)

    if system_name == 'windows':
        executable_path += ".exe"

    if not exists(executable_path):
        executable_path = join(alternative_path, system_name, executable_name)

    if system_name == 'linux':
        st = os.stat(executable_path)
        os.chmod(executable_path, st.st_mode | stat.S_IEXEC)
    return executable_path

def tecmp_convert(infile: AnyPath, outfile: AnyPath, *, tecmp_mapping: Optional[Dict[int, str]] = None, drop_replay_data: Optional[bool] = False) -> None:
    """
    Remove TECMP packets from infile and write the result to outfile.
    """
    bin_file = _resolve_executable_path()

    try:
        with make_map_file(tecmp_mapping) as map_file:
            cmd = [
                bin_file, 
                "--tecmp-only", 
                "--channel-map", 
                map_file, infile, 
                outfile
            ]
            if drop_replay_data:
                cmd.append("--drop-replay-data")
            check_call(cmd)
    except Exception as e:
        print("An error occurred: {}".format(e))
        raise