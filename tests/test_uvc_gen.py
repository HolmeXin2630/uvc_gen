# tests/test_uvc_gen.py
import subprocess
import sys
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
