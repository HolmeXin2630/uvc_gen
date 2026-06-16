`ifndef {{ uvc_info.uvc_name.upper() }}_MONITOR__SV
`define {{ uvc_info.uvc_name.upper() }}_MONITOR__SV
class {{ uvc_info.uvc_name }}_monitor extends uvm_monitor;
    `uvm_component_utils({{ uvc_info.uvc_name }}_monitor)

    virtual interface {{ uvc_info.uvc_name }}_if vif;
    {{ uvc_info.uvc_name }}_config cfg;

    uvm_analysis_port#({{ uvc_info.uvc_name }}_transaction) broadcaster;

    extern function new(string name = "{{ uvc_info.uvc_name }}_monitor", uvm_component parent = null);
    extern virtual function void build_phase(uvm_phase phase);
    extern virtual task run();
    extern virtual task rcv_data_phase();
endclass: {{ uvc_info.uvc_name }}_monitor

function {{ uvc_info.uvc_name }}_monitor::new(string name = "{{ uvc_info.uvc_name }}_monitor", uvm_component parent = null);
    super.new (name, parent);
    broadcaster = new ("broadcaster", this);
endfunction: new

function void {{ uvc_info.uvc_name }}_monitor::build_phase(uvm_phase phase);
    super.build_phase(phase);
    vif=cfg.vif;
endfunction: build_phase

task {{ uvc_info.uvc_name }}_monitor::run();
    fork begin //gurad fork
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
    end join //gurad fork
endtask: run

task {{ uvc_info.uvc_name }}_monitor::rcv_data_phase();
    fork
        //add monitor behavior here

        //example:
        //while(1)begin
        //    //@(vif.xxx_flag);
        //    //begin
        //        //{{ uvc_info.uvc_name }}_transaction {{ uvc_info.uvc_name }}_trans;
        //        //{{ uvc_info.uvc_name }}_trans = new("tmp_trans");
        //        //@(vif.cb_mon);
        //        //{{ uvc_info.uvc_name }}_trans.tmp_data = vif.cb_mon.tmp_data;
        //    //end
        //end
    join
endtask: rcv_data_phase

`endif //{{ uvc_info.uvc_name.upper() }}_MONITOR__SV