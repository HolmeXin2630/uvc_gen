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
