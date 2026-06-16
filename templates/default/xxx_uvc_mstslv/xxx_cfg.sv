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
