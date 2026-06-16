`ifndef {{ uvc_info.uvc_name.upper() }}_SLV_MONITOR__SV
`define {{ uvc_info.uvc_name.upper() }}_SLV_MONITOR__SV
class {{ uvc_info.uvc_name }}_slv_monitor extends uvm_monitor;
    `uvm_component_utils({{ uvc_info.uvc_name }}_slv_monitor)

    virtual interface {{ uvc_info.uvc_name }}_if vif;
    {{ uvc_info.uvc_name }}_cfg cfg;

    uvm_analysis_port#({{ uvc_info.uvc_name }}_transaction) broadcaster;

    extern function new(string name = "{{ uvc_info.uvc_name }}_slv_monitor", uvm_component parent = null);
    extern virtual function void build_phase(uvm_phase phase);
    extern virtual task run();
    extern virtual task rcv_data_phase();
endclass: {{ uvc_info.uvc_name }}_slv_monitor

function {{ uvc_info.uvc_name }}_slv_monitor::new(string name = "{{ uvc_info.uvc_name }}_slv_monitor", uvm_component parent = null);
    super.new (name, parent);
    broadcaster = new ("broadcaster", this);
endfunction: new

function void {{ uvc_info.uvc_name }}_slv_monitor::build_phase(uvm_phase phase);
    super.build_phase(phase);
    vif=cfg.vif;
endfunction: build_phase

task {{ uvc_info.uvc_name }}_slv_monitor::run();
    fork begin //guard fork
        forever begin
            fork
                begin
                    @(posedge vif.mrst_n);
                    rcv_data_phase();
                end
                begin
                    @(negedge vif.mrst_n);
                end
            join_any
            disable fork;
        end
    end join //guard fork
endtask: run

task {{ uvc_info.uvc_name }}_slv_monitor::rcv_data_phase();
    fork
        //add monitor behavior here
    join
endtask: rcv_data_phase

`endif //{{ uvc_info.uvc_name.upper() }}_SLV_MONITOR__SV
