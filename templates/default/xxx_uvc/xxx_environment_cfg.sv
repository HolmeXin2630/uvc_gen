`ifndef {{ uvc_info.uvc_name.upper() }}_ENVIRONMENT_CFG__SV
`define {{ uvc_info.uvc_name.upper() }}_ENVIRONMENT_CFG__SV

class {{ uvc_info.uvc_name }}_environment_cfg extends uvm_object;
    `uvm_object_utils({{ uvc_info.uvc_name }}_environment_cfg)

    int agent_num = {{ uvc_info.agent_num }};
    {{ uvc_info.uvc_name }}_config agt_cfg[];

    function new(string name = "{{ uvc_info.uvc_name }}_environment_cfg");
        super.new(name);
    endfunction

    function void build();
        agt_cfg = new[agent_num];
        foreach (agt_cfg[i])
            agt_cfg[i] = {{ uvc_info.uvc_name }}_config::type_id::create($sformatf("agt_cfg[%0d]", i));
    endfunction
endclass

`endif //{{ uvc_info.uvc_name.upper() }}_ENVIRONMENT_CFG__SV
