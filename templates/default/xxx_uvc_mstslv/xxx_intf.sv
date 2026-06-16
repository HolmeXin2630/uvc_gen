`ifndef {{ uvc_info.uvc_name.upper() }}_IF__SV
`define {{ uvc_info.uvc_name.upper() }}_IF__SV

interface {{ uvc_info.uvc_name }}_if(input mclk, input mrst_n);
    parameter HOLD_TIME=1;
    parameter SETUP_TIME=1;

    logic [15:0]    tmp_data;

    task reset_driver_signal();
        tmp_data <= 0;
    endtask

    // Master clocking blocks
    clocking cb_mst_drv @(posedge mclk);
        default input #SETUP_TIME output #HOLD_TIME;
        output tmp_data;
    endclocking

    clocking cb_mst_mon @(posedge mclk);
        default input #SETUP_TIME output #HOLD_TIME;
        input tmp_data;
    endclocking

    // Slave clocking blocks
    clocking cb_slv_drv @(posedge mclk);
        default input #SETUP_TIME output #HOLD_TIME;
        output tmp_data;
    endclocking

    clocking cb_slv_mon @(posedge mclk);
        default input #SETUP_TIME output #HOLD_TIME;
        input tmp_data;
    endclocking

endinterface

`endif//{{ uvc_info.uvc_name.upper() }}_IF__SV
