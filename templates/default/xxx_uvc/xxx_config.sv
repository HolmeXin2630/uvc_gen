`ifndef {{ uvc_info.uvc_name.upper() }}_CONFIG__SV
`define {{ uvc_info.uvc_name.upper() }}_CONFIG__SV

class {{ uvc_info.uvc_name }}_config extends uvm_object;
    `uvm_object_utils({{ uvc_info.uvc_name }}_config)

    uvm_active_passive_enum is_active = UVM_ACTIVE;
    bit en = 1;

    virtual interface {{ uvc_info.uvc_name }}_if vif;
    //add agent_ctrl vars here

    //`uvm_object_utils_begin({{ uvc_info.uvc_name }}_config)
    //`uvm_field_enum(uvm_active_passive_enum, is_active,UVM_DEFAULT)
    //`uvm_object_utils_end

    function new(string name = "{{ uvc_info.uvc_name }}_config");
        super.new(name);
    endfunction: new

endclass : {{ uvc_info.uvc_name }}_config

`endif //{{ uvc_info.uvc_name }}_CONFIG__SV