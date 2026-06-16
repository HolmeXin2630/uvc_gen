`ifndef {{ uvc_info.uvc_name.upper() }}_TRANSACTION__SV
`define {{ uvc_info.uvc_name.upper() }}_TRANSACTION__SV

class {{ uvc_info.uvc_name }}_transaction extends uvm_sequence_item;

    typedef enum {IDLE, PARA} {{ uvc_info.uvc_name }}_cmd_enum;
    rand {{ uvc_info.uvc_name }}_cmd_enum     e_{{ uvc_info.uvc_name }}_cmd;
    rand bit[15:0] tmp_data;

    `uvm_object_utils_begin({{ uvc_info.uvc_name }}_transaction)
        `uvm_field_enum({{ uvc_info.uvc_name }}_cmd_enum, e_{{uvc_info.uvc_name}}_cmd, UVM_DEFAULT)
        `uvm_field_int(tmp_data, UVM_DEFAULT)
    `uvm_object_utils_end

    function new(string name = "{{ uvc_info.uvc_name }}_transaction");
        super.new(name);
    endfunction: new

endclass

`endif //{{ uvc_info.uvc_name.upper() }}_TRANSACTION__SV
