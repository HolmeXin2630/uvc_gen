# Master/Slave Agent Architecture Design

**Date:** 2026-06-16
**Status:** Approved
**Scope:** uvc_gen — UVM Verification Component code generator

---

## 1. Purpose

Extend uvc_gen to support bus protocol UVCs with master/slave agent architecture. Current single-agent mode generates one agent (driver, monitor, sequencer, config). The new `mstslv` mode generates a complete environment with dynamically instantiated master and slave agent arrays.

**Use cases:** AHB, AXI, APB, SPI, I2C — any bus protocol where master and slave have distinct behavior but share the same interface and transaction type.

---

## 2. Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Naming style | `xxx_mst_agent` / `xxx_slv_agent` (abbreviated) | Concise, follows common UVM convention |
| Transaction | Shared between mst and slv | Most bus protocols use the same transaction structure |
| Template organization | New independent template set `xxx_uvc_mstslv/` | Clean separation, no conditional complexity in templates |
| Interface | Shared `xxx_if`, separate clocking blocks | Single physical interface, distinct drv/mon views per role |
| CLI interface | `--mode` parameter (`single` / `mstslv`) | Intuitive, auto-selects template directory |

---

## 3. CLI Interface

```bash
# Single agent mode (default, behavior unchanged)
uvc_gen -n ahb

# Master/Slave mode
uvc_gen -n ahb -m mstslv

# Specify agent counts
uvc_gen -n ahb -m mstslv --mst-num 2 --slv-num 1
```

### New CLI Arguments

| Argument | Short | Default | Description |
|---|---|---|---|
| `--mode` | `-m` | `single` | Generation mode: `single` or `mstslv` |
| `--mst-num` | — | `1` | Number of master agents (mstslv mode only) |
| `--slv-num` | — | `1` | Number of slave agents (mstslv mode only) |

### Template Directory Selection

- `--mode single` → `templates/default/xxx_uvc/`
- `--mode mstslv` → `templates/default/xxx_uvc_mstslv/`

The `-t` parameter still works as an override.

---

## 4. Template Directory Structure

```
templates/default/
├── xxx_uvc/              ← Existing single agent (unchanged)
│   ├── xxx_agent.sv
│   ├── xxx_config.sv
│   ├── xxx_driver.sv
│   ├── xxx_environment.sv
│   ├── xxx_intf.sv
│   ├── xxx_monitor.sv
│   ├── xxx_package.svp
│   ├── xxx_seq_lib.sv
│   ├── xxx_sequencer.sv
│   └── xxx_transaction.sv
│
└── xxx_uvc_mstslv/       ← New mst/slv mode
    ├── xxx_intf.sv          # Shared interface, 4 clocking blocks
    ├── xxx_transaction.sv   # Shared transaction
    ├── xxx_cfg.sv           # Shared agent config
    ├── xxx_mst_agent.sv     # Master agent
    ├── xxx_mst_driver.sv    # Master driver
    ├── xxx_mst_monitor.sv   # Master monitor
    ├── xxx_mst_sequencer.sv # Master sequencer
    ├── xxx_slv_agent.sv     # Slave agent
    ├── xxx_slv_driver.sv    # Slave driver
    ├── xxx_slv_monitor.sv   # Slave monitor
    ├── xxx_slv_sequencer.sv # Slave sequencer
    ├── xxx_env_cfg.sv       # Environment config
    ├── xxx_env.sv           # Environment (dynamic instantiation)
    ├── xxx_seq_lib.sv       # Sequence library
    └── xxx_package.svp      # Package
```

**Total:** 15 template files (vs 10 in single-agent mode).

---

## 5. Key Template Designs

### 5.1 xxx_intf.sv — Shared Interface

Single interface with 4 clocking blocks: `cb_mst_drv`, `cb_mst_mon`, `cb_slv_drv`, `cb_slv_mon`.

```systemverilog
`ifndef {{ uvc_info.uvc_name.upper() }}_IF__SV
`define {{ uvc_info.uvc_name.upper() }}_IF__SV

interface {{ uvc_info.uvc_name }}_if (input logic clk, input logic mrst_n);
    logic [15:0] tmp_data;

    // Master clocking blocks
    clocking cb_mst_drv @(posedge clk);
        default input #1 output #1;
        output tmp_data;
    endclocking

    clocking cb_mst_mon @(posedge clk);
        default input #1 output #1;
        input tmp_data;
    endclocking

    // Slave clocking blocks
    clocking cb_slv_drv @(posedge clk);
        default input #1 output #1;
        output tmp_data;
    endclocking

    clocking cb_slv_mon @(posedge clk);
        default input #1 output #1;
        input tmp_data;
    endclocking

    task reset_driver_signal();
        tmp_data <= '0;
    endtask
endinterface

`endif
```

### 5.2 xxx_env_cfg.sv — Environment Configuration

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

### 5.3 xxx_env.sv — Environment

```systemverilog
`ifndef {{ uvc_info.uvc_name.upper() }}_ENV__SV
`define {{ uvc_info.uvc_name.upper() }}_ENV__SV

class {{ uvc_info.uvc_name }}_env extends uvm_env;
    `uvm_component_utils({{ uvc_info.uvc_name }}_env)

    {{ uvc_info.uvc_name }}_env_cfg  env_cfg;
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
    // Dynamic drv-sqr connections can be added here
    // Example: mst_agt[i].drv.seq_item_port.connect(mst_agt[i].sqr.seq_item_export);
endfunction

`endif //{{ uvc_info.uvc_name.upper() }}_ENV__SV
```

### 5.4 xxx_cfg.sv — Shared Agent Config

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
    endfunction
endclass

`endif //{{ uvc_info.uvc_name.upper() }}_CFG__SV
```

### 5.5 xxx_mst_agent.sv / xxx_slv_agent.sv

Master and slave agents have identical structure but different class names and use different clocking blocks. Template content is the same pattern as the single-agent `xxx_agent.sv`, with `mst_` or `slv_` prefix and corresponding clocking block references.

---

## 6. Python Code Changes

### 6.1 UvcInfo Dataclass

```python
@dataclass
class UvcInfo:
    uvc_name: str = ''
    version: str = ''
    mode: str = 'single'        # 'single' or 'mstslv'
    master_num: int = 1          # mstslv mode only
    slave_num: int = 1           # mstslv mode only
```

### 6.2 New CLI Arguments

In `get_input_args()`:
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

### 6.3 Template Directory Selection

In `init_para()`:
```python
if mode == 'mstslv':
    default_tpl = str(self.TEMPLATES_DIR / "default" / "xxx_uvc_mstslv")
else:
    default_tpl = str(self.TEMPLATES_DIR / "default" / "xxx_uvc")
```

### 6.4 Template Rendering Context

In `generate_uvc()`:
```python
uvc_info = UvcInfo(
    uvc_name=self.uvc_name,
    version=self.version,
    mode=self.mode,
    master_num=self.master_num,
    slave_num=self.slave_num
)
```

---

## 7. File Naming Convention

Template files use `xxx_` prefix which is replaced with `{uvc_name}_` during generation.

**Single mode:** `xxx_agent.sv` → `ahb_agent.sv`

**Mstslv mode:**
- `xxx_mst_agent.sv` → `ahb_mst_agent.sv`
- `xxx_slv_agent.sv` → `ahb_slv_agent.sv`
- `xxx_env.sv` → `ahb_env.sv`
- `xxx_env_cfg.sv` → `ahb_env_cfg.sv`

---

## 8. Backward Compatibility

- Default mode is `single`, existing behavior is unchanged
- Existing templates in `xxx_uvc/` are not modified
- `-t` parameter still works as override for both modes
- `UvcInfo.uvc_num` field is removed (dead code)

---

## 9. Testing Strategy

1. **Smoke test:** Generate a single-mode UVC, verify all files exist and contain correct class names
2. **Mstslv test:** Generate a mstslv-mode UVC, verify:
   - All 15 files generated
   - Class names use `mst_`/`slv_` prefix
   - `env_cfg` contains `master_num`/`slave_num`
   - `env` contains dynamic array declarations
   - Interface has 4 clocking blocks
3. **Edge cases:** `--mst-num 0`, `--slv-num 0`, `--mst-num 5`
