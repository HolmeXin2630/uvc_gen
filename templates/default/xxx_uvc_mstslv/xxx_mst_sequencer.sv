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
