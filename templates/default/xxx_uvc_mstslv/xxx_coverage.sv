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
