`ifndef {{ uvc_info.uvc_name.upper() }}_AGENT__SV
`define {{ uvc_info.uvc_name.upper() }}_AGENT__SV

class {{ uvc_info.uvc_name }}_agent extends uvm_agent;
    `uvm_component_utils({{ uvc_info.uvc_name }}_agent)

    {{ uvc_info.uvc_name }}_sequencer    sqr;
    {{ uvc_info.uvc_name }}_driver       drv;
    {{ uvc_info.uvc_name }}_monitor      mon;
    {{ uvc_info.uvc_name }}_config       cfg;

    function new(string name = "{{ uvc_info.uvc_name }}_agent", uvm_component parent = null);
        super.new(name, parent);
    endfunction: new

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);

        if(this.cfg == null)begin
            if(!uvm_config_db#({{ uvc_info.uvc_name }}_config)::get(this, "", "cfg", this.cfg))
                `uvm_fatal("cfg not set", {get_full_name(), ".cfg"})
        end
        if(cfg.en)begin
            this.is_active = cfg.is_active;

            if(!uvm_config_db#(virtual {{ uvc_info.uvc_name }}_if)::get(this, "", "vif", cfg.vif))  //vif
                `uvm_fatal("NOVIF", {"virtual interface must get for ", get_full_name(), ".cfg.vif"})

            if(this.is_active == UVM_ACTIVE)begin
                sqr = {{ uvc_info.uvc_name }}_sequencer::type_id::create("sqr", this);
                sqr.cfg=this.cfg;

                drv = {{ uvc_info.uvc_name }}_driver::type_id::create("drv",this);
                drv.cfg=this.cfg;
            end

            mon = {{ uvc_info.uvc_name }}_monitor::type_id::create("mon", this);
            mon.cfg=this.cfg;
        end
    endfunction: build_phase

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        if(cfg.en==1 && this.is_active == UVM_ACTIVE)begin
            drv.seq_item_port.connect(sqr.seq_item_export);
        end
    endfunction: connect_phase

endclass: {{ uvc_info.uvc_name }}_agent

`endif //{{ uvc_info.uvc_name.upper() }}_AGENT__SV