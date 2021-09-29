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

import os
import logging
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer

from cocotb_test import simulator

# -----------------------------------------------------------------------------
# CoCoTB Module
@cocotb.test()
async def dummy_multiplier_basic_test(dut):
    """
    Basic multiplier test
    """
    
    # Set logger
    log = logging.getLogger("TB")
    log.setLevel('INFO')
    
    # Start test
    log.info('Multiplier basic test')
    
    # Setup TB
    clock = Clock(dut.clk, 10, units='ns') 
    cocotb.fork(clock.start())
    
    # Reset system
    await FallingEdge(dut.clk)
    log.info('Set reset')
    dut.reset <= 1
    await RisingEdge(dut.clk)
    log.info('Release reset')
    dut.reset <= 0
    
    # Set inputs
    log.info("Doing 5x7 = 35")
    dut.multiplier   <= 5
    dut.multiplicand <= 7
    dut.start <= 1
    await RisingEdge(dut.clk)
    dut.start <= 0
    
    # Wait result
    max_cnt = 10
    while dut.done == 0 and max_cnt:
        log.info("Waiting DUT ready")
        max_cnt -= 1
        await RisingEdge(dut.clk)
    
    if(max_cnt != 0):
        log.info(f'Data captured: {dut.product}')
        assert dut.product == 35, f'5x7 -> 35, but got {dut.product.value}'
    else:
        log.error(f'max_cnt reached without done set')
        assert False
    
    # Sim done
    await Timer(100, units='ns')
    log.info('Test done!')
    
# -----------------------------------------------------------------------------
# pytest

# -----------------------------------------------------------------------------
# Invoke test
if __name__ == '__main__':
    # cocotb-test default is icarus, switching to verilator
    sim = os.environ.get('SIM', 'verilator')
    os.environ['SIM'] = sim
    # ---------------------------------------
    _workpath = str(Path(__file__).resolve().parent)
    # ---------------------------------------
    sim_build = str(Path(_workpath) / "sim_build" / 'dummy_multiplier_basic_test')
    # ---------------------------------------
    simulator.run(
        toplevel='dummy_multiplier',
        module=Path(__file__).stem,
        verilog_sources=['../rtl/dummy_multiplier.sv'],
        sim_build=sim_build,
    )
    