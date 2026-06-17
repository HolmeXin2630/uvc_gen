`ifndef {{ uvc_info.uvc_name.upper() }}_SCOREBOARD__SV
`define {{ uvc_info.uvc_name.upper() }}_SCOREBOARD__SV

class {{ uvc_info.uvc_name }}_scoreboard extends uvm_component;
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
