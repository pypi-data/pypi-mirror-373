module assign_module (input [7:0] a,
input [7:0] b,
output wire [8:0] sum);
wire [7:0] internal[3:0];
assign sum = a + b;
assign internal[0] = a;
assign internal[1] = b;
endmodule