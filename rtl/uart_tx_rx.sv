// Simple UART
module uart_tx_rx
#(
    parameter BAUD_RATE=115200,
    parameter CLK_FREQUENCY=48000000,
    parameter DATA_BITS = 8
)
(
    input wire clk,
    input wire reset,
    
    // TX port
    output logic tx_rdy,
    input  wire tx_vld,
    input  wire [DATA_BITS-1:0] tx_data,
    output logic tx_uart,
    
    // RX port
    input  wire rx_rdy,
    output logic rx_valid,
    output logic [DATA_BITS-1:0] rx_data,
    input  logic rx_uart,
    
    // Errors
    output tx_err,
    output rx_err
);

localparam rcalc_CLKS_PER_BIT = $rtoi($ceil(CLK_FREQUENCY/BAUD_RATE));
localparam CLKS_PER_BIT_WL = $clog2(rcalc_CLKS_PER_BIT);
localparam CLKS_PER_BIT = rcalc_CLKS_PER_BIT[CLKS_PER_BIT_WL-1:0];

localparam TOTAL_BITS = 1 + DATA_BITS + 1;  // [START=0|DATA[0->T.BITS]|STOP=1]
localparam TOTAL_BITS_WL = $clog2(TOTAL_BITS);

// --------------------------------------------------------------------------------
logic [CLKS_PER_BIT_WL-1:0] tx_bit_baudrate;
logic   [TOTAL_BITS_WL-1:0] tx_bit_count;
logic      [TOTAL_BITS-1:0] tx_data_buff;

enum {TX_IDLE, TX_DATA_SEND} tx_fsm;
always_ff @(posedge clk) begin : tx_block
    if(reset) begin
        tx_rdy  <= 1'b1;
        tx_uart <= 1'b1;
        tx_fsm  <= TX_IDLE;
        
        tx_err <= 1'b0;
        
    end else begin
        case(tx_fsm)
            TX_IDLE: begin
                if(tx_vld) begin: if_tx_new_data
                    tx_rdy          <= 1'b0;
                    tx_bit_baudrate <= '0;
                    tx_bit_count    <= '0;
                    tx_data_buff    <= {1'b0, tx_data, 1'b1};
                    
                    tx_fsm <= TX_DATA_SEND;
                end
            end
            
            TX_DATA_SEND: begin
                tx_uart <= tx_data_buff[tx_bit_count];
                
                if(tx_bit_baudrate < CLKS_PER_BIT) begin: if_sending_bit
                    tx_bit_baudrate <= tx_bit_baudrate + 1;
                    
                end else begin: if_done_sending_bit
                    tx_bit_baudrate <= 'b0;
                    if(tx_bit_count < TOTAL_BITS) begin: if_more_bits_to_send
                        tx_bit_count <= tx_bit_count + 1;
                        
                    end else begin: if_done_all_bits
                        tx_rdy <= 1'b1;
                        tx_fsm <= TX_IDLE;
                    end
                    
                end
            end
        endcase
    end
end

// --------------------------------------------------------------------------------
logic rx_counter_enable;
logic [CLKS_PER_BIT_WL-1:0] rx_bit_counter;

assign rx_valid = 1'b0;
assign rx_data = '0;
assign rx_err  = 1'b0;

endmodule
