`ifndef {{ uvc_info.uvc_name.upper() }}_INTF__SV
`define {{ uvc_info.uvc_name.upper() }}_INTF__SV

interface {{ uvc_info.uvc_name }}_if(input mclk, input mrst_n);
    parameter HOLD_TIME=1; //1 ns
    parameter SETUP_TIME=1; //1 ns

    logic [15:0]    tmp_data;

    task reset_driver_signal();
        tmp_data <= 0;
    endtask

    clocking cb_drv @(posedge mclk);
        default input #SETUP_TIME output #HOLD_TIME;
        output tmp_data;
    endclocking

    clocking cb_mon @(posedge mclk);
        default input #SETUP_TIME output #HOLD_TIME;
        input tmp_data;
    endclocking

endinterface

`endif