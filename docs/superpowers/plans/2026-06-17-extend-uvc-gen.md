# Extend uvc_gen — Agent Multi-Instantiation & Optional Components

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend uvc_gen single mode to support multi-agent instantiation via `--agent-num`, and add optional components (env, coverage, scoreboard, ref_model) controlled by `--with-*` flags. Default output must remain identical to current behavior.

**Architecture:** Add `agent_num` and `with_*` fields to UvcInfo. Single-mode env/config templates gain Jinja2 conditionals for dynamic arrays. Optional component templates are always generated as files, but their `include` lines in package.svp are commented out unless the corresponding `--with-*` flag is set. Backward compatible: `python3 uvc_gen.py -n ahb -o ./output` produces the exact same 10 files with the same content.

**Tech Stack:** Python 3, Jinja2, Rich, pytest

---

## File Structure

### New Template Files

| File | Responsibility |
|---|---|
| `templates/default/xxx_uvc/xxx_coverage.sv` | Coverage collector (optional, `--with-coverage`) |
| `templates/default/xxx_uvc/xxx_scoreboard.sv` | Scoreboard (optional, `--with-scoreboard`) |
| `templates/default/xxx_uvc/xxx_ref_model.sv` | Reference model (optional, `--with-ref-model`) |

### Modified Files

| File | Changes |
|---|---|
| `uvc_gen.py:14-21` | UvcInfo: add `agent_num`, `with_env`, `with_coverage`, `with_scoreboard`, `with_ref_model` |
| `uvc_gen.py:25-38` | UvcGen.__init__: add new fields |
| `uvc_gen.py:40-65` | get_input_args: add `--agent-num`, `--with-*` flags |
| `uvc_gen.py:104-124` | init_para: accept and store new params |
| `uvc_gen.py:169-175` | generate_uvc: pass new fields to UvcInfo |
| `uvc_gen.py:229-241` | main: pass new args |
| `templates/default/xxx_uvc/xxx_environment.sv` | Conditional single/multi agent instantiation |
| `templates/default/xxx_uvc/xxx_package.svp` | Conditional includes for optional components |

### New Test Cases

| Test | Responsibility |
|---|---|
| `test_cli_agent_num_default` | `--agent-num` defaults to 1 |
| `test_cli_agent_num_custom` | `--agent-num 3` is accepted |
| `test_cli_with_env_flag` | `--with-env` sets `with_env=True` |
| `test_cli_with_coverage_flag` | `--with-coverage` sets `with_coverage=True` |
| `test_single_mode_default_unchanged` | Default single mode produces identical output |
| `test_single_mode_multi_agent_files` | `--agent-num 3` generates env with agt[] |
| `test_single_mode_multi_agent_env_content` | env.sv contains `agt[]` array and dynamic creation |
| `test_single_mode_with_env_includes` | `--with-env` uncomments env include in pkg |
| `test_single_mode_with_coverage_includes` | `--with-coverage` uncomments coverage include |

---

## Task 1: UvcInfo & CLI — Add New Fields

**Files:**
- Modify: `uvc_gen.py:14-21` (UvcInfo)
- Modify: `uvc_gen.py:25-38` (UvcGen.__init__)
- Modify: `uvc_gen.py:40-65` (get_input_args)
- Modify: `uvc_gen.py:104-124` (init_para)
- Modify: `uvc_gen.py:169-175` (generate_uvc UvcInfo construction)
- Modify: `uvc_gen.py:229-241` (main)
- Modify: `tests/test_uvc_gen.py`

- [ ] **Step 1: Write failing tests for new CLI args**

Append to `tests/test_uvc_gen.py`:

```python
def test_cli_agent_num_default():
    """--agent-num defaults to 1."""
    gen = __import__('uvc_gen').UvcGen()
    with patch('sys.argv', ['uvc_gen', '-n', 'ahb']):
        args = gen.get_input_args()
    assert args.agent_num == 1

def test_cli_agent_num_custom():
    """--agent-num 3 is accepted."""
    gen = __import__('uvc_gen').UvcGen()
    with patch('sys.argv', ['uvc_gen', '-n', 'ahb', '--agent-num', '3']):
        args = gen.get_input_args()
    assert args.agent_num == 3

def test_cli_with_env_flag():
    """--with-env sets with_env=True."""
    gen = __import__('uvc_gen').UvcGen()
    with patch('sys.argv', ['uvc_gen', '-n', 'ahb', '--with-env']):
        args = gen.get_input_args()
    assert args.with_env is True

def test_cli_with_env_default_false():
    """--with-env defaults to False."""
    gen = __import__('uvc_gen').UvcGen()
    with patch('sys.argv', ['uvc_gen', '-n', 'ahb']):
        args = gen.get_input_args()
    assert args.with_env is False

def test_cli_with_coverage_flag():
    """--with-coverage sets with_coverage=True."""
    gen = __import__('uvc_gen').UvcGen()
    with patch('sys.argv', ['uvc_gen', '-n', 'ahb', '--with-coverage']):
        args = gen.get_input_args()
    assert args.with_coverage is True

def test_cli_with_scoreboard_flag():
    """--with-scoreboard sets with_scoreboard=True."""
    gen = __import__('uvc_gen').UvcGen()
    with patch('sys.argv', ['uvc_gen', '-n', 'ahb', '--with-scoreboard']):
        args = gen.get_input_args()
    assert args.with_scoreboard is True

def test_cli_with_ref_model_flag():
    """--with-ref-model sets with_ref_model=True."""
    gen = __import__('uvc_gen').UvcGen()
    with patch('sys.argv', ['uvc_gen', '-n', 'ahb', '--with-ref-model']):
        args = gen.get_input_args()
    assert args.with_ref_model is True

def test_uvc_info_new_fields():
    """UvcInfo should have agent_num and with_* fields."""
    info = UvcInfo(uvc_name="ahb", agent_num=3, with_env=True, with_coverage=True)
    assert info.agent_num == 3
    assert info.with_env is True
    assert info.with_coverage is True
    assert info.with_scoreboard is False
    assert info.with_ref_model is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_uvc_gen.py -v -k "cli_agent_num or cli_with_env or cli_with_coverage or cli_with_scoreboard or cli_with_ref_model or uvc_info_new"`
Expected: FAIL — new args/fields don't exist yet

- [ ] **Step 3: Update UvcInfo dataclass**

Replace `uvc_gen.py:14-21` with:

```python
@dataclass
class UvcInfo:
    """UVC 信息类"""
    uvc_name: str = ''
    version: str = ''
    mode: str = 'single'
    master_num: int = 1
    slave_num: int = 1
    agent_num: int = 1
    with_env: bool = False
    with_coverage: bool = False
    with_scoreboard: bool = False
    with_ref_model: bool = False
```

- [ ] **Step 4: Update UvcGen.__init__**

Replace `uvc_gen.py:25-38` with:

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
    self.agent_num: int = 1
    self.with_env: bool = False
    self.with_coverage: bool = False
    self.with_scoreboard: bool = False
    self.with_ref_model: bool = False

    script_dir = Path(__file__).resolve().parent
    self.TEMPLATES_DIR = script_dir / "templates"
    self.DEFAULT_TPL = str(self.TEMPLATES_DIR / "default" / "xxx_uvc")
    self.MSTSLV_TPL = str(self.TEMPLATES_DIR / "default" / "xxx_uvc_mstslv")
```

- [ ] **Step 5: Update get_input_args**

After the `--slv-num` argument (line 64), add:

```python
parser.add_argument('--agent-num',
                    type=int, default=1,
                    help='Number of agents (single mode)')
parser.add_argument('--with-env',
                    action='store_true', default=False,
                    help='Enable env/env_cfg includes in package')
parser.add_argument('--with-coverage',
                    action='store_true', default=False,
                    help='Enable coverage collector include in package')
parser.add_argument('--with-scoreboard',
                    action='store_true', default=False,
                    help='Enable scoreboard include in package')
parser.add_argument('--with-ref-model',
                    action='store_true', default=False,
                    help='Enable reference model include in package')
```

- [ ] **Step 6: Update init_para signature and body**

Replace `uvc_gen.py:104-124` with:

```python
def init_para(self, tpl_dir: str, uvc_name: str, version: str, output: str,
              mode: str = 'single', master_num: int = 1, slave_num: int = 1,
              agent_num: int = 1, with_env: bool = False,
              with_coverage: bool = False, with_scoreboard: bool = False,
              with_ref_model: bool = False) -> None:
    """初始化参数"""
    self.mode = mode
    self.master_num = master_num
    self.slave_num = slave_num
    self.agent_num = agent_num
    self.with_env = with_env
    self.with_coverage = with_coverage
    self.with_scoreboard = with_scoreboard
    self.with_ref_model = with_ref_model

    # If tpl_dir is the default and mode is mstslv, switch to mstslv template
    if mode == 'mstslv' and tpl_dir == self.DEFAULT_TPL:
        tpl_dir = self.MSTSLV_TPL

    # 处理模板目录路径
    resolved_tpl_dir = self._resolve_template_dir(tpl_dir)

    if not Path(resolved_tpl_dir).exists():
        raise FileNotFoundError(f"Template directory not found: {resolved_tpl_dir}")

    self.tpl_dir = resolved_tpl_dir
    self.uvc_name = uvc_name
    self.version = version
    self.output = output
```

- [ ] **Step 7: Update UvcInfo construction in generate_uvc**

Replace `uvc_gen.py:169-175` with:

```python
uvc_info = UvcInfo(
    uvc_name=self.uvc_name,
    version=self.version,
    mode=self.mode,
    master_num=self.master_num,
    slave_num=self.slave_num,
    agent_num=self.agent_num,
    with_env=self.with_env,
    with_coverage=self.with_coverage,
    with_scoreboard=self.with_scoreboard,
    with_ref_model=self.with_ref_model
)
```

- [ ] **Step 8: Update main() to pass new args**

Replace `uvc_gen.py:234-235` (the init_para call in main) with:

```python
uvc_gen.init_para(args.tpl_dir, args.uvc_name, args.version, args.output,
                  mode=args.mode, master_num=args.mst_num, slave_num=args.slv_num,
                  agent_num=args.agent_num, with_env=args.with_env,
                  with_coverage=args.with_coverage, with_scoreboard=args.with_scoreboard,
                  with_ref_model=args.with_ref_model)
```

- [ ] **Step 9: Run all new tests**

Run: `.venv/bin/pytest tests/test_uvc_gen.py -v -k "cli_agent_num or cli_with_env or cli_with_coverage or cli_with_scoreboard or cli_with_ref_model or uvc_info_new"`
Expected: 8 passed

- [ ] **Step 10: Run ALL tests to verify backward compatibility**

Run: `.venv/bin/pytest tests/test_uvc_gen.py -v`
Expected: all 24 passed (16 existing + 8 new)

- [ ] **Step 11: Commit**

```bash
git add uvc_gen.py tests/test_uvc_gen.py
git commit -m "feat: add --agent-num and --with-* CLI arguments"
```

---

## Task 2: Single-Mode Environment — Multi-Agent Support

**Files:**
- Modify: `templates/default/xxx_uvc/xxx_environment.sv`
- Modify: `templates/default/xxx_uvc/xxx_package.svp`
- Modify: `tests/test_uvc_gen.py`

**Key constraint:** When `agent_num=1` (default), generated output must be identical to current behavior.

- [ ] **Step 1: Write failing tests**

Append to `tests/test_uvc_gen.py`:

```python
def test_single_mode_default_unchanged():
    """Default single mode (agent_num=1, no --with-*) produces identical output."""
    gen = __import__('uvc_gen').UvcGen()
    output_dir = tempfile.mkdtemp()
    try:
        gen.init_para(gen.DEFAULT_TPL, "ahb", "v1.0", output_dir, mode="single")
        gen.parse_tpl_dir()
        gen.generate_uvc()

        env_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_environment.sv").read_text()
        # Single agent: should have direct agt, NOT agt[]
        assert "agt;" in env_content
        assert "agt[]" not in env_content
        # Should use type_id::create("agt", this)
        assert 'create("agt"' in env_content

        pkg_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_package.svp").read_text()
        # environment include should be commented out by default
        assert "//`include" in pkg_content
        assert "ahb_environment.sv" in pkg_content
    finally:
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)

def test_single_mode_multi_agent_env_content():
    """--agent-num 3 generates env with agt[] dynamic array."""
    gen = __import__('uvc_gen').UvcGen()
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
    gen = __import__('uvc_gen').UvcGen()
    output_dir = tempfile.mkdtemp()
    try:
        gen.init_para(gen.DEFAULT_TPL, "ahb", "v1.0", output_dir,
                      mode="single", with_env=True)
        gen.parse_tpl_dir()
        gen.generate_uvc()

        pkg_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_package.svp").read_text()
        # environment include should NOT be commented out
        lines = pkg_content.split('\n')
        env_include_line = [l for l in lines if "environment.sv" in l][0]
        assert not env_include_line.strip().startswith("//")
    finally:
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)

def test_single_mode_multi_agent_with_env():
    """--agent-num 2 --with-env generates full env with dynamic arrays."""
    gen = __import__('uvc_gen').UvcGen()
    output_dir = tempfile.mkdtemp()
    try:
        gen.init_para(gen.DEFAULT_TPL, "ahb", "v1.0", output_dir,
                      mode="single", agent_num=2, with_env=True)
        gen.parse_tpl_dir()
        gen.generate_uvc()

        env_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_environment.sv").read_text()
        assert "agt[]" in env_content
        assert "new[env_cfg.agent_num]" in env_content

        # Check env_cfg is generated
        cfg_content = (Path(output_dir) / "ahb_uvc" / "v1.0" / "ahb_env_cfg.sv").read_text()
        assert "agent_num" in cfg_content
        assert "agt_cfg[]" in cfg_content
    finally:
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_uvc_gen.py -v -k "single_mode_default_unchanged or single_mode_multi_agent or single_mode_with_env"`
Expected: FAIL — templates don't support conditionals yet

- [ ] **Step 3: Update xxx_environment.sv template**

Replace `templates/default/xxx_uvc/xxx_environment.sv` with:

```
`ifndef {{ uvc_info.uvc_name.upper() }}_ENVIRONMENT__SV
`define {{ uvc_info.uvc_name.upper() }}_ENVIRONMENT__SV

class {{ uvc_info.uvc_name }}_environment extends uvm_env;
    `uvm_component_utils({{ uvc_info.uvc_name }}_environment)

{% if uvc_info.agent_num > 1 %}
    {{ uvc_info.uvc_name }}_environment_cfg   env_cfg;
    {{ uvc_info.uvc_name }}_agent             agt[];
{% else %}
    {{ uvc_info.uvc_name }}_agent    agt;
    {{ uvc_info.uvc_name }}_config   cfg;
{% endif %}

    extern function new(string name="{{ uvc_info.uvc_name }}_environment", uvm_component parent=null);
    extern virtual function void build_phase(uvm_phase phase);
    extern virtual function void connect_phase(uvm_phase phase);

endclass: {{ uvc_info.uvc_name }}_environment

function {{ uvc_info.uvc_name }}_environment::new(string name= "{{ uvc_info.uvc_name }}_environment", uvm_component parent=null);
    super.new(name,parent);
endfunction: new

function void {{ uvc_info.uvc_name }}_environment::build_phase(uvm_phase phase);
    super.build_phase(phase);
{% if uvc_info.agent_num > 1 %}
    agt = new[env_cfg.agent_num];
    foreach (agt[i]) begin
        agt[i] = {{ uvc_info.uvc_name }}_agent::type_id::create(
            $sformatf("agt[%0d]", i), this);
        agt[i].cfg = env_cfg.agt_cfg[i];
    end
{% else %}
    //cfg gotted through 'UVM_REFERENCE'
    //uvm_config_db#(uvm_object)::set(this, "agt", "cfg", cfg);
    agt = {{ uvc_info.uvc_name }}_agent::type_id::create("agt",this);
    agt.cfg = this.cfg;
{% endif %}
endfunction: build_phase

function void {{ uvc_info.uvc_name }}_environment::connect_phase(uvm_phase phase);
    super.connect_phase(phase);
endfunction: connect_phase

`endif //{{ uvc_info.uvc_name.upper() }}_ENVIRONMENT__SV
```

- [ ] **Step 4: Create xxx_env_cfg.sv template (for multi-agent mode)**

Create `templates/default/xxx_uvc/xxx_env_cfg.sv`:

```
`ifndef {{ uvc_info.uvc_name.upper() }}_ENVIRONMENT_CFG__SV
`define {{ uvc_info.uvc_name.upper() }}_ENVIRONMENT_CFG__SV

class {{ uvc_info.uvc_name }}_environment_cfg extends uvm_object;
    `uvm_object_utils({{ uvc_info.uvc_name }}_environment_cfg)

    int agent_num = {{ uvc_info.agent_num }};
    {{ uvc_info.uvc_name }}_config agt_cfg[];

    function new(string name = "{{ uvc_info.uvc_name }}_environment_cfg");
        super.new(name);
    endfunction

    function void build();
        agt_cfg = new[agent_num];
        foreach (agt_cfg[i])
            agt_cfg[i] = {{ uvc_info.uvc_name }}_config::type_id::create($sformatf("agt_cfg[%0d]", i));
    endfunction
endclass

`endif //{{ uvc_info.uvc_name.upper() }}_ENVIRONMENT_CFG__SV
```

- [ ] **Step 5: Update xxx_package.svp template**

Replace `templates/default/xxx_uvc/xxx_package.svp` with:

```
`ifndef {{ uvc_info.uvc_name.upper() }}_PACKAGE__SVP
`define {{ uvc_info.uvc_name.upper() }}_PACKAGE__SVP

{% set prefix = uvc_info.uvc_name + '_uvc/' + (uvc_info.version ~ '/' if uvc_info.version != '' else '') %}
`include "{{prefix}}{{uvc_info.uvc_name}}_intf.sv"
package {{ uvc_info.uvc_name }}_package;

    import uvm_pkg::*;

    // === Agent components (always included) ===
    `include "{{prefix}}{{uvc_info.uvc_name}}_transaction.sv"
    `include "{{prefix}}{{uvc_info.uvc_name}}_config.sv"
    `include "{{prefix}}{{uvc_info.uvc_name}}_sequencer.sv"
    `include "{{prefix}}{{uvc_info.uvc_name}}_driver.sv"
    `include "{{prefix}}{{uvc_info.uvc_name}}_monitor.sv"
    `include "{{prefix}}{{uvc_info.uvc_name}}_agent.sv"
    `include "{{prefix}}{{uvc_info.uvc_name}}_seq_lib.sv"

{% if uvc_info.with_env %}
    // === Environment components ===
{% if uvc_info.agent_num > 1 %}
    `include "{{prefix}}{{uvc_info.uvc_name}}_environment_cfg.sv"
{% endif %}
    `include "{{prefix}}{{uvc_info.uvc_name}}_environment.sv"
{% else %}
    // === Environment components (enable with --with-env) ===
    //`include "{{prefix}}{{uvc_info.uvc_name}}_environment.sv"
{% endif %}

{% if uvc_info.with_coverage %}
    // === Coverage ===
    `include "{{prefix}}{{uvc_info.uvc_name}}_coverage.sv"
{% else %}
    // === Coverage (enable with --with-coverage) ===
    //`include "{{prefix}}{{uvc_info.uvc_name}}_coverage.sv"
{% endif %}

{% if uvc_info.with_scoreboard %}
    // === Scoreboard ===
    `include "{{prefix}}{{uvc_info.uvc_name}}_scoreboard.sv"
{% else %}
    // === Scoreboard (enable with --with-scoreboard) ===
    //`include "{{prefix}}{{uvc_info.uvc_name}}_scoreboard.sv"
{% endif %}

{% if uvc_info.with_ref_model %}
    // === Reference Model ===
    `include "{{prefix}}{{uvc_info.uvc_name}}_ref_model.sv"
{% else %}
    // === Reference Model (enable with --with-ref-model) ===
    //`include "{{prefix}}{{uvc_info.uvc_name}}_ref_model.sv"
{% endif %}

endpackage
`endif
```

- [ ] **Step 6: Run tests**

Run: `.venv/bin/pytest tests/test_uvc_gen.py -v -k "single_mode"`
Expected: all single_mode tests pass

- [ ] **Step 7: Run ALL tests**

Run: `.venv/bin/pytest tests/test_uvc_gen.py -v`
Expected: all tests pass

- [ ] **Step 8: Manual verification — default output unchanged**

Run: `python3 uvc_gen.py -n ahb -o /tmp/uvc_default_check`
Then verify:
```bash
# Should produce exactly 10 files (same as before)
ls /tmp/uvc_default_check/ahb_uvc/v1.0/ | wc -l
# Expected: 10

# Package should have env commented out
grep "environment" /tmp/uvc_default_check/ahb_uvc/v1.0/ahb_package.svp
# Expected: //`include "...ahb_environment.sv"

# Env should have single agent (no array)
grep "agt" /tmp/uvc_default_check/ahb_uvc/v1.0/ahb_environment.sv
# Expected: agt; (not agt[])

# Cleanup
rm -rf /tmp/uvc_default_check
```

- [ ] **Step 9: Commit**

```bash
git add templates/default/xxx_uvc/xxx_environment.sv templates/default/xxx_uvc/xxx_env_cfg.sv templates/default/xxx_uvc/xxx_package.svp tests/test_uvc_gen.py
git commit -m "feat: single-mode env supports multi-agent via --agent-num"
```

---

## Task 3: Optional Component Templates

**Files:**
- Create: `templates/default/xxx_uvc/xxx_coverage.sv`
- Create: `templates/default/xxx_uvc/xxx_scoreboard.sv`
- Create: `templates/default/xxx_uvc/xxx_ref_model.sv`
- Modify: `tests/test_uvc_gen.py`

- [ ] **Step 1: Write failing test**

Append to `tests/test_uvc_gen.py`:

```python
def test_single_mode_with_coverage_includes():
    """--with-coverage uncomments coverage include and generates file."""
    gen = __import__('uvc_gen').UvcGen()
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
    gen = __import__('uvc_gen').UvcGen()
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
    gen = __import__('uvc_gen').UvcGen()
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
    gen = __import__('uvc_gen').UvcGen()
    output_dir = tempfile.mkdtemp()
    try:
        gen.init_para(gen.DEFAULT_TPL, "ahb", "v1.0", output_dir, mode="single")
        gen.parse_tpl_dir()
        gen.generate_uvc()

        out_dir = Path(output_dir) / "ahb_uvc" / "v1.0"
        assert not (out_dir / "ahb_coverage.sv").exists()
        assert not (out_dir / "ahb_scoreboard.sv").exists()
        assert not (out_dir / "ahb_ref_model.sv").exists()
        assert not (out_dir / "ahb_env_cfg.sv").exists()
    finally:
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_uvc_gen.py -v -k "with_coverage_includes or with_scoreboard_includes or with_ref_model_includes or optional_components_default"`
Expected: FAIL — templates don't exist yet

- [ ] **Step 3: Create xxx_coverage.sv**

Create `templates/default/xxx_uvc/xxx_coverage.sv`:

```
`ifndef {{ uvc_info.uvc_name.upper() }}_COVERAGE__SV
`define {{ uvc_info.uvc_name.upper() }}_COVERAGE__SV

class {{ uvc_info.uvc_name }}_coverage extends uvm_subscriber #({{ uvc_info.uvc_name }}_transaction);
    `uvm_component_utils({{ uvc_info.uvc_name }}_coverage)

    {{ uvc_info.uvc_name }}_transaction tr;

    // TODO: Define covergroups and coverpoints here

    function new(string name = "{{ uvc_info.uvc_name }}_coverage", uvm_component parent = null);
        super.new(name, parent);
    endfunction: new

    function void write({{ uvc_info.uvc_name }}_transaction t);
        // TODO: Sample coverage
        tr = t;
    endfunction: write

endclass: {{ uvc_info.uvc_name }}_coverage

`endif //{{ uvc_info.uvc_name.upper() }}_COVERAGE__SV
```

- [ ] **Step 4: Create xxx_scoreboard.sv**

Create `templates/default/xxx_uvc/xxx_scoreboard.sv`:

```
`ifndef {{ uvc_info.uvc_name.upper() }}_SCOREBOARD__SV
`define {{ uvc_info.uvc_name.upper() }}_SCOREBOARD__SV

class {{ uvc_info.uvc_name }}_scoreboard extends uvm_scoreboard;
    `uvm_component_utils({{ uvc_info.uvc_name }}_scoreboard)

    uvm_analysis_imp #({{ uvc_info.uvc_name }}_transaction, {{ uvc_info.uvc_name }}_scoreboard) exp_port;

    // TODO: Add expected transaction queue and comparison logic

    function new(string name = "{{ uvc_info.uvc_name }}_scoreboard", uvm_component parent = null);
        super.new(name, parent);
        exp_port = new("exp_port", this);
    endfunction: new

    function void write({{ uvc_info.uvc_name }}_transaction tr);
        // TODO: Compare actual vs expected
    endfunction: write

endclass: {{ uvc_info.uvc_name }}_scoreboard

`endif //{{ uvc_info.uvc_name.upper() }}_SCOREBOARD__SV
```

- [ ] **Step 5: Create xxx_ref_model.sv**

Create `templates/default/xxx_uvc/xxx_ref_model.sv`:

```
`ifndef {{ uvc_info.uvc_name.upper() }}_REF_MODEL__SV
`define {{ uvc_info.uvc_name.upper() }}_REF_MODEL__SV

class {{ uvc_info.uvc_name }}_ref_model extends uvm_component;
    `uvm_component_utils({{ uvc_info.uvc_name }}_ref_model)

    uvm_analysis_port #({{ uvc_info.uvc_name }}_transaction) out_port;

    // TODO: Add reference model logic

    function new(string name = "{{ uvc_info.uvc_name }}_ref_model", uvm_component parent = null);
        super.new(name, parent);
        out_port = new("out_port", this);
    endfunction: new

    task run_phase(uvm_phase phase);
        // TODO: Implement reference model behavior
    endtask: run_phase

endclass: {{ uvc_info.uvc_name }}_ref_model

`endif //{{ uvc_info.uvc_name.upper() }}_REF_MODEL__SV
```

- [ ] **Step 6: Update generate_uvc to skip optional templates when not requested**

In `uvc_gen.py`, in the `generate_uvc` method, inside the `for file_path in self.file_list:` loop, after the `rel_path = file_path.relative_to(self.tpl_dir)` line (around line 189), add:

```python
                    # Skip optional component templates if not requested
                    skip_map = {
                        'xxx_environment.sv': not (self.with_env or self.agent_num > 1),
                        'xxx_env_cfg.sv': not (self.with_env and self.agent_num > 1),
                        'xxx_coverage.sv': not self.with_coverage,
                        'xxx_scoreboard.sv': not self.with_scoreboard,
                        'xxx_ref_model.sv': not self.with_ref_model,
                    }
                    if skip_map.get(file_path.name, False):
                        continue
```

- [ ] **Step 7: Run tests**

Run: `.venv/bin/pytest tests/test_uvc_gen.py -v`
Expected: all tests pass

- [ ] **Step 8: Manual verification**

Run: `python3 uvc_gen.py -n ahb --agent-num 2 --with-env --with-coverage --with-scoreboard --with-ref-model -o /tmp/uvc_full`
```bash
ls /tmp/uvc_full/ahb_uvc/v1.0/
# Expected: 14 files (10 base + env_cfg + coverage + scoreboard + ref_model)

# All includes should be uncommented
grep -v "^//" /tmp/uvc_full/ahb_uvc/v1.0/ahb_package.svp | grep "include"
# Expected: all include lines active

rm -rf /tmp/uvc_full
```

- [ ] **Step 9: Commit**

```bash
git add templates/default/xxx_uvc/xxx_coverage.sv templates/default/xxx_uvc/xxx_scoreboard.sv templates/default/xxx_uvc/xxx_ref_model.sv uvc_gen.py tests/test_uvc_gen.py
git commit -m "feat: add optional component templates (coverage, scoreboard, ref_model)"
```

---

## Task 4: mstslv Mode — Optional Components Support

**Files:**
- Create: `templates/default/xxx_uvc_mstslv/xxx_coverage.sv`
- Create: `templates/default/xxx_uvc_mstslv/xxx_scoreboard.sv`
- Create: `templates/default/xxx_uvc_mstslv/xxx_ref_model.sv`
- Modify: `templates/default/xxx_uvc_mstslv/xxx_package.svp`
- Modify: `tests/test_uvc_gen.py`

- [ ] **Step 1: Write failing test**

Append to `tests/test_uvc_gen.py`:

```python
def test_mstslv_with_coverage():
    """mstslv mode with --with-coverage generates coverage file."""
    gen = __import__('uvc_gen').UvcGen()
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_uvc_gen.py -v -k "mstslv_with_coverage"`
Expected: FAIL

- [ ] **Step 3: Create mstslv optional component templates**

Create `templates/default/xxx_uvc_mstslv/xxx_coverage.sv` (same content as single mode):

```
`ifndef {{ uvc_info.uvc_name.upper() }}_COVERAGE__SV
`define {{ uvc_info.uvc_name.upper() }}_COVERAGE__SV

class {{ uvc_info.uvc_name }}_coverage extends uvm_subscriber #({{ uvc_info.uvc_name }}_transaction);
    `uvm_component_utils({{ uvc_info.uvc_name }}_coverage)

    {{ uvc_info.uvc_name }}_transaction tr;

    // TODO: Define covergroups and coverpoints here

    function new(string name = "{{ uvc_info.uvc_name }}_coverage", uvm_component parent = null);
        super.new(name, parent);
    endfunction: new

    function void write({{ uvc_info.uvc_name }}_transaction t);
        // TODO: Sample coverage
        tr = t;
    endfunction: write

endclass: {{ uvc_info.uvc_name }}_coverage

`endif //{{ uvc_info.uvc_name.upper() }}_COVERAGE__SV
```

Create `templates/default/xxx_uvc_mstslv/xxx_scoreboard.sv` (same content as single mode):

```
`ifndef {{ uvc_info.uvc_name.upper() }}_SCOREBOARD__SV
`define {{ uvc_info.uvc_name.upper() }}_SCOREBOARD__SV

class {{ uvc_info.uvc_name }}_scoreboard extends uvm_scoreboard;
    `uvm_component_utils({{ uvc_info.uvc_name }}_scoreboard)

    uvm_analysis_imp #({{ uvc_info.uvc_name }}_transaction, {{ uvc_info.uvc_name }}_scoreboard) exp_port;

    // TODO: Add expected transaction queue and comparison logic

    function new(string name = "{{ uvc_info.uvc_name }}_scoreboard", uvm_component parent = null);
        super.new(name, parent);
        exp_port = new("exp_port", this);
    endfunction: new

    function void write({{ uvc_info.uvc_name }}_transaction tr);
        // TODO: Compare actual vs expected
    endfunction: write

endclass: {{ uvc_info.uvc_name }}_scoreboard

`endif //{{ uvc_info.uvc_name.upper() }}_SCOREBOARD__SV
```

Create `templates/default/xxx_uvc_mstslv/xxx_ref_model.sv` (same content as single mode):

```
`ifndef {{ uvc_info.uvc_name.upper() }}_REF_MODEL__SV
`define {{ uvc_info.uvc_name.upper() }}_REF_MODEL__SV

class {{ uvc_info.uvc_name }}_ref_model extends uvm_component;
    `uvm_component_utils({{ uvc_info.uvc_name }}_ref_model)

    uvm_analysis_port #({{ uvc_info.uvc_name }}_transaction) out_port;

    // TODO: Add reference model logic

    function new(string name = "{{ uvc_info.uvc_name }}_ref_model", uvm_component parent = null);
        super.new(name, parent);
        out_port = new("out_port", this);
    endfunction: new

    task run_phase(uvm_phase phase);
        // TODO: Implement reference model behavior
    endtask: run_phase

endclass: {{ uvc_info.uvc_name }}_ref_model

`endif //{{ uvc_info.uvc_name.upper() }}_REF_MODEL__SV
```

- [ ] **Step 4: Update mstslv package.svp**

Replace `templates/default/xxx_uvc_mstslv/xxx_package.svp` with:

```
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

{% if uvc_info.with_coverage %}
    `include "{{prefix}}{{uvc_info.uvc_name}}_coverage.sv"
{% else %}
    //`include "{{prefix}}{{uvc_info.uvc_name}}_coverage.sv"
{% endif %}

{% if uvc_info.with_scoreboard %}
    `include "{{prefix}}{{uvc_info.uvc_name}}_scoreboard.sv"
{% else %}
    //`include "{{prefix}}{{uvc_info.uvc_name}}_scoreboard.sv"
{% endif %}

{% if uvc_info.with_ref_model %}
    `include "{{prefix}}{{uvc_info.uvc_name}}_ref_model.sv"
{% else %}
    //`include "{{prefix}}{{uvc_info.uvc_name}}_ref_model.sv"
{% endif %}

endpackage
`endif
```

- [ ] **Step 5: Update generate_uvc skip logic for mstslv**

The skip_map in `generate_uvc` (added in Task 3 Step 6) already covers `xxx_coverage.sv`, `xxx_scoreboard.sv`, and `xxx_ref_model.sv`. No additional changes needed for mstslv mode since the filenames are the same.

- [ ] **Step 6: Run all tests**

Run: `.venv/bin/pytest tests/test_uvc_gen.py -v`
Expected: all tests pass

- [ ] **Step 7: Commit**

```bash
git add templates/default/xxx_uvc_mstslv/xxx_coverage.sv templates/default/xxx_uvc_mstslv/xxx_scoreboard.sv templates/default/xxx_uvc_mstslv/xxx_ref_model.sv templates/default/xxx_uvc_mstslv/xxx_package.svp tests/test_uvc_gen.py
git commit -m "feat: mstslv mode supports optional components (coverage, scoreboard, ref_model)"
```

---

## Task 5: Final Integration & Cleanup

- [ ] **Step 1: Run ALL tests**

Run: `.venv/bin/pytest tests/test_uvc_gen.py -v`
Expected: all tests pass

- [ ] **Step 2: Manual smoke test — default single mode unchanged**

Run:
```bash
python3 uvc_gen.py -n ahb -o /tmp/uvc_smoke
ls /tmp/uvc_smoke/ahb_uvc/v1.0/
# Expected: 10 files, same as original

# Verify package content
cat /tmp/uvc_smoke/ahb_uvc/v1.0/ahb_package.svp
# Expected: env include commented out, optional components commented out

rm -rf /tmp/uvc_smoke
```

- [ ] **Step 3: Manual smoke test — multi-agent with all options**

Run:
```bash
python3 uvc_gen.py -n ahb --agent-num 3 --with-env --with-coverage --with-scoreboard --with-ref-model -o /tmp/uvc_full
ls /tmp/uvc_full/ahb_uvc/v1.0/
# Expected: 14 files

cat /tmp/uvc_full/ahb_uvc/v1.0/ahb_environment.sv
# Expected: agt[] array, dynamic instantiation

cat /tmp/uvc_full/ahb_uvc/v1.0/ahb_package.svp
# Expected: all includes uncommented

rm -rf /tmp/uvc_full
```

- [ ] **Step 4: Manual smoke test — mstslv with optional components**

Run:
```bash
python3 uvc_gen.py -n ahb -m mstslv --mst-num 2 --slv-num 1 --with-coverage -o /tmp/uvc_mstslv
ls /tmp/uvc_mstslv/ahb_uvc/v1.0/
# Expected: 16 files (15 base + coverage)

cat /tmp/uvc_mstslv/ahb_uvc/v1.0/ahb_package.svp
# Expected: coverage include active, scoreboard/ref_model commented

rm -rf /tmp/uvc_mstslv
```

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: complete uvc_gen extension — multi-agent and optional components"
```
