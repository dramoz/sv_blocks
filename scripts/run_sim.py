#####################################################################################
#  File: run_sim.py
#  Copyright (c) 2021 Danilo Ramos
#  All rights reserved.
#  This license message must appear in all versions of this code including
#  modified versions.
#  BSD 3-Clause
####################################################################################
#  Overview:
"""
Simple UART Testbench
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
from cocotb_test import simulator

# -----------------------------------------------------------------------------
# Internal modules
_workpath = str(Path(__file__).resolve().parent)
sys.path.append(_workpath)

# -----------------------------------------------------------------------------
def run_cocotb(
    module,
    test_name, top_level,
    include_dirs=['../rtl'],
    verilog_sources=[], vhdl_sources=[],
    parameters=[],
    testcase=None,
):
    # ---------------------------------------
    toplevel_lang = 'verilog' if verilog_sources else 'vhdl'
    # ---------------------------------------
    sim_build = str(Path(_workpath) / "sim_build" / test_name)
    # ---------------------------------------
    # load environment variables defined by user at command line
    # e.g. SIM=icarus
    # cocotb-test default is icarus, switching to verilator
    sim = os.environ.get('SIM', 'verilator')
    os.environ['SIM'] = sim
    
    coverage = os.environ.get('COVERAGE_RUN', '-1')
    seed = os.environ.get('SEED', '0')
    if seed=='0':
        seed=None
    else:
        seed = int(seed)
    
    # ---------------------------------------
    extra_env = {}
    # timeunit/timeprecision
    extra_env['COCOTB_HDL_TIMEUNIT'] = '1ns'
    extra_env['COCOTB_HDL_TIMEPRECISION'] = '100ps'
    # simulation 'x' resolve
    # COCOTB_RESOLVE_X=[VALUE_ERROR, ZEROS, ONES, RANDOM] )
    extra_env['COCOTB_RESOLVE_X'] = 'RANDOM'
    
    # ---------------------------------------
    loglevel = os.environ.get('LOGLEVEL', 'WARNING')
    extra_env['LOGLEVEL'] = loglevel
    # ---------------------------------------
    
    # Include(s) directories, path from sim_build/test_id/
    compile_args = [f"-I{d}" for d in include_dirs]
    
    # ---------------------------------------
    extra_args = []
    # Verilator
    if sim == 'verilator':
        # remove warnings OK to sim (this is not linting)
        for arg in  ['fatal', 'UNOPT', 'UNOPTFLAT', 'UNUSED', 'WIDTH']:
            extra_args.append(f'-Wno-{arg}')
        
        if coverage != '-1':
            extra_args.append('--coverage')
        
    elif sim == 'icarus':
        pass
        
    # ---------------------------------------
    logging.info(f'Running test: {test_name} on UUT: {top_level}')
    simulator.run(
        toplevel=top_level,
        module=module,
        python_search=[_workpath],
        verilog_sources=verilog_sources,
        vhdl_sources=vhdl_sources,
        toplevel_lang=toplevel_lang,
        #includes=None,
        #defines=None,
        parameters=parameters,
        compile_args=compile_args,
        #sim_args=None,
        extra_args=extra_args,
        #plus_args=None,
        force_compile=True,
        #compile_only=True,
        testcase=testcase,
        sim_build=sim_build,
        seed=seed,
        extra_env=extra_env,
    )

