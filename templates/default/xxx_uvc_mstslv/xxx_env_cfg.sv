`ifndef {{ uvc_info.uvc_name.upper() }}_ENV_CFG__SV
`define {{ uvc_info.uvc_name.upper() }}_ENV_CFG__SV

class {{ uvc_info.uvc_name }}_env_cfg extends uvm_object;
    `uvm_object_utils({{ uvc_info.uvc_name }}_env_cfg)

    int master_num = 1;
    int slave_num  = 1;

    {{ uvc_info.uvc_name }}_cfg mst_cfg[];
    {{ uvc_info.uvc_name }}_cfg slv_cfg[];

    function new(string name = "{{ uvc_info.uvc_name }}_env_cfg");
        super.new(name);
    endfunction

    function void build();
        mst_cfg = new[master_num];
        slv_cfg = new[slave_num];
        foreach (mst_cfg[i]) mst_cfg[i] = {{ uvc_info.uvc_name }}_cfg::type_id::create($sformatf("mst_cfg[%0d]", i));
        foreach (slv_cfg[i]) slv_cfg[i] = {{ uvc_info.uvc_name }}_cfg::type_id::create($sformatf("slv_cfg[%0d]", i));
    endfunction
endclass

`endif //{{ uvc_info.uvc_name.upper() }}_ENV_CFG__SV
