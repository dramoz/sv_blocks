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
    output logic [$clog2(WL+1)-1:0] count
);

always_comb begin : count_ones_comb
    count = 'b0;
    for(int inx=0; inx < WL; inx=inx+1) begin
        count = count + din[inx];
    end
end

endmodule
