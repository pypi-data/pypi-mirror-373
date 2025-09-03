module param_module #(parameter WIDTH = 8,
parameter DEPTH = 16) (input clk,
input wire [7:0] data_in,
output reg [7:0] data_out,
inout wire [3:0] bidir_port);
endmodule