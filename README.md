# UVC Generator (uvc_gen)

UVM Verification Component 代码生成工具，用于自动生成符合 UVM 方法学的验证组件代码框架。

## 功能特性

- 支持 **single** 模式：生成单 agent 的标准 UVC
- 支持 **mstslv** 模式：生成 master/slave 多 agent 的 UVC，支持动态数组实例化
- 支持 **多 agent 实例化**：`--agent-num` 参数生成同类型 agent 动态数组
- 支持 **可选组件**：coverage、scoreboard、ref_model 按需启用
- 基于 Jinja2 模板引擎，可自定义模板
- 自动生成文件名前缀替换（`xxx_` → `{uvc_name}_`）
- 自动创建版本符号链接（`latest` → `{version}`）

## 命令行用法

### 基本语法

```bash
python3 uvc_gen.py [OPTIONS]
```

### 参数说明

| 参数 | 缩写 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--uvc_name` | `-n` | ✅ | - | UVC 名称（如 `ahb`, `spi`, `axi`） |
| `--mode` | `-m` | ❌ | `single` | 生成模式：`single` 或 `mstslv` |
| `--version` | `-v` | ❌ | `v1.0` | UVC 版本号 |
| `--output` | `-o` | ❌ | 当前目录 | 输出目录路径 |
| `--tpl_dir` | `-t` | ❌ | 自动选择 | 模板目录路径 |
| `--agent-num` | - | ❌ | `1` | 同类型 agent 数量（single 模式） |
| `--mst-num` | - | ❌ | `1` | Master agent 数量（mstslv 模式） |
| `--slv-num` | - | ❌ | `1` | Slave agent 数量（mstslv 模式） |
| `--with-env` | - | ❌ | `False` | 启用 env/env_cfg 组件 |
| `--with-coverage` | - | ❌ | `False` | 启用覆盖率收集器 |
| `--with-scoreboard` | - | ❌ | `False` | 启用记分板 |
| `--with-ref-model` | - | ❌ | `False` | 启用参考模型 |

> **注意：** `--agent-num >= 2` 时会自动启用 `--with-env`（多 agent 需要 env_cfg）。

### 使用示例

#### 1. Single 模式（默认）

```bash
# 生成 AHB 单 agent UVC
python3 uvc_gen.py -n ahb -o ./output

# 生成 SPI UVC，指定版本
python3 uvc_gen.py -n spi -v v2.0 -o ./output
```

#### 2. 多 Agent 实例化

```bash
# 生成 3 个同类型 agent（自动启用 env）
python3 uvc_gen.py -n ahb --agent-num 3 -o ./output

# 生成 2 个 agent + 可选组件
python3 uvc_gen.py -n ahb --agent-num 2 --with-env --with-coverage --with-scoreboard -o ./output
```

#### 3. 可选组件

```bash
# 启用覆盖率收集器
python3 uvc_gen.py -n ahb --with-coverage -o ./output

# 启用所有可选组件
python3 uvc_gen.py -n ahb --with-env --with-coverage --with-scoreboard --with-ref-model -o ./output
```

**生成文件列表（10个）：**
```
output/ahb_uvc/v1.0/
├── ahb_agent.sv
├── ahb_config.sv
├── ahb_driver.sv
├── ahb_environment.sv
├── ahb_intf.sv
├── ahb_monitor.sv
├── ahb_package.svp
├── ahb_seq_lib.sv
├── ahb_sequencer.sv
└── ahb_transaction.sv
```

#### 2. Master/Slave 模式

```bash
# 生成 AHB master/slave UVC（默认 1 master + 1 slave）
python3 uvc_gen.py -n ahb -m mstslv -o ./output

# 生成 2 master + 3 slave 的 UVC
python3 uvc_gen.py -n axi -m mstslv --mst-num 2 --slv-num 3 -o ./output
```

**生成文件列表（15个）：**
```
output/ahb_uvc/v1.0/
├── ahb_cfg.sv              # Agent 配置类
├── ahb_env.sv              # 环境类（含动态 agent 数组）
├── ahb_env_cfg.sv          # 环境配置类（master_num, slave_num）
├── ahb_intf.sv             # 接口（4 个 clocking block）
├── ahb_mst_agent.sv        # Master agent
├── ahb_mst_driver.sv       # Master driver（使用 cb_mst_drv）
├── ahb_mst_monitor.sv      # Master monitor（使用 cb_mst_mon）
├── ahb_mst_sequencer.sv    # Master sequencer
├── ahb_package.svp         # 包文件
├── ahb_seq_lib.sv          # 序列库（mst + slv base sequence）
├── ahb_slv_agent.sv        # Slave agent
├── ahb_slv_driver.sv       # Slave driver（使用 cb_slv_drv）
├── ahb_slv_monitor.sv      # Slave monitor（使用 cb_slv_mon）
├── ahb_slv_sequencer.sv    # Slave sequencer
└── ahb_transaction.sv      # 事务类
```

## Python API 调用

### 直接调用脚本

```python
import subprocess

def generate_uvc(uvc_name, mode="single", version="v1.0", output="./output",
                 mst_num=1, slv_num=1, agent_num=1,
                 with_env=False, with_coverage=False,
                 with_scoreboard=False, with_ref_model=False):
    """调用 uvc_gen 生成 UVC"""
    cmd = [
        "python3", "uvc_gen.py",
        "-n", uvc_name,
        "-m", mode,
        "-v", version,
        "-o", output
    ]

    if mode == "mstslv":
        cmd.extend(["--mst-num", str(mst_num), "--slv-num", str(slv_num)])
    else:
        cmd.extend(["--agent-num", str(agent_num)])

    if with_env: cmd.append("--with-env")
    if with_coverage: cmd.append("--with-coverage")
    if with_scoreboard: cmd.append("--with-scoreboard")
    if with_ref_model: cmd.append("--with-ref-model")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"uvc_gen failed: {result.stderr}")
    return result.stdout

# 使用示例
generate_uvc("ahb", mode="mstslv", mst_num=2, slv_num=1)
generate_uvc("ahb", agent_num=3, with_env=True, with_coverage=True)
```

### 模块导入调用

```python
from uvc_gen import UvcGen, UvcInfo, build_parser

# 简单调用（推荐）
gen = UvcGen()
gen.init_para(gen.DEFAULT_TPL, "ahb", "v1.0", "./output")
gen.parse_tpl_dir()
gen.generate_uvc()

# 完整参数
gen = UvcGen()
gen.init_para(
    tpl_dir=gen.DEFAULT_TPL,
    uvc_name="ahb",
    version="v1.0",
    output="./output",
    mode="single",
    agent_num=3,
    with_env=True,
    with_coverage=True
)
gen.parse_tpl_dir()
gen.generate_uvc()

# 访问 UvcInfo（单一数据源）
print(gen.info.uvc_name)    # "ahb"
print(gen.info.agent_num)   # 3
print(gen.with_env)         # True（属性别名，兼容旧代码）

# CLI 参数解析（测试友好，无需 mock sys.argv）
parser = build_parser()
args = parser.parse_args(['-n', 'ahb', '--with-env', '--agent-num', '3'])
```

## 模板变量

模板中可使用 `uvc_info` 对象，包含以下属性：

| 属性 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `uvc_info.uvc_name` | `str` | UVC 名称 | `"ahb"` |
| `uvc_info.version` | `str` | 版本号 | `"v1.0"` |
| `uvc_info.mode` | `str` | 生成模式 | `"single"` / `"mstslv"` |
| `uvc_info.master_num` | `int` | Master 数量 | `2` |
| `uvc_info.slave_num` | `int` | Slave 数量 | `3` |
| `uvc_info.agent_num` | `int` | 同类型 agent 数量 | `3` |
| `uvc_info.with_env` | `bool` | 是否启用 env | `True` / `False` |
| `uvc_info.with_coverage` | `bool` | 是否启用 coverage | `True` / `False` |
| `uvc_info.with_scoreboard` | `bool` | 是否启用 scoreboard | `True` / `False` |
| `uvc_info.with_ref_model` | `bool` | 是否启用 ref_model | `True` / `False` |

### 模板示例

```systemverilog
// 使用 uvc_info.uvc_name 生成类名
class {{ uvc_info.uvc_name }}_driver extends uvm_driver;
    `uvm_component_utils({{ uvc_info.uvc_name }}_driver)

    // 使用 uvc_info.uvc_name 生成接口名
    virtual interface {{ uvc_info.uvc_name }}_if vif;

    function new(string name = "{{ uvc_info.uvc_name }}_driver", uvm_component parent = null);
        super.new(name, parent);
    endfunction
endclass
```

## 模板目录结构

```
templates/
└── default/
    ├── xxx_uvc/                # Single 模式模板
    │   ├── xxx_agent.sv
    │   ├── xxx_config.sv
    │   ├── xxx_coverage.sv     # 可选组件
    │   ├── xxx_driver.sv
    │   ├── xxx_environment.sv
    │   ├── xxx_environment_cfg.sv  # 多 agent 时使用
    │   ├── xxx_intf.sv
    │   ├── xxx_monitor.sv
    │   ├── xxx_package.svp
    │   ├── xxx_ref_model.sv    # 可选组件
    │   ├── xxx_scoreboard.sv   # 可选组件
    │   ├── xxx_seq_lib.sv
    │   ├── xxx_sequencer.sv
    │   └── xxx_transaction.sv
    └── xxx_uvc_mstslv/         # Master/Slave 模式模板
        ├── xxx_cfg.sv
        ├── xxx_coverage.sv     # 可选组件
        ├── xxx_env.sv
        ├── xxx_env_cfg.sv
        ├── xxx_intf.sv
        ├── xxx_mst_agent.sv
        ├── xxx_mst_driver.sv
        ├── xxx_mst_monitor.sv
        ├── xxx_mst_sequencer.sv
        ├── xxx_package.svp
        ├── xxx_ref_model.sv    # 可选组件
        ├── xxx_scoreboard.sv   # 可选组件
        ├── xxx_seq_lib.sv
        ├── xxx_slv_agent.sv
        ├── xxx_slv_driver.sv
        ├── xxx_slv_monitor.sv
        ├── xxx_slv_sequencer.sv
        └── xxx_transaction.sv
```

## 自定义模板

1. 复制现有模板目录：
   ```bash
   cp -r templates/default/xxx_uvc templates/default/my_custom_uvc
   ```

2. 修改模板文件中的 Jinja2 变量

3. 使用自定义模板生成：
   ```bash
   python3 uvc_gen.py -n ahb -t my_custom_uvc -o ./output
   ```

## mstslv 模式关键特性

### 接口时钟块

```systemverilog
// xxx_intf.sv 自动生成 4 个 clocking block
clocking cb_mst_drv @(posedge mclk);  // Master driver
clocking cb_mst_mon @(posedge mclk);  // Master monitor
clocking cb_slv_drv @(posedge mclk);  // Slave driver
clocking cb_slv_mon @(posedge mclk);  // Slave monitor
```

### 环境动态数组

```systemverilog
// xxx_env.sv 自动生成动态 agent 数组
class {{ uvc_info.uvc_name }}_env extends uvm_env;
    {{ uvc_info.uvc_name }}_mst_agent mst_agt[];  // Master agent 数组
    {{ uvc_info.uvc_name }}_slv_agent slv_agt[];  // Slave agent 数组

    function void build_phase(uvm_phase phase);
        mst_agt = new[env_cfg.master_num];
        slv_agt = new[env_cfg.slave_num];
        // 自动实例化...
    endfunction
endclass
```

### 环境配置

```systemverilog
// xxx_env_cfg.sv 包含 master/slave 数量配置
class {{ uvc_info.uvc_name }}_env_cfg extends uvm_object;
    int master_num = 1;
    int slave_num  = 1;

    {{ uvc_info.uvc_name }}_cfg mst_cfg[];  // Master 配置数组
    {{ uvc_info.uvc_name }}_cfg slv_cfg[];  // Slave 配置数组
endclass
```

## 测试

```bash
# 运行所有测试
.venv/bin/pytest tests/ -v

# 运行 VCS 编译验证（需要 VCS 环境）
bash tests/test_vcs_compile.sh
```

## 依赖

- Python 3.8+
- Jinja2
- Rich

## 许可证

Internal use only.
