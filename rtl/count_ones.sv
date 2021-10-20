/*!
@copyright Copyright (c) 2021 Danilo Ramos
           All rights reserved.
#  This license message must appear in all versions of this code including
#  modified versions.
#  BSD 3-Clause
####################################################################################
#  Overview:
"""
count ones
*/

module count_ones
#(
    parameter WL = 32
)
(
    input  wire [WL-1:0]           din,
    output wire [$clog2(WL+1)-1:0] count_ones
)

always_comb begin : count_ones
    count_ones = 'b0;
    for(int inx=0; inx < WL; inx=inx+1) begin
        count_ones = count_ones + din[inx];
    end
end

endmodule