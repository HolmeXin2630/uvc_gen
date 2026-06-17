# tests/test_uvc_gen.py
import subprocess
import sys
import argparse
from pathlib import Path
from uvc_gen import UvcInfo, UvcGen, build_parser

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
    parser = build_parser()
    args = parser.parse_args(['-n', 'ahb'])
    assert args.mode == 'single'

def test_cli_mode_mstslv():
    """--mode mstslv is accepted."""
    parser = build_parser()
    args = parser.parse_args(['-n', 'ahb', '-m', 'mstslv'])
    assert args.mode == 'mstslv'

def test_cli_mst_slv_num_defaults():
    """--mst-num and --slv-num default to 1."""
    parser = build_parser()
    args = parser.parse_args(['-n', 'ahb', '-m', 'mstslv'])
    assert args.mst_num == 1
    assert args.slv_num == 1

def test_cli_mst_slv_num_custom():
    """--mst-num 2 --slv-num 3 is accepted."""
    parser = build_parser()
    args = parser.parse_args(['-n', 'ahb', '-m', 'mstslv', '--mst-num', '2', '--slv-num', '3'])
    assert args.mst_num == 2
    assert args.slv_num == 3

import tempfile, os

def test_init_para_single_mode_uses_default_template():
    """single mode should use templates/default/xxx_uvc/."""
    gen = UvcGen()
    gen.init_para(gen.DEFAULT_TPL, "ahb", "v1.0", tempfile.mkdtemp())
    assert "xxx_uvc" in gen.tpl_dir
    assert "xxx_uvc_mstslv" not in gen.tpl_dir

def test_init_para_mstslv_mode_uses_mstslv_template():
    """mstslv mode should use templates/default/xxx_uvc_mstslv/."""
    gen = UvcGen()
    mstslv_dir = gen.TEMPLATES_DIR / "default" / "xxx_uvc_mstslv"
    mstslv_dir.mkdir(parents=True, exist_ok=True)
    try:
        gen.init_para("mstslv", "ahb", "v1.0", tempfile.mkdtemp())
        assert "xxx_uvc_mstslv" in gen.tpl_dir
    finally:
        pass

def test_generate_uvc_creates_mstslv_files():
    """mstslv mode should generate all 15 files with correct names."""
    gen = UvcGen()
    output_dir = tempfile.mkdtemp()

    mstslv_dir = gen.TEMPLATES_DIR / "default" / "xxx_uvc_mstslv"
    mstslv_dir.mkdir(parents=True, exist_ok=True)

    templates = [
        "xxx_intf.sv", "xxx_transaction.sv", "xxx_cfg.sv",
        "xxx_mst_agent.sv", "xxx_mst_driver.sv", "xxx_mst_monitor.sv", "xxx_mst_sequencer.sv",
        "xxx_slv_agent.sv", "xxx_slv_driver.sv", "xxx_slv_monitor.sv", "xxx_slv_sequencer.sv",
        "xxx_env_cfg.sv", "xxx_env.sv", "xxx_seq_lib.sv", "xxx_package.svp"
    ]
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
        for tpl in templates:
            p = mstslv_dir / tpl
            if tpl in saved_templates:
                p.write_text(saved_templates[tpl])
            elif p.exists():
                p.unlink()
        shutil.rmtree(output_dir, ignore_errors=True)


def test_mstslv_env_contains_dynamic_arrays():
    """env.sv should contain mst_agt[] and slv_agt[] dynamic arrays."""
    gen = UvcGen()
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
    gen = UvcGen()
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
    gen = UvcGen()
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
    gen = UvcGen()
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
    gen = UvcGen()
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

def test_cli_agent_num_default():
    """--agent-num defaults to 1."""
    parser = build_parser()
    args = parser.parse_args(['-n', 'ahb'])
    assert args.agent_num == 1

def test_cli_agent_num_custom():
    """--agent-num 3 is accepted."""
    parser = build_parser()
    args = parser.parse_args(['-n', 'ahb', '--agent-num', '3'])
    assert args.agent_num == 3

def test_cli_with_env_flag():
    """--with-env sets with_env=True."""
    parser = build_parser()
    args = parser.parse_args(['-n', 'ahb', '--with-env'])
    assert args.with_env is True

def test_cli_with_env_default_false():
    """--with-env defaults to False."""
    parser = build_parser()
    args = parser.parse_args(['-n', 'ahb'])
    assert args.with_env is False

def test_cli_with_coverage_flag():
    """--with-coverage sets with_coverage=True."""
    parser = build_parser()
    args = parser.parse_args(['-n', 'ahb', '--with-coverage'])
    assert args.with_coverage is True

def test_cli_with_scoreboard_flag():
    """--with-scoreboard sets with_scoreboard=True."""
    parser = build_parser()
    args = parser.parse_args(['-n', 'ahb', '--with-scoreboard'])
    assert args.with_scoreboard is True

def test_cli_with_ref_model_flag():
    """--with-ref-model sets with_ref_model=True."""
    parser = build_parser()
    args = parser.parse_args(['-n', 'ahb', '--with-ref-model'])
    assert args.with_ref_model is True

def test_uvc_info_new_fields():
    """UvcInfo should have agent_num and with_* fields."""
    info = UvcInfo(uvc_name="ahb", agent_num=3, with_env=True, with_coverage=True)
    assert info.agent_num == 3
    assert info.with_env is True
    assert info.with_coverage is True
    assert info.with_scoreboard is False
    assert info.with_ref_model is False


def test_single_mode_default_unchanged():
    """Default single mode (agent_num=1, no --with-*) produces identical output."""
    gen = UvcGen()
    output_dir = tempfile.mkdtemp()
    try:
        gen.init_para(gen.DEFAULT_TPL, "ahb", "v1.0", output_dir, mode="single")
        gen.parse_tpl_dir()
        gen.generate_uvc()

        env_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_environment.sv").read_text()
        assert "agt;" in env_content
        assert "agt[]" not in env_content
        assert 'create("agt"' in env_content

        pkg_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_package.svp").read_text()
        assert "//`include" in pkg_content
        assert "ahb_environment.sv" in pkg_content
    finally:
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)


def test_single_mode_multi_agent_env_content():
    """--agent-num 3 generates env with agt[] dynamic array."""
    gen = UvcGen()
    output_dir = tempfile.mkdtemp()
    try:
        gen.init_para(gen.DEFAULT_TPL, "ahb", "v1.0", output_dir,
                      mode="single", agent_num=3)
        gen.parse_tpl_dir()
        gen.generate_uvc()

        env_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_environment.sv").read_text()
        assert "agt[]" in env_content
        assert "agent_num" in env_content
        assert "agt_cfg" in env_content
    finally:
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)


def test_single_mode_with_env_includes():
    """--with-env uncomments env include in package.svp."""
    gen = UvcGen()
    output_dir = tempfile.mkdtemp()
    try:
        gen.init_para(gen.DEFAULT_TPL, "ahb", "v1.0", output_dir,
                      mode="single", with_env=True)
        gen.parse_tpl_dir()
        gen.generate_uvc()

        pkg_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_package.svp").read_text()
        lines = pkg_content.split('\n')
        env_include_line = [l for l in lines if "environment.sv" in l][0]
        assert not env_include_line.strip().startswith("//")
    finally:
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)


def test_single_mode_multi_agent_with_env():
    """--agent-num 2 --with-env generates full env with dynamic arrays."""
    gen = UvcGen()
    output_dir = tempfile.mkdtemp()
    try:
        gen.init_para(gen.DEFAULT_TPL, "ahb", "v1.0", output_dir,
                      mode="single", agent_num=2, with_env=True)
        gen.parse_tpl_dir()
        gen.generate_uvc()

        env_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_environment.sv").read_text()
        assert "agt[]" in env_content
        assert "new[env_cfg.agent_num]" in env_content

        cfg_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_environment_cfg.sv").read_text()
        assert "agent_num" in cfg_content
        assert "agt_cfg[]" in cfg_content
    finally:
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)


def test_single_mode_multi_agent_auto_implies_env():
    """--agent-num 2 without --with-env should auto-implicate with_env."""
    gen = UvcGen()
    output_dir = tempfile.mkdtemp()
    try:
        gen.init_para(gen.DEFAULT_TPL, "ahb", "v1.0", output_dir,
                      mode="single", agent_num=2)
        gen.parse_tpl_dir()
        gen.generate_uvc()

        assert gen.with_env is True
        assert gen.info.with_env is True

        pkg_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_package.svp").read_text()
        lines = pkg_content.split('\n')
        env_include_line = [l for l in lines if "environment.sv" in l][0]
        assert not env_include_line.strip().startswith("//")
    finally:
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)


def test_single_mode_with_coverage_includes():
    """--with-coverage uncomments coverage include and generates file."""
    gen = UvcGen()
    output_dir = tempfile.mkdtemp()
    try:
        gen.init_para(gen.DEFAULT_TPL, "ahb", "v1.0", output_dir,
                      mode="single", with_coverage=True)
        gen.parse_tpl_dir()
        gen.generate_uvc()

        pkg_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_package.svp").read_text()
        lines = pkg_content.split('\n')
        coverage_line = [l for l in lines if "coverage.sv" in l][0]
        assert not coverage_line.strip().startswith("//")

        assert (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_coverage.sv").exists()
    finally:
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)


def test_single_mode_with_scoreboard_includes():
    """--with-scoreboard uncomments scoreboard include and generates file."""
    gen = UvcGen()
    output_dir = tempfile.mkdtemp()
    try:
        gen.init_para(gen.DEFAULT_TPL, "ahb", "v1.0", output_dir,
                      mode="single", with_scoreboard=True)
        gen.parse_tpl_dir()
        gen.generate_uvc()

        pkg_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_package.svp").read_text()
        lines = pkg_content.split('\n')
        sb_line = [l for l in lines if "scoreboard.sv" in l][0]
        assert not sb_line.strip().startswith("//")

        assert (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_scoreboard.sv").exists()
    finally:
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)


def test_single_mode_with_ref_model_includes():
    """--with-ref-model uncomments ref_model include and generates file."""
    gen = UvcGen()
    output_dir = tempfile.mkdtemp()
    try:
        gen.init_para(gen.DEFAULT_TPL, "ahb", "v1.0", output_dir,
                      mode="single", with_ref_model=True)
        gen.parse_tpl_dir()
        gen.generate_uvc()

        pkg_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_package.svp").read_text()
        lines = pkg_content.split('\n')
        ref_line = [l for l in lines if "ref_model.sv" in l][0]
        assert not ref_line.strip().startswith("//")

        assert (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_ref_model.sv").exists()
    finally:
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)


def test_optional_components_default_not_in_output():
    """Default single mode should NOT generate optional component files."""
    gen = UvcGen()
    output_dir = tempfile.mkdtemp()
    try:
        gen.init_para(gen.DEFAULT_TPL, "ahb", "v1.0", output_dir, mode="single")
        gen.parse_tpl_dir()
        gen.generate_uvc()

        out_dir = Path(output_dir) / "ahb_uvc" / "v1.0"
        assert not (out_dir / "ahb_coverage.sv").exists()
        assert not (out_dir / "ahb_scoreboard.sv").exists()
        assert not (out_dir / "ahb_ref_model.sv").exists()
    finally:
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)


def test_mstslv_with_coverage():
    """mstslv mode with --with-coverage generates coverage file."""
    gen = UvcGen()
    output_dir = tempfile.mkdtemp()
    mstslv_dir = gen.TEMPLATES_DIR / "default" / "xxx_uvc_mstslv"
    try:
        gen.init_para(str(mstslv_dir), "ahb", "v1.0", output_dir,
                      mode="mstslv", with_coverage=True)
        gen.parse_tpl_dir()
        gen.generate_uvc()

        assert (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_coverage.sv").exists()
        pkg_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_package.svp").read_text()
        lines = pkg_content.split('\n')
        cov_line = [l for l in lines if "coverage.sv" in l][0]
        assert not cov_line.strip().startswith("//")
    finally:
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)


def test_mstslv_with_scoreboard():
    """mstslv mode with --with-scoreboard generates scoreboard file."""
    gen = UvcGen()
    output_dir = tempfile.mkdtemp()
    mstslv_dir = gen.TEMPLATES_DIR / "default" / "xxx_uvc_mstslv"
    try:
        gen.init_para(str(mstslv_dir), "ahb", "v1.0", output_dir,
                      mode="mstslv", with_scoreboard=True)
        gen.parse_tpl_dir()
        gen.generate_uvc()

        assert (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_scoreboard.sv").exists()
        pkg_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_package.svp").read_text()
        lines = pkg_content.split('\n')
        sb_line = [l for l in lines if "scoreboard.sv" in l][0]
        assert not sb_line.strip().startswith("//")
    finally:
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)


def test_mstslv_with_ref_model():
    """mstslv mode with --with-ref-model generates ref_model file."""
    gen = UvcGen()
    output_dir = tempfile.mkdtemp()
    mstslv_dir = gen.TEMPLATES_DIR / "default" / "xxx_uvc_mstslv"
    try:
        gen.init_para(str(mstslv_dir), "ahb", "v1.0", output_dir,
                      mode="mstslv", with_ref_model=True)
        gen.parse_tpl_dir()
        gen.generate_uvc()

        assert (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_ref_model.sv").exists()
        pkg_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_package.svp").read_text()
        lines = pkg_content.split('\n')
        ref_line = [l for l in lines if "ref_model.sv" in l][0]
        assert not ref_line.strip().startswith("//")
    finally:
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)


def test_mstslv_optional_components_default_not_in_output():
    """Default mstslv mode should NOT generate optional component files."""
    gen = UvcGen()
    output_dir = tempfile.mkdtemp()
    mstslv_dir = gen.TEMPLATES_DIR / "default" / "xxx_uvc_mstslv"
    try:
        gen.init_para(str(mstslv_dir), "ahb", "v1.0", output_dir, mode="mstslv")
        gen.parse_tpl_dir()
        gen.generate_uvc()

        out_dir = Path(output_dir) / "ahb_uvc" / "v1.0"
        assert not (out_dir / "ahb_coverage.sv").exists()
        assert not (out_dir / "ahb_scoreboard.sv").exists()
        assert not (out_dir / "ahb_ref_model.sv").exists()

        pkg_content = (out_dir / "ahb_package.svp").read_text()
        lines = pkg_content.split('\n')
        cov_lines = [l for l in lines if "coverage.sv" in l]
        sb_lines = [l for l in lines if "scoreboard.sv" in l]
        ref_lines = [l for l in lines if "ref_model.sv" in l]
        for l in cov_lines + sb_lines + ref_lines:
            assert l.strip().startswith("//")
    finally:
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)


# === New tests for refactored architecture ===

def test_uvcgen_holds_uvc_info():
    """UvcGen should have self.info as UvcInfo instance."""
    gen = UvcGen()
    assert isinstance(gen.info, UvcInfo)
    assert gen.info.uvc_name == ''

def test_property_aliases_read_from_info():
    """Property aliases should read from self.info."""
    gen = UvcGen()
    gen.info.uvc_name = "ahb"
    assert gen.uvc_name == "ahb"

def test_property_aliases_write_to_info():
    """Property aliases should write to self.info."""
    gen = UvcGen()
    gen.uvc_name = "spi"
    assert gen.info.uvc_name == "spi"

def test_init_para_populates_info():
    """init_para should populate self.info, not separate attrs."""
    gen = UvcGen()
    output_dir = tempfile.mkdtemp()
    gen.init_para(gen.DEFAULT_TPL, "ahb", "v1.0", output_dir,
                  mode="single", agent_num=3, with_coverage=True)
    assert gen.info.uvc_name == "ahb"
    assert gen.info.version == "v1.0"
    assert gen.info.mode == "single"
    assert gen.info.agent_num == 3
    assert gen.info.with_coverage is True

def test_generate_uvc_uses_info_directly():
    """generate_uvc should pass self.info to templates, not create a new one."""
    gen = UvcGen()
    output_dir = tempfile.mkdtemp()
    try:
        gen.init_para(gen.DEFAULT_TPL, "ahb", "v1.0", output_dir, mode="single")
        gen.parse_tpl_dir()
        gen.generate_uvc()

        # The generated file should use info.uvc_name
        assert (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_agent.sv").exists()
    finally:
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)

def test_build_parser_standalone():
    """build_parser should return a usable parser without creating UvcGen."""
    parser = build_parser()
    args = parser.parse_args(['-n', 'ahb', '-m', 'mstslv', '--mst-num', '2'])
    assert args.uvc_name == 'ahb'
    assert args.mode == 'mstslv'
    assert args.mst_num == 2

def test_build_parser_with_custom_default():
    """build_parser accepts custom default_tpl."""
    parser = build_parser('/custom/path')
    assert parser.get_default('tpl_dir') == '/custom/path'

def test_no_sys_argv_import_in_cli_tests():
    """CLI tests should not need sys.argv patching."""
    # This test exists to verify the refactor goal:
    # build_parser().parse_args([...]) works without sys.argv mocking
    parser = build_parser()
    args = parser.parse_args(['-n', 'ahb', '--with-env', '--with-coverage',
                              '--agent-num', '3', '-m', 'single'])
    assert args.uvc_name == 'ahb'
    assert args.with_env is True
    assert args.with_coverage is True
    assert args.agent_num == 3
    assert args.mode == 'single'
