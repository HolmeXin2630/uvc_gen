`ifndef {{ uvc_info.uvc_name.upper() }}_SEQ_LIB__SV
`define {{ uvc_info.uvc_name.upper() }}_SEQ_LIB__SV

class {{ uvc_info.uvc_name }}_mst_base_seq extends uvm_sequence #({{ uvc_info.uvc_name }}_transaction);
    `uvm_declare_p_sequencer({{ uvc_info.uvc_name }}_mst_sequencer)
    `uvm_object_utils({{ uvc_info.uvc_name }}_mst_base_seq)

    function new(string name = "{{ uvc_info.uvc_name }}_mst_base_seq");
        super.new(name);
    endfunction: new

    virtual task body();
    endtask: body

    virtual task template_task(bit[15:0] send_data);
        `uvm_do_with(req,{
            req.e_{{ uvc_info.uvc_name }}_cmd == {{ uvc_info.uvc_name }}_transaction::IDLE;
            req.tmp_data == send_data;
        })
    endtask

endclass:{{ uvc_info.uvc_name }}_mst_base_seq

class {{ uvc_info.uvc_name }}_slv_base_seq extends uvm_sequence #({{ uvc_info.uvc_name }}_transaction);
    `uvm_declare_p_sequencer({{ uvc_info.uvc_name }}_slv_sequencer)
    `uvm_object_utils({{ uvc_info.uvc_name }}_slv_base_seq)

    function new(string name = "{{ uvc_info.uvc_name }}_slv_base_seq");
        super.new(name);
    endfunction: new

    virtual task body();
    endtask: body

    virtual task template_task(bit[15:0] send_data);
        `uvm_do_with(req,{
            req.e_{{ uvc_info.uvc_name }}_cmd == {{ uvc_info.uvc_name }}_transaction::IDLE;
            req.tmp_data == send_data;
        })
    endtask

endclass:{{ uvc_info.uvc_name }}_slv_base_seq

`endif //{{ uvc_info.uvc_name.upper() }}_SEQ_LIB__SV
