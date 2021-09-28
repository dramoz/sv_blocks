////////////////////////////////////////////////////////////////////////////////
/// @author: Danilo Ramos
/// @copyrightCopyright (c) 2021. Danilo Ramos
/// All rights reserved
/// 
/// @license Licensed under the BSD 3-Clause license.
/// This license message must appear in all versions of this code including
/// modified versions.
///
/// @brief Simple SV multipier for examples aid
/// 
/// product = multiplier * multiplicand
/// 
////////////////////////////////////////////////////////////////////////////////

module dummy_multiplier
#(
    parameter WL = 32,
    parameter DONE_PIPE_LVL = 4
)
(
    input wire clk,
    input wire reset,
    
    // Inputs
    input wire          start,
    input wire [WL-1:0] multiplier,
    input wire [WL-1:0] multiplicand,
    
    // Outputs
    output wire done,
    output wire [2*WL-1:0] product
);

    logic [DONE_PIPE_LVL-1:0] done_dummy_pipe;
    logic          [2*WL-1:0] product_dummy_pipe[DONE_PIPE_LVL];

    always_ff @(posedge clk) begin : tx_block
        if(reset) begin
            done_dummy_pipe <= '0;
            
        end else begin
            product_dummy_pipe[0] <= multiplier * multiplicand;
            if(start == 1'b1) begin
                done_dummy_pipe[0] <= 1'b1;
                
            end else begin
                done_dummy_pipe[0] <= 1'b0;
                
            end
        end
    end
    
    assign done = done_dummy_pipe[DONE_PIPE_LVL-1];
    assign product = product_dummy_pipe[DONE_PIPE_LVL-1];
endmodule
