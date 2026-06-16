# tests/test_uvc_gen.py
import subprocess
import sys
import argparse
from unittest.mock import patch
from uvc_gen import UvcInfo

def test_pytest_runs():
    """Sanity check that pytest infrastructure works."""
    assert True

def test_uvc_info_default_single_mode():
    info = UvcInfo(uvc_name="ahb", version="v1.0")
    assert info.uvc_name == "ahb"
    assert info.version == "v1.0"
    assert info.mode == "single"
    assert info.master_num == 1
    assert info.slave_num == 1

def test_uvc_info_mstslv_mode():
    info = UvcInfo(uvc_name="ahb", version="v1.0", mode="mstslv", master_num=2, slave_num=3)
    assert info.mode == "mstslv"
    assert info.master_num == 2
    assert info.slave_num == 3

def test_uvc_info_no_uvc_num():
    """uvc_num field should be removed (dead code)."""
    info = UvcInfo(uvc_name="ahb")
    assert not hasattr(info, 'uvc_num')

def test_cli_mode_default_single():
    """--mode defaults to 'single'."""
    gen = __import__('uvc_gen').UvcGen()
    with patch('sys.argv', ['uvc_gen', '-n', 'ahb']):
        args = gen.get_input_args()
    assert args.mode == 'single'

def test_cli_mode_mstslv():
    """--mode mstslv is accepted."""
    gen = __import__('uvc_gen').UvcGen()
    with patch('sys.argv', ['uvc_gen', '-n', 'ahb', '-m', 'mstslv']):
        args = gen.get_input_args()
    assert args.mode == 'mstslv'

def test_cli_mst_slv_num_defaults():
    """--mst-num and --slv-num default to 1."""
    gen = __import__('uvc_gen').UvcGen()
    with patch('sys.argv', ['uvc_gen', '-n', 'ahb', '-m', 'mstslv']):
        args = gen.get_input_args()
    assert args.mst_num == 1
    assert args.slv_num == 1

def test_cli_mst_slv_num_custom():
    """--mst-num 2 --slv-num 3 is accepted."""
    gen = __import__('uvc_gen').UvcGen()
    with patch('sys.argv', ['uvc_gen', '-n', 'ahb', '-m', 'mstslv', '--mst-num', '2', '--slv-num', '3']):
        args = gen.get_input_args()
    assert args.mst_num == 2
    assert args.slv_num == 3
