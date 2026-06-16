`ifndef {{ uvc_info.uvc_name.upper() }}_ENVIRONMENT__SV
`define {{ uvc_info.uvc_name.upper() }}_ENVIRONMENT__SV

class {{ uvc_info.uvc_name }}_environment extends uvm_env;
    `uvm_component_utils({{ uvc_info.uvc_name }}_environment)

    {{ uvc_info.uvc_name }}_agent    agt;
    {{ uvc_info.uvc_name }}_config   cfg;

    //`uvm_component_utils_begin({{ uvc_info.uvc_name }}_environment)
    //`uvm_field_object(cfg, UVM_DEFAULT| UVM_REFERENCE)
    //`uvm_component_utils_end

    extern function new(string name="{{ uvc_info.uvc_name }}_environment", uvm_component parent=null);
    extern virtual function void build_phase(uvm_phase phase);
    extern virtual function void connect_phase(uvm_phase phase);

endclass: {{ uvc_info.uvc_name }}_environment

function {{ uvc_info.uvc_name }}_environment::new(string name= "{{ uvc_info.uvc_name }}_environment", uvm_component parent=null);
    super.new(name,parent);
endfunction: new

function void {{ uvc_info.uvc_name }}_environment::build_phase(uvm_phase phase);
    super.build_phase(phase);
    //cfg gotted through 'UVM_REFERENCE'
    //uvm_config_db#(uvm_object)::set(this, "agt", "cfg", cfg);
    agt = {{ uvc_info.uvc_name }}_agent::type_id::create("agt",this);
    agt.cfg = this.cfg;
endfunction: build_phase

function void {{ uvc_info.uvc_name }}_environment::connect_phase(uvm_phase phase);
    super.connect_phase(phase);
endfunction: connect_phase

`endif // TMP_DFT2TX_ENVIRONMENT__SV