module case_module (input clk,
input rst_n,
input [2:0] opcode,
input [7:0] data_a,
input [7:0] data_b,
output reg [7:0] result,
output reg valid);
always_ff @(posedge clk, negedge rst_n) begin
if (!rst_n) begin
result <= 8'b0;
valid <= 1'b0;
end
else begin
case (opcode)
3'b000: result <= data_a + data_b;
3'b001: result <= data_a - data_b;
3'b010: begin
result <= data_a & data_b;
valid <= 1'b1;
end
3'b011: begin
result <= data_a | data_b;
valid <= 1'b1;
end
default: result <= 8'b0;
endcase
valid <= 1'b1;
end
end
endmodule