`ifndef {{ uvc_info.uvc_name.upper() }}_DRIVER__SV
`define {{ uvc_info.uvc_name.upper() }}_DRIVER__SV
class {{ uvc_info.uvc_name }}_driver extends uvm_driver#({{ uvc_info.uvc_name }}_transaction);
    `uvm_component_utils({{ uvc_info.uvc_name }}_driver)

    virtual interface {{ uvc_info.uvc_name }}_if vif;
    {{ uvc_info.uvc_name }}_config cfg;

    extern function new(string name = "{{ uvc_info.uvc_name }}_driver", uvm_component parent = null);
    extern virtual function void build_phase(uvm_phase phase);
    extern virtual protected task get_and_drive();
    extern virtual protected task drive_trans({{ uvc_info.uvc_name }}_transaction trans);
    extern virtual task run();
endclass: {{ uvc_info.uvc_name }}_driver

function {{ uvc_info.uvc_name }}_driver::new(string name = "{{ uvc_info.uvc_name }}_driver", uvm_component parent = null);
    super.new(name,parent);
endfunction: new

function void {{ uvc_info.uvc_name }}_driver::build_phase(uvm_phase phase);
    super.build_phase(phase);
    vif=cfg.vif;
endfunction: build_phase

task {{ uvc_info.uvc_name }}_driver::run();
    fork begin //gurad fork
        forever begin
            fork
                begin
                    @(posedge vif.mrst_n);
                    vif.reset_driver_signal();
                    get_and_drive();
                end
                begin
                    @(negedge vif.mrst_n);
                end
            join_any
            disable fork;
        end
    end join //gurad fork
endtask: run

task {{ uvc_info.uvc_name }}_driver::get_and_drive();
    forever begin
        seq_item_port.get_next_item(req);
        drive_trans(req);
        seq_item_port.item_done();
    end
endtask:get_and_drive

task {{ uvc_info.uvc_name }}_driver::drive_trans({{ uvc_info.uvc_name }}_transaction trans);
    if(trans.e_{{ uvc_info.uvc_name }}_cmd == {{uvc_info.uvc_name}}_transaction::IDLE) begin
        @(vif.cb_drv);
        vif.cb_drv.tmp_data <= trans.tmp_data;
    end
endtask

`endif //{{ uvc_info.uvc_name.upper() }}_DRIVER__SV