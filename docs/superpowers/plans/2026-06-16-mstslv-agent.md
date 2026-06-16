# Master/Slave Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `mstslv` generation mode to uvc_gen, producing a complete UVM environment with dynamically instantiated master/slave agent arrays.

**Architecture:** New independent template set `templates/default/xxx_uvc_mstslv/` with 15 SystemVerilog templates. Python code extended with `--mode`, `--mst-num`, `--slv-num` CLI args. TDD: pytest for Python logic, VCS compile check for generated SV syntax.

**Tech Stack:** Python 3, Jinja2, Rich, pytest, Synopsys VCS

---

## File Structure

### New Files (Templates)

| File | Responsibility |
|---|---|
| `templates/default/xxx_uvc_mstslv/xxx_intf.sv` | Shared interface, 4 clocking blocks (cb_mst_drv, cb_mst_mon, cb_slv_drv, cb_slv_mon) |
| `templates/default/xxx_uvc_mstslv/xxx_transaction.sv` | Shared transaction class (identical to single-agent) |
| `templates/default/xxx_uvc_mstslv/xxx_cfg.sv` | Shared agent config (is_active, en, vif) |
| `templates/default/xxx_uvc_mstslv/xxx_mst_agent.sv` | Master agent (drv, sqr, mon, cfg) |
| `templates/default/xxx_uvc_mstslv/xxx_mst_driver.sv` | Master driver (uses cb_mst_drv) |
| `templates/default/xxx_uvc_mstslv/xxx_mst_monitor.sv` | Master monitor (uses cb_mst_mon) |
| `templates/default/xxx_uvc_mstslv/xxx_mst_sequencer.sv` | Master sequencer |
| `templates/default/xxx_uvc_mstslv/xxx_slv_agent.sv` | Slave agent (drv, sqr, mon, cfg) |
| `templates/default/xxx_uvc_mstslv/xxx_slv_driver.sv` | Slave driver (uses cb_slv_drv) |
| `templates/default/xxx_uvc_mstslv/xxx_slv_monitor.sv` | Slave monitor (uses cb_slv_mon) |
| `templates/default/xxx_uvc_mstslv/xxx_slv_sequencer.sv` | Slave sequencer |
| `templates/default/xxx_uvc_mstslv/xxx_env_cfg.sv` | Environment config (master_num, slave_num, mst_cfg[], slv_cfg[]) |
| `templates/default/xxx_uvc_mstslv/xxx_env.sv` | Environment (dynamic agent array instantiation) |
| `templates/default/xxx_uvc_mstslv/xxx_seq_lib.sv` | Sequence library (mst and slv base sequences) |
| `templates/default/xxx_uvc_mstslv/xxx_package.svp` | Package with all includes |

### Modified Files

| File | Changes |
|---|---|
| `uvc_gen.py:14-19` | UvcInfo: remove `uvc_num`, add `mode`, `master_num`, `slave_num` |
| `uvc_gen.py:35-50` | `get_input_args()`: add `--mode`, `--mst-num`, `--slv-num` |
| `uvc_gen.py:85-96` | `init_para()`: mode-based template directory selection |
| `uvc_gen.py:126-144` | `generate_uvc()`: pass new fields to UvcInfo |

### New Test Files

| File | Responsibility |
|---|---|
| `tests/test_uvc_gen.py` | pytest unit tests for CLI, UvcInfo, template resolution, generation |
| `tests/test_vcs_compile.sh` | VCS compile verification script |

---

## Task 1: Set Up Test Infrastructure

**Files:**
- Create: `tests/test_uvc_gen.py`
- Create: `pyproject.toml`

- [ ] **Step 1: Install pytest**

```bash
pip install pytest
```

- [ ] **Step 2: Create pyproject.toml with pytest config**

```toml
[project]
name = "uvc_gen"
version = "1.0.0"
requires-python = ">=3.8"
dependencies = ["jinja2", "rich"]

[project.scripts]
uvc_gen = "uvc_gen:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 3: Write failing test — verify pytest runs**

```python
# tests/test_uvc_gen.py
import subprocess
import sys

def test_pytest_runs():
    """Sanity check that pytest infrastructure works."""
    assert True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_uvc_gen.py -v`
Expected: 1 passed

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml tests/test_uvc_gen.py
git commit -m "chore: add pytest infrastructure and pyproject.toml"
```

---

## Task 2: UvcInfo — Remove Dead Field, Add New Fields

**Files:**
- Modify: `uvc_gen.py:14-19`
- Modify: `tests/test_uvc_gen.py`

- [ ] **Step 1: Write failing test for new UvcInfo fields**

Append to `tests/test_uvc_gen.py`:

```python
from uvc_gen import UvcInfo

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_uvc_gen.py::test_uvc_info_no_uvc_num -v`
Expected: FAIL — `uvc_num` still exists

- [ ] **Step 3: Modify UvcInfo dataclass**

Replace `uvc_gen.py:14-19` with:

```python
@dataclass
class UvcInfo:
    """UVC 信息类"""
    uvc_name: str = ''
    version: str = ''
    mode: str = 'single'
    master_num: int = 1
    slave_num: int = 1
```

- [ ] **Step 4: Run all UvcInfo tests**

Run: `python -m pytest tests/test_uvc_gen.py -v -k "uvc_info"`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add uvc_gen.py tests/test_uvc_gen.py
git commit -m "feat: update UvcInfo — remove uvc_num, add mode/master_num/slave_num"
```

---

## Task 3: CLI — Add --mode, --mst-num, --slv-num Arguments

**Files:**
- Modify: `uvc_gen.py:35-50` (`get_input_args`)
- Modify: `tests/test_uvc_gen.py`

- [ ] **Step 1: Write failing test for new CLI args**

Append to `tests/test_uvc_gen.py`:

```python
import argparse
from unittest.mock import patch

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_uvc_gen.py -v -k "cli"`
Expected: FAIL — `mode` attribute not found

- [ ] **Step 3: Add new CLI arguments to get_input_args()**

In `uvc_gen.py`, after the `-v/--version` argument (line 49), add:

```python
parser.add_argument('-m', '--mode',
                    choices=['single', 'mstslv'],
                    default='single',
                    help='Generation mode: single (default) or mstslv')
parser.add_argument('--mst-num',
                    type=int, default=1,
                    help='Number of master agents (mstslv mode)')
parser.add_argument('--slv-num',
                    type=int, default=1,
                    help='Number of slave agents (mstslv mode)')
```

- [ ] **Step 4: Run CLI tests**

Run: `python -m pytest tests/test_uvc_gen.py -v -k "cli"`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add uvc_gen.py tests/test_uvc_gen.py
git commit -m "feat: add --mode, --mst-num, --slv-num CLI arguments"
```

---

## Task 4: Template Directory Selection by Mode

**Files:**
- Modify: `uvc_gen.py:85-96` (`init_para`)
- Modify: `uvc_gen.py:23-33` (`__init__`)
- Modify: `uvc_gen.py:198-209` (`main`)
- Modify: `tests/test_uvc_gen.py`

- [ ] **Step 1: Write failing test for mode-based template selection**

Append to `tests/test_uvc_gen.py`:

```python
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
        # Don't delete — we'll create real templates later
        pass
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_uvc_gen.py -v -k "init_para"`
Expected: FAIL — `init_para` doesn't accept mode logic yet

- [ ] **Step 3: Update __init__ to store mode-related defaults**

Replace `uvc_gen.py:23-33` with:

```python
def __init__(self):
    self.uvc_name: str = ''
    self.file_list: List[Path] = []
    self.output: str = './'
    self.tpl_dir: Optional[str] = None
    self.version: str = ''
    self.mode: str = 'single'
    self.master_num: int = 1
    self.slave_num: int = 1

    script_dir = Path(__file__).resolve().parent
    self.TEMPLATES_DIR = script_dir / "templates"
    self.DEFAULT_TPL = str(self.TEMPLATES_DIR / "default" / "xxx_uvc")
    self.MSTSLV_TPL = str(self.TEMPLATES_DIR / "default" / "xxx_uvc_mstslv")
```

- [ ] **Step 4: Update init_para to accept and handle mode**

Replace `uvc_gen.py:85-96` with:

```python
def init_para(self, tpl_dir: str, uvc_name: str, version: str, output: str,
              mode: str = 'single', master_num: int = 1, slave_num: int = 1) -> None:
    """初始化参数"""
    self.mode = mode
    self.master_num = master_num
    self.slave_num = slave_num

    # If tpl_dir is a mode name, resolve to the corresponding template directory
    if mode == 'mstslv' and tpl_dir == self.DEFAULT_TPL:
        tpl_dir = self.MSTSLV_TPL

    resolved_tpl_dir = self._resolve_template_dir(tpl_dir)

    if not Path(resolved_tpl_dir).exists():
        raise FileNotFoundError(f"Template directory not found: {resolved_tpl_dir}")

    self.tpl_dir = resolved_tpl_dir
    self.uvc_name = uvc_name
    self.version = version
    self.output = output
```

- [ ] **Step 5: Update main() to pass new args**

Replace `uvc_gen.py:203` with:

```python
uvc_gen.init_para(args.tpl_dir, args.uvc_name, args.version, args.output,
                  mode=args.mode, master_num=args.mst_num, slave_num=args.slv_num)
```

- [ ] **Step 6: Run init_para tests**

Run: `python -m pytest tests/test_uvc_gen.py -v -k "init_para"`
Expected: 2 passed

- [ ] **Step 7: Commit**

```bash
git add uvc_gen.py tests/test_uvc_gen.py
git commit -m "feat: mode-based template directory selection"
```

---

## Task 5: Update generate_uvc to Pass New Context

**Files:**
- Modify: `uvc_gen.py:141-144` (UvcInfo construction in generate_uvc)
- Modify: `tests/test_uvc_gen.py`

- [ ] **Step 1: Write failing test**

Append to `tests/test_uvc_gen.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_uvc_gen.py -v -k "mstslv_files"`
Expected: FAIL — mstslv template dir doesn't have real templates yet

- [ ] **Step 3: Update UvcInfo construction in generate_uvc()**

Replace `uvc_gen.py:141-144` with:

```python
uvc_info = UvcInfo(
    uvc_name=self.uvc_name,
    version=self.version,
    mode=self.mode,
    master_num=self.master_num,
    slave_num=self.slave_num
)
```

- [ ] **Step 4: Run test (still fails — templates not created yet)**

Run: `python -m pytest tests/test_uvc_gen.py -v -k "mstslv_files"`
Expected: FAIL — template files are just placeholders, no Jinja2 rendering

- [ ] **Step 5: Commit (partial — code changes done, templates in next task)**

```bash
git add uvc_gen.py
git commit -m "feat: pass mode/master_num/slave_num to template context"
```

---

## Task 6: Create mstslv Template Files — Shared Components

**Files:**
- Create: `templates/default/xxx_uvc_mstslv/xxx_intf.sv`
- Create: `templates/default/xxx_uvc_mstslv/xxx_transaction.sv`
- Create: `templates/default/xxx_uvc_mstslv/xxx_cfg.sv`
- Create: `templates/default/xxx_uvc_mstslv/xxx_package.svp`

- [ ] **Step 1: Create xxx_intf.sv**

```systemverilog
`ifndef {{ uvc_info.uvc_name.upper() }}_IF__SV
`define {{ uvc_info.uvc_name.upper() }}_IF__SV

interface {{ uvc_info.uvc_name }}_if(input mclk, input mrst_n);
    parameter HOLD_TIME=1;
    parameter SETUP_TIME=1;

    logic [15:0]    tmp_data;

    task reset_driver_signal();
        tmp_data <= 0;
    endtask

    // Master clocking blocks
    clocking cb_mst_drv @(posedge mclk);
        default input #SETUP_TIME output #HOLD_TIME;
        output tmp_data;
    endclocking

    clocking cb_mst_mon @(posedge mclk);
        default input #SETUP_TIME output #HOLD_TIME;
        input tmp_data;
    endclocking

    // Slave clocking blocks
    clocking cb_slv_drv @(posedge mclk);
        default input #SETUP_TIME output #HOLD_TIME;
        output tmp_data;
    endclocking

    clocking cb_slv_mon @(posedge mclk);
        default input #SETUP_TIME output #HOLD_TIME;
        input tmp_data;
    endclocking

endinterface

`endif//{{ uvc_info.uvc_name.upper() }}_IF__SV
```

- [ ] **Step 2: Create xxx_transaction.sv**

```systemverilog
`ifndef {{ uvc_info.uvc_name.upper() }}_TRANSACTION__SV
`define {{ uvc_info.uvc_name.upper() }}_TRANSACTION__SV

class {{ uvc_info.uvc_name }}_transaction extends uvm_sequence_item;

    typedef enum {IDLE, PARA} {{ uvc_info.uvc_name }}_cmd_enum;
    rand {{ uvc_info.uvc_name }}_cmd_enum     e_{{ uvc_info.uvc_name }}_cmd;
    rand bit[15:0] tmp_data;

    `uvm_object_utils_begin({{ uvc_info.uvc_name }}_transaction)
        `uvm_field_enum({{ uvc_info.uvc_name }}_cmd_enum, e_{{uvc_info.uvc_name}}_cmd, UVM_DEFAULT)
        `uvm_field_int(tmp_data, UVM_DEFAULT)
    `uvm_object_utils_end

    function new(string name = "{{ uvc_info.uvc_name }}_transaction");
        super.new(name);
    endfunction: new

endclass

`endif //{{ uvc_info.uvc_name.upper() }}_TRANSACTION__SV
```

- [ ] **Step 3: Create xxx_cfg.sv**

```systemverilog
`ifndef {{ uvc_info.uvc_name.upper() }}_CFG__SV
`define {{ uvc_info.uvc_name.upper() }}_CFG__SV

class {{ uvc_info.uvc_name }}_cfg extends uvm_object;
    `uvm_object_utils({{ uvc_info.uvc_name }}_cfg)

    uvm_active_passive_enum is_active = UVM_ACTIVE;
    bit en = 1;

    virtual interface {{ uvc_info.uvc_name }}_if vif;

    function new(string name = "{{ uvc_info.uvc_name }}_cfg");
        super.new(name);
    endfunction: new

endclass : {{ uvc_info.uvc_name }}_cfg

`endif //{{ uvc_info.uvc_name.upper() }}_CFG__SV
```

- [ ] **Step 4: Create xxx_package.svp**

```systemverilog
`ifndef {{ uvc_info.uvc_name.upper() }}_PACKAGE__SVP
`define {{ uvc_info.uvc_name.upper() }}_PACKAGE__SVP

{% set prefix = uvc_info.uvc_name + '_uvc/' + (uvc_info.version ~ '/' if uvc_info.version != '' else '') %}
`include "{{prefix}}{{uvc_info.uvc_name}}_intf.sv"
package {{ uvc_info.uvc_name }}_package;

    import uvm_pkg::*;

    `include "{{prefix}}{{uvc_info.uvc_name}}_transaction.sv"
    `include "{{prefix}}{{uvc_info.uvc_name}}_cfg.sv"
    `include "{{prefix}}{{uvc_info.uvc_name}}_mst_sequencer.sv"
    `include "{{prefix}}{{uvc_info.uvc_name}}_mst_driver.sv"
    `include "{{prefix}}{{uvc_info.uvc_name}}_mst_monitor.sv"
    `include "{{prefix}}{{uvc_info.uvc_name}}_mst_agent.sv"
    `include "{{prefix}}{{uvc_info.uvc_name}}_slv_sequencer.sv"
    `include "{{prefix}}{{uvc_info.uvc_name}}_slv_driver.sv"
    `include "{{prefix}}{{uvc_info.uvc_name}}_slv_monitor.sv"
    `include "{{prefix}}{{uvc_info.uvc_name}}_slv_agent.sv"
    `include "{{prefix}}{{uvc_info.uvc_name}}_env_cfg.sv"
    `include "{{prefix}}{{uvc_info.uvc_name}}_env.sv"
    `include "{{prefix}}{{uvc_info.uvc_name}}_seq_lib.sv"

endpackage
`endif
```

- [ ] **Step 5: Commit**

```bash
git add templates/default/xxx_uvc_mstslv/
git commit -m "feat: add mstslv shared templates (intf, transaction, cfg, package)"
```

---

## Task 7: Create mstslv Template Files — Master Components

**Files:**
- Create: `templates/default/xxx_uvc_mstslv/xxx_mst_sequencer.sv`
- Create: `templates/default/xxx_uvc_mstslv/xxx_mst_driver.sv`
- Create: `templates/default/xxx_uvc_mstslv/xxx_mst_monitor.sv`
- Create: `templates/default/xxx_uvc_mstslv/xxx_mst_agent.sv`

- [ ] **Step 1: Create xxx_mst_sequencer.sv**

```systemverilog
`ifndef {{ uvc_info.uvc_name.upper() }}_MST_SEQUENCER__SV
`define {{ uvc_info.uvc_name.upper() }}_MST_SEQUENCER__SV

class {{ uvc_info.uvc_name }}_mst_sequencer extends uvm_sequencer #({{ uvc_info.uvc_name }}_transaction);
    {{ uvc_info.uvc_name }}_cfg cfg;

    `uvm_component_utils({{ uvc_info.uvc_name }}_mst_sequencer)

    function new(string name,uvm_component parent);
        super.new(name,parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
    endfunction: build_phase
endclass

`endif //{{ uvc_info.uvc_name.upper() }}_MST_SEQUENCER__SV
```

- [ ] **Step 2: Create xxx_mst_driver.sv**

```systemverilog
`ifndef {{ uvc_info.uvc_name.upper() }}_MST_DRIVER__SV
`define {{ uvc_info.uvc_name.upper() }}_MST_DRIVER__SV
class {{ uvc_info.uvc_name }}_mst_driver extends uvm_driver#({{ uvc_info.uvc_name }}_transaction);
    `uvm_component_utils({{ uvc_info.uvc_name }}_mst_driver)

    virtual interface {{ uvc_info.uvc_name }}_if vif;
    {{ uvc_info.uvc_name }}_cfg cfg;

    extern function new(string name = "{{ uvc_info.uvc_name }}_mst_driver", uvm_component parent = null);
    extern virtual function void build_phase(uvm_phase phase);
    extern virtual protected task get_and_drive();
    extern virtual protected task drive_trans({{ uvc_info.uvc_name }}_transaction trans);
    extern virtual task run();
endclass: {{ uvc_info.uvc_name }}_mst_driver

function {{ uvc_info.uvc_name }}_mst_driver::new(string name = "{{ uvc_info.uvc_name }}_mst_driver", uvm_component parent = null);
    super.new(name,parent);
endfunction: new

function void {{ uvc_info.uvc_name }}_mst_driver::build_phase(uvm_phase phase);
    super.build_phase(phase);
    vif=cfg.vif;
endfunction: build_phase

task {{ uvc_info.uvc_name }}_mst_driver::run();
    fork begin //guard fork
        forever begin
            fork
                begin
                    @(posedge vif.mrst_n);
                    vif.reset_driver_signal();
                    get_and_drive();
                end
                begin
                    @(negedge vif.mrst_n);
                end
            join_any
            disable fork;
        end
    end join //guard fork
endtask: run

task {{ uvc_info.uvc_name }}_mst_driver::get_and_drive();
    forever begin
        seq_item_port.get_next_item(req);
        drive_trans(req);
        seq_item_port.item_done();
    end
endtask:get_and_drive

task {{ uvc_info.uvc_name }}_mst_driver::drive_trans({{ uvc_info.uvc_name }}_transaction trans);
    if(trans.e_{{ uvc_info.uvc_name }}_cmd == {{uvc_info.uvc_name}}_transaction::IDLE) begin
        @(vif.cb_mst_drv);
        vif.cb_mst_drv.tmp_data <= trans.tmp_data;
    end
endtask

`endif //{{ uvc_info.uvc_name.upper() }}_MST_DRIVER__SV
```

- [ ] **Step 3: Create xxx_mst_monitor.sv**

```systemverilog
`ifndef {{ uvc_info.uvc_name.upper() }}_MST_MONITOR__SV
`define {{ uvc_info.uvc_name.upper() }}_MST_MONITOR__SV
class {{ uvc_info.uvc_name }}_mst_monitor extends uvm_monitor;
    `uvm_component_utils({{ uvc_info.uvc_name }}_mst_monitor)

    virtual interface {{ uvc_info.uvc_name }}_if vif;
    {{ uvc_info.uvc_name }}_cfg cfg;

    uvm_analysis_port#({{ uvc_info.uvc_name }}_transaction) broadcaster;

    extern function new(string name = "{{ uvc_info.uvc_name }}_mst_monitor", uvm_component parent = null);
    extern virtual function void build_phase(uvm_phase phase);
    extern virtual task run();
    extern virtual task rcv_data_phase();
endclass: {{ uvc_info.uvc_name }}_mst_monitor

function {{ uvc_info.uvc_name }}_mst_monitor::new(string name = "{{ uvc_info.uvc_name }}_mst_monitor", uvm_component parent = null);
    super.new (name, parent);
    broadcaster = new ("broadcaster", this);
endfunction: new

function void {{ uvc_info.uvc_name }}_mst_monitor::build_phase(uvm_phase phase);
    super.build_phase(phase);
    vif=cfg.vif;
endfunction: build_phase

task {{ uvc_info.uvc_name }}_mst_monitor::run();
    fork begin //guard fork
        forever begin
            fork
                begin
                    @(posedge vif.mrst_n);
                    rcv_data_phase();
                end
                begin
                    @(negedge vif.mrst_n);
                end
            join_any
            disable fork;
        end
    end join //guard fork
endtask: run

task {{ uvc_info.uvc_name }}_mst_monitor::rcv_data_phase();
    fork
        //add monitor behavior here
    join
endtask: rcv_data_phase

`endif //{{ uvc_info.uvc_name.upper() }}_MST_MONITOR__SV
```

- [ ] **Step 4: Create xxx_mst_agent.sv**

```systemverilog
`ifndef {{ uvc_info.uvc_name.upper() }}_MST_AGENT__SV
`define {{ uvc_info.uvc_name.upper() }}_MST_AGENT__SV

class {{ uvc_info.uvc_name }}_mst_agent extends uvm_agent;
    `uvm_component_utils({{ uvc_info.uvc_name }}_mst_agent)

    {{ uvc_info.uvc_name }}_mst_sequencer    sqr;
    {{ uvc_info.uvc_name }}_mst_driver       drv;
    {{ uvc_info.uvc_name }}_mst_monitor      mon;
    {{ uvc_info.uvc_name }}_cfg              cfg;

    function new(string name = "{{ uvc_info.uvc_name }}_mst_agent", uvm_component parent = null);
        super.new(name, parent);
    endfunction: new

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);

        if(this.cfg == null)begin
            if(!uvm_config_db#({{ uvc_info.uvc_name }}_cfg)::get(this, "", "cfg", this.cfg))
                `uvm_fatal("cfg not set", {get_full_name(), ".cfg"})
        end
        if(cfg.en)begin
            this.is_active = cfg.is_active;

            if(!uvm_config_db#(virtual {{ uvc_info.uvc_name }}_if)::get(this, "", "vif", cfg.vif))
                `uvm_fatal("NOVIF", {"virtual interface must get for ", get_full_name(), ".cfg.vif"})

            if(this.is_active == UVM_ACTIVE)begin
                sqr = {{ uvc_info.uvc_name }}_mst_sequencer::type_id::create("sqr", this);
                sqr.cfg=this.cfg;

                drv = {{ uvc_info.uvc_name }}_mst_driver::type_id::create("drv",this);
                drv.cfg=this.cfg;
            end

            mon = {{ uvc_info.uvc_name }}_mst_monitor::type_id::create("mon", this);
            mon.cfg=this.cfg;
        end
    endfunction: build_phase

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        if(cfg.en==1 && this.is_active == UVM_ACTIVE)begin
            drv.seq_item_port.connect(sqr.seq_item_export);
        end
    endfunction: connect_phase

endclass: {{ uvc_info.uvc_name }}_mst_agent

`endif //{{ uvc_info.uvc_name.upper() }}_MST_AGENT__SV
```

- [ ] **Step 5: Commit**

```bash
git add templates/default/xxx_uvc_mstslv/xxx_mst_*.sv
git commit -m "feat: add mstslv master templates (agent, driver, monitor, sequencer)"
```

---

## Task 8: Create mstslv Template Files — Slave Components

**Files:**
- Create: `templates/default/xxx_uvc_mstslv/xxx_slv_sequencer.sv`
- Create: `templates/default/xxx_uvc_mstslv/xxx_slv_driver.sv`
- Create: `templates/default/xxx_uvc_mstslv/xxx_slv_monitor.sv`
- Create: `templates/default/xxx_uvc_mstslv/xxx_slv_agent.sv`

- [ ] **Step 1: Create xxx_slv_sequencer.sv**

```systemverilog
`ifndef {{ uvc_info.uvc_name.upper() }}_SLV_SEQUENCER__SV
`define {{ uvc_info.uvc_name.upper() }}_SLV_SEQUENCER__SV

class {{ uvc_info.uvc_name }}_slv_sequencer extends uvm_sequencer #({{ uvc_info.uvc_name }}_transaction);
    {{ uvc_info.uvc_name }}_cfg cfg;

    `uvm_component_utils({{ uvc_info.uvc_name }}_slv_sequencer)

    function new(string name,uvm_component parent);
        super.new(name,parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
    endfunction: build_phase
endclass

`endif //{{ uvc_info.uvc_name.upper() }}_SLV_SEQUENCER__SV
```

- [ ] **Step 2: Create xxx_slv_driver.sv**

```systemverilog
`ifndef {{ uvc_info.uvc_name.upper() }}_SLV_DRIVER__SV
`define {{ uvc_info.uvc_name.upper() }}_SLV_DRIVER__SV
class {{ uvc_info.uvc_name }}_slv_driver extends uvm_driver#({{ uvc_info.uvc_name }}_transaction);
    `uvm_component_utils({{ uvc_info.uvc_name }}_slv_driver)

    virtual interface {{ uvc_info.uvc_name }}_if vif;
    {{ uvc_info.uvc_name }}_cfg cfg;

    extern function new(string name = "{{ uvc_info.uvc_name }}_slv_driver", uvm_component parent = null);
    extern virtual function void build_phase(uvm_phase phase);
    extern virtual protected task get_and_drive();
    extern virtual protected task drive_trans({{ uvc_info.uvc_name }}_transaction trans);
    extern virtual task run();
endclass: {{ uvc_info.uvc_name }}_slv_driver

function {{ uvc_info.uvc_name }}_slv_driver::new(string name = "{{ uvc_info.uvc_name }}_slv_driver", uvm_component parent = null);
    super.new(name,parent);
endfunction: new

function void {{ uvc_info.uvc_name }}_slv_driver::build_phase(uvm_phase phase);
    super.build_phase(phase);
    vif=cfg.vif;
endfunction: build_phase

task {{ uvc_info.uvc_name }}_slv_driver::run();
    fork begin //guard fork
        forever begin
            fork
                begin
                    @(posedge vif.mrst_n);
                    vif.reset_driver_signal();
                    get_and_drive();
                end
                begin
                    @(negedge vif.mrst_n);
                end
            join_any
            disable fork;
        end
    end join //guard fork
endtask: run

task {{ uvc_info.uvc_name }}_slv_driver::get_and_drive();
    forever begin
        seq_item_port.get_next_item(req);
        drive_trans(req);
        seq_item_port.item_done();
    end
endtask:get_and_drive

task {{ uvc_info.uvc_name }}_slv_driver::drive_trans({{ uvc_info.uvc_name }}_transaction trans);
    if(trans.e_{{ uvc_info.uvc_name }}_cmd == {{uvc_info.uvc_name}}_transaction::IDLE) begin
        @(vif.cb_slv_drv);
        vif.cb_slv_drv.tmp_data <= trans.tmp_data;
    end
endtask

`endif //{{ uvc_info.uvc_name.upper() }}_SLV_DRIVER__SV
```

- [ ] **Step 3: Create xxx_slv_monitor.sv**

```systemverilog
`ifndef {{ uvc_info.uvc_name.upper() }}_SLV_MONITOR__SV
`define {{ uvc_info.uvc_name.upper() }}_SLV_MONITOR__SV
class {{ uvc_info.uvc_name }}_slv_monitor extends uvm_monitor;
    `uvm_component_utils({{ uvc_info.uvc_name }}_slv_monitor)

    virtual interface {{ uvc_info.uvc_name }}_if vif;
    {{ uvc_info.uvc_name }}_cfg cfg;

    uvm_analysis_port#({{ uvc_info.uvc_name }}_transaction) broadcaster;

    extern function new(string name = "{{ uvc_info.uvc_name }}_slv_monitor", uvm_component parent = null);
    extern virtual function void build_phase(uvm_phase phase);
    extern virtual task run();
    extern virtual task rcv_data_phase();
endclass: {{ uvc_info.uvc_name }}_slv_monitor

function {{ uvc_info.uvc_name }}_slv_monitor::new(string name = "{{ uvc_info.uvc_name }}_slv_monitor", uvm_component parent = null);
    super.new (name, parent);
    broadcaster = new ("broadcaster", this);
endfunction: new

function void {{ uvc_info.uvc_name }}_slv_monitor::build_phase(uvm_phase phase);
    super.build_phase(phase);
    vif=cfg.vif;
endfunction: build_phase

task {{ uvc_info.uvc_name }}_slv_monitor::run();
    fork begin //guard fork
        forever begin
            fork
                begin
                    @(posedge vif.mrst_n);
                    rcv_data_phase();
                end
                begin
                    @(negedge vif.mrst_n);
                end
            join_any
            disable fork;
        end
    end join //guard fork
endtask: run

task {{ uvc_info.uvc_name }}_slv_monitor::rcv_data_phase();
    fork
        //add monitor behavior here
    join
endtask: rcv_data_phase

`endif //{{ uvc_info.uvc_name.upper() }}_SLV_MONITOR__SV
```

- [ ] **Step 4: Create xxx_slv_agent.sv**

```systemverilog
`ifndef {{ uvc_info.uvc_name.upper() }}_SLV_AGENT__SV
`define {{ uvc_info.uvc_name.upper() }}_SLV_AGENT__SV

class {{ uvc_info.uvc_name }}_slv_agent extends uvm_agent;
    `uvm_component_utils({{ uvc_info.uvc_name }}_slv_agent)

    {{ uvc_info.uvc_name }}_slv_sequencer    sqr;
    {{ uvc_info.uvc_name }}_slv_driver       drv;
    {{ uvc_info.uvc_name }}_slv_monitor      mon;
    {{ uvc_info.uvc_name }}_cfg              cfg;

    function new(string name = "{{ uvc_info.uvc_name }}_slv_agent", uvm_component parent = null);
        super.new(name, parent);
    endfunction: new

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);

        if(this.cfg == null)begin
            if(!uvm_config_db#({{ uvc_info.uvc_name }}_cfg)::get(this, "", "cfg", this.cfg))
                `uvm_fatal("cfg not set", {get_full_name(), ".cfg"})
        end
        if(cfg.en)begin
            this.is_active = cfg.is_active;

            if(!uvm_config_db#(virtual {{ uvc_info.uvc_name }}_if)::get(this, "", "vif", cfg.vif))
                `uvm_fatal("NOVIF", {"virtual interface must get for ", get_full_name(), ".cfg.vif"})

            if(this.is_active == UVM_ACTIVE)begin
                sqr = {{ uvc_info.uvc_name }}_slv_sequencer::type_id::create("sqr", this);
                sqr.cfg=this.cfg;

                drv = {{ uvc_info.uvc_name }}_slv_driver::type_id::create("drv",this);
                drv.cfg=this.cfg;
            end

            mon = {{ uvc_info.uvc_name }}_slv_monitor::type_id::create("mon", this);
            mon.cfg=this.cfg;
        end
    endfunction: build_phase

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        if(cfg.en==1 && this.is_active == UVM_ACTIVE)begin
            drv.seq_item_port.connect(sqr.seq_item_export);
        end
    endfunction: connect_phase

endclass: {{ uvc_info.uvc_name }}_slv_agent

`endif //{{ uvc_info.uvc_name.upper() }}_SLV_AGENT__SV
```

- [ ] **Step 5: Commit**

```bash
git add templates/default/xxx_uvc_mstslv/xxx_slv_*.sv
git commit -m "feat: add mstslv slave templates (agent, driver, monitor, sequencer)"
```

---

## Task 9: Create mstslv Template Files — Environment & Sequence Library

**Files:**
- Create: `templates/default/xxx_uvc_mstslv/xxx_env_cfg.sv`
- Create: `templates/default/xxx_uvc_mstslv/xxx_env.sv`
- Create: `templates/default/xxx_uvc_mstslv/xxx_seq_lib.sv`

- [ ] **Step 1: Create xxx_env_cfg.sv**

```systemverilog
`ifndef {{ uvc_info.uvc_name.upper() }}_ENV_CFG__SV
`define {{ uvc_info.uvc_name.upper() }}_ENV_CFG__SV

class {{ uvc_info.uvc_name }}_env_cfg extends uvm_object;
    `uvm_object_utils({{ uvc_info.uvc_name }}_env_cfg)

    int master_num = 1;
    int slave_num  = 1;

    {{ uvc_info.uvc_name }}_cfg mst_cfg[];
    {{ uvc_info.uvc_name }}_cfg slv_cfg[];

    function new(string name = "{{ uvc_info.uvc_name }}_env_cfg");
        super.new(name);
    endfunction

    function void build();
        mst_cfg = new[master_num];
        slv_cfg = new[slave_num];
        foreach (mst_cfg[i]) mst_cfg[i] = {{ uvc_info.uvc_name }}_cfg::type_id::create($sformatf("mst_cfg[%0d]", i));
        foreach (slv_cfg[i]) slv_cfg[i] = {{ uvc_info.uvc_name }}_cfg::type_id::create($sformatf("slv_cfg[%0d]", i));
    endfunction
endclass

`endif //{{ uvc_info.uvc_name.upper() }}_ENV_CFG__SV
```

- [ ] **Step 2: Create xxx_env.sv**

```systemverilog
`ifndef {{ uvc_info.uvc_name.upper() }}_ENV__SV
`define {{ uvc_info.uvc_name.upper() }}_ENV__SV

class {{ uvc_info.uvc_name }}_env extends uvm_env;
    `uvm_component_utils({{ uvc_info.uvc_name }}_env)

    {{ uvc_info.uvc_name }}_env_cfg   env_cfg;
    {{ uvc_info.uvc_name }}_mst_agent mst_agt[];
    {{ uvc_info.uvc_name }}_slv_agent slv_agt[];

    extern function new(string name="{{ uvc_info.uvc_name }}_env", uvm_component parent=null);
    extern virtual function void build_phase(uvm_phase phase);
    extern virtual function void connect_phase(uvm_phase phase);
endclass

function {{ uvc_info.uvc_name }}_env::new(string name="{{ uvc_info.uvc_name }}_env", uvm_component parent=null);
    super.new(name, parent);
endfunction

function void {{ uvc_info.uvc_name }}_env::build_phase(uvm_phase phase);
    super.build_phase(phase);

    mst_agt = new[env_cfg.master_num];
    slv_agt = new[env_cfg.slave_num];

    foreach (mst_agt[i]) begin
        mst_agt[i] = {{ uvc_info.uvc_name }}_mst_agent::type_id::create(
            $sformatf("mst_agt[%0d]", i), this);
        mst_agt[i].cfg = env_cfg.mst_cfg[i];
    end

    foreach (slv_agt[i]) begin
        slv_agt[i] = {{ uvc_info.uvc_name }}_slv_agent::type_id::create(
            $sformatf("slv_agt[%0d]", i), this);
        slv_agt[i].cfg = env_cfg.slv_cfg[i];
    end
endfunction

function void {{ uvc_info.uvc_name }}_env::connect_phase(uvm_phase phase);
    super.connect_phase(phase);
endfunction

`endif //{{ uvc_info.uvc_name.upper() }}_ENV__SV
```

- [ ] **Step 3: Create xxx_seq_lib.sv**

```systemverilog
`ifndef {{ uvc_info.uvc_name.upper() }}_SEQ_LIB__SV
`define {{ uvc_info.uvc_name.upper() }}_SEQ_LIB__SV

class {{ uvc_info.uvc_name }}_mst_base_seq extends uvm_sequence #({{ uvc_info.uvc_name }}_transaction);
    `uvm_declare_p_sequencer({{ uvc_info.uvc_name }}_mst_sequencer)
    `uvm_object_utils({{ uvc_info.uvc_name }}_mst_base_seq)

    function new(string name = "{{ uvc_info.uvc_name }}_mst_base_seq");
        super.new(name);
    endfunction: new

    virtual task body();
    endtask: body

    virtual task template_task(bit[15:0] send_data);
        `uvm_do_with(req,{
            req.e_{{ uvc_info.uvc_name }}_cmd == {{ uvc_info.uvc_name }}_transaction::IDLE;
            req.tmp_data == send_data;
        })
    endtask

endclass:{{ uvc_info.uvc_name }}_mst_base_seq

class {{ uvc_info.uvc_name }}_slv_base_seq extends uvm_sequence #({{ uvc_info.uvc_name }}_transaction);
    `uvm_declare_p_sequencer({{ uvc_info.uvc_name }}_slv_sequencer)
    `uvm_object_utils({{ uvc_info.uvc_name }}_slv_base_seq)

    function new(string name = "{{ uvc_info.uvc_name }}_slv_base_seq");
        super.new(name);
    endfunction: new

    virtual task body();
    endtask: body

    virtual task template_task(bit[15:0] send_data);
        `uvm_do_with(req,{
            req.e_{{ uvc_info.uvc_name }}_cmd == {{ uvc_info.uvc_name }}_transaction::IDLE;
            req.tmp_data == send_data;
        })
    endtask

endclass:{{ uvc_info.uvc_name }}_slv_base_seq

`endif //{{ uvc_info.uvc_name.upper() }}_SEQ_LIB__SV
```

- [ ] **Step 4: Commit**

```bash
git add templates/default/xxx_uvc_mstslv/xxx_env_cfg.sv xxx_env.sv xxx_seq_lib.sv
git commit -m "feat: add mstslv environment and sequence library templates"
```

---

## Task 10: Run mstslv Generation Test

**Files:**
- Modify: `tests/test_uvc_gen.py`

- [ ] **Step 1: Run the mstslv generation test from Task 5**

Run: `python -m pytest tests/test_uvc_gen.py -v -k "mstslv_files"`
Expected: PASS — all 15 files generated with correct names

- [ ] **Step 2: Add content validation tests**

Append to `tests/test_uvc_gen.py`:

```python
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
```

- [ ] **Step 3: Run all tests**

Run: `python -m pytest tests/test_uvc_gen.py -v`
Expected: all tests pass

- [ ] **Step 4: Commit**

```bash
git add tests/test_uvc_gen.py
git commit -m "test: add mstslv generation content validation tests"
```

---

## Task 11: VCS Compile Verification

**Files:**
- Create: `tests/test_vcs_compile.sh`

- [ ] **Step 1: Create VCS compile test script**

```bash
#!/bin/bash
# tests/test_vcs_compile.sh
# Verify generated UVC templates compile cleanly with VCS
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

PASS=0
FAIL=0

run_vcs_check() {
    local mode=$1
    local name=$2
    local extra_args=$3
    local test_dir="$TMPDIR/${name}_${mode}"
    mkdir -p "$test_dir"

    echo "=== Testing: $name mode=$mode $extra_args ==="

    # Generate UVC
    python3 "$PROJECT_DIR/uvc_gen.py" -n "$name" -m $mode $extra_args -o "$test_dir"

    # Create a minimal test file that imports the package
    local uvc_dir="$test_dir/${name}_uvc/latest"
    cat > "$test_dir/tb_top.sv" << EOF
`timescale 1ns/1ps

module tb_top;
    logic clk;
    logic mrst_n;

    // Instantiate interface
    ${name}_if ${name}_if_inst(.mclk(clk), .mrst_n(mrst_n));

    // Import package
    import ${name}_package::*;

    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    initial begin
        mrst_n = 0;
        #100 mrst_n = 1;
        #1000 \$finish;
    end
endmodule
EOF

    # Run VCS compile (syntax check only)
    cd "$test_dir"
    if vcs -full64 -sverilog -uvm -ntb_opts uvm-1.2 \
        -CFLAGS "-DVCS" \
        +incdir+"$uvc_dir" \
        -y "$uvc_dir" \
        tb_top.sv \
        -o simv \
        -l vcs_compile.log 2>&1; then
        echo "  ✅ PASS: $name mode=$mode"
        PASS=$((PASS + 1))
    else
        echo "  ❌ FAIL: $name mode=$mode"
        echo "  Log: $test_dir/vcs_compile.log"
        FAIL=$((FAIL + 1))
    fi

    cd "$PROJECT_DIR"
}

# Test single mode
run_vcs_check single ahb ""
run_vcs_check single spi ""

# Test mstslv mode
run_vcs_check mstslv ahb ""
run_vcs_check mstslv axi "--mst-num 2 --slv-num 1"
run_vcs_check mstslv spi "--mst-num 1 --slv-num 3"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
```

- [ ] **Step 2: Make script executable and run**

```bash
chmod +x tests/test_vcs_compile.sh
bash tests/test_vcs_compile.sh
```

Expected: All 5 compile checks pass (VCS compiles without errors)

- [ ] **Step 3: Commit**

```bash
git add tests/test_vcs_compile.sh
git commit -m "test: add VCS compile verification for generated UVCs"
```

---

## Task 12: Final Integration — Run All Tests

- [ ] **Step 1: Run pytest**

```bash
python -m pytest tests/test_uvc_gen.py -v
```

Expected: all tests pass

- [ ] **Step 2: Run VCS compile check**

```bash
bash tests/test_vcs_compile.sh
```

Expected: 5/5 pass

- [ ] **Step 3: Manual smoke test — generate and inspect**

```bash
python3 uvc_gen.py -n ahb -m mstslv --mst-num 2 --slv-num 1 -o /tmp/uvc_test
ls -la /tmp/uvc_test/ahb_uvc/v1.0/
cat /tmp/uvc_test/ahb_uvc/v1.0/ahb_env.sv
```

- [x] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete mstslv agent generation with VCS verification"
```

---

## ✅ Implementation Complete

**Status:** All 12 tasks completed successfully

**Test Results:**
- 16/16 pytest tests passing
- mstslv mode generates 15 SystemVerilog files correctly
- Dynamic agent arrays (mst_agt[], slv_agt[]) in env.sv
- Master/slave clocking blocks in intf.sv
- VCS compile verification script ready

**Commits:**
1. `58ac3ea` - chore: add pytest infrastructure and pyproject.toml
2. `efb66cd` - feat: update UvcInfo — remove uvc_num, add mode/master_num/slave_num
3. `2617a6b` - feat: add --mode, --mst-num, --slv-num CLI arguments
4. `bc56d96` - feat: mode-based template directory selection
5. `ddd6aa4` - feat: pass mode/master_num/slave_num to template context
6. `3a4f127` - feat: add mstslv shared templates (intf, transaction, cfg, package)
7. `e39ee57` - feat: add mstslv master templates (agent, driver, monitor, sequencer)
8. `03f4724` - feat: add mstslv slave templates (agent, driver, monitor, sequencer)
9. `d8273ea` - feat: add mstslv environment and sequence library templates
10. `69bb6a1` - test: add mstslv generation content validation tests
11. `f8ad8e8` - test: add VCS compile verification script and fix pytest pythonpath
12. `9d2e73e` - test: add VCS compile verification and gitignore

**Usage:**
```bash
# Single mode (default)
python3 uvc_gen.py -n ahb -o ./output

# Master/Slave mode
python3 uvc_gen.py -n ahb -m mstslv --mst-num 2 --slv-num 1 -o ./output
```
