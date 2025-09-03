module complex_module #(parameter DATA_WIDTH = 32,
parameter ADDR_WIDTH = 10) (input clk,
input rst_n,
input wr_en,
input rd_en,
input [ADDR_WIDTH-1:0] addr,
input [DATA_WIDTH-1:0] wr_data,
output reg [DATA_WIDTH-1:0] rd_data,
output reg ready);
wire mem_select;
reg [1:0] state;
reg [DATA_WIDTH-1:0] memory[2**ADDR_WIDTH-1:0];

// State machine
always_ff @(posedge clk, negedge rst_n) begin
if (!rst_n) begin
state <= 2'b00;
ready <= 1'b0;
end
else begin
case (state)
                                2'b00: begin
                                    if (wr_en) state <= 2'b01;
                                    else if (rd_en) state <= 2'b10;
                                end
                                2'b01: begin // Write state
                                    memory[addr] <= wr_data;
                                    ready <= 1'b1;
                                    state <= 2'b00;
                                end
                                2'b10: begin // Read state
                                    rd_data <= memory[addr];
                                    ready <= 1'b1;
                                    state <= 2'b00;
                                end
                                endcase
end
end

// Combinational logic
always_comb begin
mem_select = wr_en | rd_en;
end
endmodule