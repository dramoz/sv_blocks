#####################################################################################
## @author: Danilo Ramos
## @copyrightCopyright (c) 2021. Danilo Ramos
## All rights reserved
## 
## @license Licensed under the BSD 3-Clause license.
## This license message must appear in all versions of this code including
## modified versions.
##
## @brief Simple SV multipier testbench
## 
## product = multiplier * multiplicand
## 
#####################################################################################


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

import random
from itertools import product
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer

# -----------------------------------------------------------------------------
# Internal modules
_workpath = str(Path(__file__).resolve().parent)
sys.path.append(_workpath)

from run_sim import run_cocotb

# -----------------------------------------------------------------------------
# Parameters
# -----------------------------------------------------------------------------
# TB
CLK_FREQUENCY = 10000000
CLK_PERIOD = ceil(1 / CLK_FREQUENCY * 1e9)
CLK_PERIOD += CLK_PERIOD % 2
CLK_PERIOD_UNITS = 'ns'

# DUT
parameters = {
    'WL': 32,
}

# -----------------------------------------------------------------------------
# CoCoTB Module
@cocotb.test()
async def multiplier_test(dut):
    """
    Basic multiplier test
    """
    
    # Set logger
    log = logging.getLogger("TB")
    loglevel = os.environ.get("LOGLEVEL", 'INFO')
    log.setLevel(loglevel)
    
    # Start test
    log.info('Multiplier test')
    
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
    
    # Set inputs
    multiplier = [0, 1, 15, 17, 2]
    multiplicand = [3, 0, 7, 6]
    
    for op in list(product(multiplier, multiplicand)):
        log.info(f': {op[0]} x {op[1]}')
        dut.multiplier   <= op[0]
        dut.multiplicand <= op[1]
        await RisingEdge(dut.clk)
        
    
    await Timer(10*CLK_PERIOD, units=CLK_PERIOD_UNITS)
    log.info('Test done!')
    
async def multiplier_monitor(dut):
    inputs = []
    outputs = []
    
    
# -----------------------------------------------------------------------------
# Invoke test
if __name__ == '__main__':
    run_cocotb(
        module=Path(__file__).stem,
        test_name='uart_tx',
        top_level='uart_tx_rx',
        include_dirs=['../rtl'],
        verilog_sources=['../rtl/uart_tx_rx.sv'],
        parameters=parameters,
        testcase=None
    )
    