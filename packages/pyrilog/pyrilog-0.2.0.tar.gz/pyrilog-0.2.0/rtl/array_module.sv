module array_module (input clk,
output [31:0] data_out[1:0][1:0]);
wire [7:0] mem[15:0][3:0];
reg buffer[7:0];
reg [3:0] single_array[9:0];
endmodule