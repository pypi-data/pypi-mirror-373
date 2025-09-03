module always_module (input clk,
input rst_n,
input [7:0] data_in,
output reg [7:0] q,
output wire [7:0] data_doubled);
always_ff @(posedge clk, negedge rst_n) begin
if (!rst_n) begin
q <= 8'b0;
end
else begin
q <= data_in;
end
end
always_comb begin
data_doubled = data_in << 1;
end
endmodule