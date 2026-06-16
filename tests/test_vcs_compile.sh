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
\`timescale 1ns/1ps

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
