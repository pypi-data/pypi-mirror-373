module top_module (input clk,
input [7:0] data_in,
output wire [7:0] data_out);
memory_module #(
    .WIDTH(8),
    .DEPTH(256)
)
mem_inst (
    .clk(clk),
    .addr(addr),
    .data_in(data_in),
    .data_out(data_out)
);
endmodule