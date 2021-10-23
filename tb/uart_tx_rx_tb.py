#####################################################################################
#  File: uart_tx_rx_tb.py
#  Copyright (c) 2021 Danilo Ramos
#  All rights reserved.
#  This license message must appear in all versions of this code including
#  modified versions.
#  BSD 3-Clause
####################################################################################
#  Overview:
"""
Simple UART Testbench - CoCoTB module
"""

# -----------------------------------------------------------------------------
# Info
__author__ = 'Danilo Ramos'
__copyright__ = 'Copyright (c) 2021'
__credits__ = ['Danilo Ramos']
__license__ = 'BSD 3-Clause'
__version__ = "0.0.1"
__maintainer__ = 'Danilo Ramos'
__email__ = 'dramoz@gmail.com'

# __status__ = ["Prototype"|"Development"|"Production"]
__status__ = "Prototype"

import sys, os
import logging
from pathlib import Path

from math import ceil
import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer, ReadWrite

# -----------------------------------------------------------------------------
# Internal modules
_workpath = Path(__file__).resolve().parent
sys.path.append(str(_workpath))

HDL_VERIF_SCRIPTS = os.environ.get('HDL_VERIF_SCRIPTS')
assert HDL_VERIF_SCRIPTS is not None, "HDL_VERIF_SCRIPTS env. var not found! (required for loading run_sim)"
_hdl_verif_path = Path(HDL_VERIF_SCRIPTS) / 'src/hdl_verif'
sys.path.append(str(_hdl_verif_path))
print(_hdl_verif_path)
from run_cocotb_sim import run_cocotb_sim

# -----------------------------------------------------------------------------
# Parameters
CLK_FREQUENCY = 48000000
CLK_PERIOD = ceil(1 / CLK_FREQUENCY * 1e9)
CLK_PERIOD += CLK_PERIOD % 2
CLK_PERIOD_UNITS = 'ns'
BAUD_RATE = 115200

parameters = {
    'BAUD_RATE': BAUD_RATE,
    'CLK_FREQUENCY': CLK_FREQUENCY,
}

# -----------------------------------------------------------------------------
# CoCoTB Module
async def uart_rx_loop(dut):
    while True:
        await RisingEdge(dut.clk)
        await ReadWrite()
        dut.rx_uart <= dut.tx_uart.value
    
@cocotb.test()
async def uart_tx_test(dut):
    """ Send 'Hello World! """
    # Set logger
    log = logging.getLogger("TB")
    loglevel = os.environ.get("LOGLEVEL", 'INFO')
    log.setLevel(loglevel)
    
    # Start test
    log.info('UART TX test')
    
    # Setup TB
    log.info(f'CLK: {CLK_PERIOD} {CLK_PERIOD_UNITS}')
    clock = Clock(dut.clk, CLK_PERIOD, units=CLK_PERIOD_UNITS) 
    cocotb.fork(clock.start())
        
    # Reset system
    await FallingEdge(dut.clk)
    log.info('Set reset')
    dut.reset <= 1
    await RisingEdge(dut.clk)
    log.info('Release reset')
    dut.reset <= 0
    
    # RX
    cocotb.fork(uart_rx_loop(dut))
    
    # TX
    #data = b'\x55\x55'
    #data = b'He'
    #data = b'\x7f'
    data = b'Hello World!!!'
    for ch in data:
        while True:
            await RisingEdge(dut.clk)
            await ReadWrite()
            if dut.tx_rdy.value == 1:
                break
        
        log.info(f'UART TX: {hex(ch)}')
        dut.tx_data <= ch
        dut.tx_vld <= 1
        await RisingEdge(dut.clk)
        dut.tx_vld <= 0
    
    await RisingEdge(dut.tx_rdy)
    await Timer(1000*CLK_PERIOD, units=CLK_PERIOD_UNITS)
    log.info('Test done!')

# -----------------------------------------------------------------------------
# Invoke test
if __name__ == '__main__':
    run_cocotb_sim(
        py_module=Path(__file__).stem,
        workpath=Path(__file__).resolve().parent,
        test_name='uart_tx',
        top_level='uart_tx_rx',
        include_dirs=['../rtl'],
        hdl_sources=['../rtl/uart_tx_rx.sv'],
        parameters=parameters,
        testcase=None
    )
    