# tests/test_uvc_gen.py
import subprocess
import sys
import argparse
from pathlib import Path
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

import tempfile, os

def test_init_para_single_mode_uses_default_template():
    """single mode should use templates/default/xxx_uvc/."""
    gen = __import__('uvc_gen').UvcGen()
    gen.init_para(gen.DEFAULT_TPL, "ahb", "v1.0", tempfile.mkdtemp())
    assert "xxx_uvc" in gen.tpl_dir
    assert "xxx_uvc_mstslv" not in gen.tpl_dir

def test_init_para_mstslv_mode_uses_mstslv_template():
    """mstslv mode should use templates/default/xxx_uvc_mstslv/."""
    gen = __import__('uvc_gen').UvcGen()
    # First create the mstslv template dir so it exists
    mstslv_dir = gen.TEMPLATES_DIR / "default" / "xxx_uvc_mstslv"
    mstslv_dir.mkdir(parents=True, exist_ok=True)
    try:
        gen.init_para("mstslv", "ahb", "v1.0", tempfile.mkdtemp())
        assert "xxx_uvc_mstslv" in gen.tpl_dir
    finally:
        pass

def test_generate_uvc_creates_mstslv_files():
    """mstslv mode should generate all 15 files with correct names."""
    gen = __import__('uvc_gen').UvcGen()
    output_dir = tempfile.mkdtemp()

    # Create the mstslv template dir with placeholder files
    mstslv_dir = gen.TEMPLATES_DIR / "default" / "xxx_uvc_mstslv"
    mstslv_dir.mkdir(parents=True, exist_ok=True)

    # Create minimal template files
    templates = [
        "xxx_intf.sv", "xxx_transaction.sv", "xxx_cfg.sv",
        "xxx_mst_agent.sv", "xxx_mst_driver.sv", "xxx_mst_monitor.sv", "xxx_mst_sequencer.sv",
        "xxx_slv_agent.sv", "xxx_slv_driver.sv", "xxx_slv_monitor.sv", "xxx_slv_sequencer.sv",
        "xxx_env_cfg.sv", "xxx_env.sv", "xxx_seq_lib.sv", "xxx_package.svp"
    ]
    # Save existing template files so we can restore them after the test
    saved_templates = {}
    for tpl in templates:
        p = mstslv_dir / tpl
        if p.exists():
            saved_templates[tpl] = p.read_text()
    try:
        for tpl in templates:
            (mstslv_dir / tpl).write_text(f"// {tpl}\n")

        gen.init_para(str(mstslv_dir), "ahb", "v1.0", output_dir, mode="mstslv", master_num=2, slave_num=1)
        gen.parse_tpl_dir()
        gen.generate_uvc()

        out_uvc = Path(output_dir) / "ahb_uvc" / "v1.0"
        assert out_uvc.exists()

        # Check all expected files exist with correct names
        expected_files = [
            "ahb_intf.sv", "ahb_transaction.sv", "ahb_cfg.sv",
            "ahb_mst_agent.sv", "ahb_mst_driver.sv", "ahb_mst_monitor.sv", "ahb_mst_sequencer.sv",
            "ahb_slv_agent.sv", "ahb_slv_driver.sv", "ahb_slv_monitor.sv", "ahb_slv_sequencer.sv",
            "ahb_env_cfg.sv", "ahb_env.sv", "ahb_seq_lib.sv", "ahb_package.svp"
        ]
        for f in expected_files:
            assert (out_uvc / f).exists(), f"Missing: {f}"
    finally:
        import shutil
        # Restore original template files
        for tpl in templates:
            p = mstslv_dir / tpl
            if tpl in saved_templates:
                p.write_text(saved_templates[tpl])
            elif p.exists():
                p.unlink()
        shutil.rmtree(output_dir, ignore_errors=True)


def test_mstslv_env_contains_dynamic_arrays():
    """env.sv should contain mst_agt[] and slv_agt[] dynamic arrays."""
    gen = __import__('uvc_gen').UvcGen()
    output_dir = tempfile.mkdtemp()
    mstslv_dir = gen.TEMPLATES_DIR / "default" / "xxx_uvc_mstslv"
    gen.init_para(str(mstslv_dir), "ahb", "v1.0", output_dir, mode="mstslv", master_num=2, slave_num=3)
    gen.parse_tpl_dir()
    gen.generate_uvc()

    env_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_env.sv").read_text()
    assert "mst_agt[]" in env_content
    assert "slv_agt[]" in env_content
    assert "ahb_mst_agent" in env_content
    assert "ahb_slv_agent" in env_content

def test_mstslv_env_cfg_contains_nums():
    """env_cfg.sv should contain master_num and slave_num."""
    gen = __import__('uvc_gen').UvcGen()
    output_dir = tempfile.mkdtemp()
    mstslv_dir = gen.TEMPLATES_DIR / "default" / "xxx_uvc_mstslv"
    gen.init_para(str(mstslv_dir), "ahb", "v1.0", output_dir, mode="mstslv", master_num=2, slave_num=3)
    gen.parse_tpl_dir()
    gen.generate_uvc()

    cfg_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_env_cfg.sv").read_text()
    assert "master_num" in cfg_content
    assert "slave_num" in cfg_content
    assert "mst_cfg[]" in cfg_content
    assert "slv_cfg[]" in cfg_content

def test_mstslv_intf_has_four_clocking_blocks():
    """intf.sv should have 4 clocking blocks: cb_mst_drv, cb_mst_mon, cb_slv_drv, cb_slv_mon."""
    gen = __import__('uvc_gen').UvcGen()
    output_dir = tempfile.mkdtemp()
    mstslv_dir = gen.TEMPLATES_DIR / "default" / "xxx_uvc_mstslv"
    gen.init_para(str(mstslv_dir), "ahb", "v1.0", output_dir, mode="mstslv")
    gen.parse_tpl_dir()
    gen.generate_uvc()

    intf_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_intf.sv").read_text()
    assert "clocking cb_mst_drv" in intf_content
    assert "clocking cb_mst_mon" in intf_content
    assert "clocking cb_slv_drv" in intf_content
    assert "clocking cb_slv_mon" in intf_content

def test_mstslv_driver_uses_correct_clocking_block():
    """mst_driver should use cb_mst_drv, slv_driver should use cb_slv_drv."""
    gen = __import__('uvc_gen').UvcGen()
    output_dir = tempfile.mkdtemp()
    mstslv_dir = gen.TEMPLATES_DIR / "default" / "xxx_uvc_mstslv"
    gen.init_para(str(mstslv_dir), "ahb", "v1.0", output_dir, mode="mstslv")
    gen.parse_tpl_dir()
    gen.generate_uvc()

    mst_drv = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_mst_driver.sv").read_text()
    slv_drv = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_slv_driver.sv").read_text()
    assert "cb_mst_drv" in mst_drv
    assert "cb_slv_drv" in slv_drv
    assert "cb_slv_drv" not in mst_drv
    assert "cb_mst_drv" not in slv_drv

def test_single_mode_still_works():
    """single mode should still generate the original 10 files."""
    gen = __import__('uvc_gen').UvcGen()
    output_dir = tempfile.mkdtemp()
    gen.init_para(gen.DEFAULT_TPL, "spi", "v1.0", output_dir, mode="single")
    gen.parse_tpl_dir()
    gen.generate_uvc()

    out_uvc = Path(output_dir) / "spi_uvc" / "v1.0"
    expected = [
        "spi_agent.sv", "spi_config.sv", "spi_driver.sv",
        "spi_environment.sv", "spi_intf.sv", "spi_monitor.sv",
        "spi_package.svp", "spi_seq_lib.sv", "spi_sequencer.sv", "spi_transaction.sv"
    ]
    for f in expected:
        assert (out_uvc / f).exists(), f"Missing: {f}"
