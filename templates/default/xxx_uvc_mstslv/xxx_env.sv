`ifndef {{ uvc_info.uvc_name.upper() }}_ENV__SV
`define {{ uvc_info.uvc_name.upper() }}_ENV__SV

class {{ uvc_info.uvc_name }}_env extends uvm_env;
    `uvm_component_utils({{ uvc_info.uvc_name }}_env)

    {{ uvc_info.uvc_name }}_env_cfg   env_cfg;
    {{ uvc_info.uvc_name }}_mst_agent mst_agt[];
    {{ uvc_info.uvc_name }}_slv_agent slv_agt[];

    extern function new(string name="{{ uvc_info.uvc_name }}_env", uvm_component parent=null);
    extern virtual function void build_phase(uvm_phase phase);
    extern virtual function void connect_phase(uvm_phase phase);
endclass

function {{ uvc_info.uvc_name }}_env::new(string name="{{ uvc_info.uvc_name }}_env", uvm_component parent=null);
    super.new(name, parent);
endfunction

function void {{ uvc_info.uvc_name }}_env::build_phase(uvm_phase phase);
    super.build_phase(phase);

    mst_agt = new[env_cfg.master_num];
    slv_agt = new[env_cfg.slave_num];

    foreach (mst_agt[i]) begin
        mst_agt[i] = {{ uvc_info.uvc_name }}_mst_agent::type_id::create(
            $sformatf("mst_agt[%0d]", i), this);
        mst_agt[i].cfg = env_cfg.mst_cfg[i];
    end

    foreach (slv_agt[i]) begin
        slv_agt[i] = {{ uvc_info.uvc_name }}_slv_agent::type_id::create(
            $sformatf("slv_agt[%0d]", i), this);
        slv_agt[i].cfg = env_cfg.slv_cfg[i];
    end
endfunction

function void {{ uvc_info.uvc_name }}_env::connect_phase(uvm_phase phase);
    super.connect_phase(phase);
endfunction

`endif //{{ uvc_info.uvc_name.upper() }}_ENV__SV
