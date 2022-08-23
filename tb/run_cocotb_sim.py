# ============================================================================
#  File: run_cocotb_sim.py
#  Author: Danilo Ramos
#  Copyright (c) 2021. Eidetic Communications Inc.
#  All rights reserved.
#  Licensed under the BSD 3-Clause license.
#  This license message must appear in all versions of this code including
#  modified versions.
# ============================================================================
#  Overview:
"""
CoCoTB testbench runner with cocotb-test
"""

# -----------------------------------------------------------------------------
# Info
__author__ = 'Danilo Ramos'
__copyright__ = 'Copyright (c) 2021'
__credits__ = ['Danilo Ramos', 'Jonathan Eskritt']
__version__ = "0.0.3"
__maintainer__ = 'Danilo Ramos'
__email__ = 'danilo.ramos@eideticom.com'

# __status__ = ["Prototype"|"Development"|"Production"]
__status__ = "Development"

import sys, os
import logging
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Union
from cocotb_test import simulator

# -----------------------------------------------------------------------------
src_path_t = Union[str, Path]

def run_cocotb(
  module: str,
  top_level: str,
  test_name: Optional[str] = None,
  include_dirs: Optional[Sequence[src_path_t]] = None,
  hdl_sources: Sequence[src_path_t] = None,
  simulator_engine: Optional[str] = None,
  parameters: Optional[Mapping[str, Any]] = None,
  testcase: Optional[str] = None,
  workpath: Optional[src_path_t] = None,
  seed: Optional[int] = None,
  extra_env: Optional[Dict[str, str]] = None
) -> None:
  """cocotb-test wrapper (https://github.com/themperek/cocotb-test)
  
  Wrapper around cocotb-test (which removes the Makefile requirement, and enables pytest utilities)
  - Auto-search for RTL files
  - Set default timeunit/timeprecision
  - Set simulator(s) common parameters
  
  :param module: python file with the CoCoTB testcase(s). If run_cocotb(...) invoked from the module, use: Path(__file__).stem as argument value (e.g. with "if __name__ == '__main__':")
  :param test_name: test output dir used as work directory. Simulation will run under "sim_build/test_name", if None -> test_name = top_level_test
  :param top_level: Name of the top level RTL module (DUT) to test
  :param include_dirs: directories to be included in the simulation (for packages search or HDL sources auto-search), defaults to None (../rtl)
  :param hdl_sources: HDL(aka RTL) source files. It could be a list of files, a path to a file containing the list of HDL/RTL files or None (If None -> auto-search using include_dirs) Acceptable extensions files are VHDL['vhd', 'vhdl'], Verilog/SystemVerilog['v', 'sv', 'vlog']
  :param simulator_engine: simulator to use (verilator, icarus, modelsim, ...) - if None and not enviromental SIM variable is found, defaults to verilator
  :param parameters: top-level parameters as mapping structure: key:value => parameter_name:parameter_value, defaults to None
  :param testcase: specific to run only the CoCoTB test declared in the module file, defaults to None (e.g. run all cocotb_test in module file)
  :param workpath: Where to run the files, find python, defaults to None (cwd)
  :param seed: simulation seed to replicate previous runs, defaults to None
  :param extra_env: Extra environmental variables to pass to sim. This can be used to pass config to TB through pytest
  """
  # -------------------------------------------------------------------
  log = logging.getLogger("run_cocotb")
  loglevel = os.environ.get('LOGLEVEL', 'WARNING')
  longformat = os.environ.get('COCOTB_REDUCED_LOG_FMT', '0')
  # -------------------------------------------------------------------
  # Check arguments
  if test_name is None:
    test_name = f'{top_level}_test'
  log.debug(f"test_name: {test_name}")
  # -------------------------------------------------------------------
  if include_dirs is None:
    include_dirs = ['../rtl', '../tb']
  else:
    include_dirs = [str(x) for x in include_dirs]
  log.debug(f"Include dirs: {include_dirs}")
  # -------------------------------------------------------------------
  verilog_ext = ['v', 'sv', 'vlog']
  vhdl_ext = ['vhd', 'vhdl']
  verilog_sources = []
  vhdl_sources = []
  if hdl_sources is None:
    # Search the include dirs
    for d in include_dirs:
      verilog_sources.extend(list(Path(d).glob(f'**/*.({"|".join(verilog_ext)})')))
      vhdl_sources.extend(list(Path(d).glob(f'**/*.({"|".join(vhdl_ext)})')))
      
  else:
    log.debug(f"hdl_sources: {hdl_sources}")
    if isinstance(hdl_sources, Path):
      # File with list of HDL files
      hdl_sources = hdl_sources.read_text()
    
    else:
      if not isinstance(hdl_sources, list):
        raise ValueError(f"hdl_sources must be None, a path to a file or a list of files, but type(hdl_sources): {type(hdl_sources)}")
        
    if any(f'.{ext}' in file for file in hdl_sources for ext in verilog_ext):
      verilog_sources = hdl_sources
      
    if any(f'.{ext}' in file for file in hdl_sources for ext in vhdl_sources):
      vhdl_sources = hdl_sources
  
  if vhdl_sources:
    log.debug(f"VHDL source files: {vhdl_sources}")
  if verilog_sources:
    log.debug(f"Verilog/SV source files: {verilog_sources}")
    
  # -------------------------------------------------------------------
  # cocotb-test default is icarus, switching to verilator
  sim_verilog = ['icarus', 'verilator', 'cvc']
  sim_vhdl    = ['ghdl']
  sim_mixed   = ['vcs', 'riviera', 'activehdl', 'questa', 'modelsim', 'ius', 'xcelium']
  if simulator_engine is None:
    sim = os.environ.get('SIM', 'verilator')
  else:
    sim = simulator_engine
  os.environ['SIM'] = sim
  
  # Check simulator support
  if not (verilog_sources or vhdl_sources):
    raise ValueError("No HDL files found")
  if verilog_sources and vhdl_sources:
    if sim in sim_verilog+sim_vhdl:
      raise ValueError("Selected simulator engine ({sim}) does not support mixed languages Verilog/VHDL")
    
  elif verilog_sources:
    if sim not in sim_verilog+sim_mixed:
      raise ValueError("Selected simulator engine ({sim}) does not support Verilog")
      
  elif vhdl_sources:
    if sim not in sim_vhdl+sim_mixed:
      raise ValueError("Selected simulator engine ({sim}) does not support VHDL")
    
  toplevel_lang = 'verilog' if verilog_sources else 'vhdl'
  # -------------------------------------------------------------------
  if workpath is None:
    workpath = Path(os.getcwd())
  else:
    workpath = Path(workpath)
  sim_build = str(Path(workpath) / "sim_build" / test_name)
  
  # -------------------------------------------------------------------
  # load SEED
  seed = os.environ.get('SEED', seed)
  seed = int(seed)
  if seed==0:
    seed=None
  
  # -------------------------------------------------------------------
  # load environment variables defined by user at command line
  # waves: waves are handled by cocotb-test, however extra parameters are required
  # to trace structs and parameters
  waves = os.environ.get('WAVES', '-1')
  # coverage
  coverage = os.environ.get('COVERAGE_RUN', '-1')
  
  # -------------------------------------------------------------------
  if extra_env is None:
    extra_env = {}
  else:
    extra_env = {nm:str(vl) for nm,vl in extra_env.items() if vl not in [None, 'None']}
  
  # TB path
  extra_env['TB_PATH'] = str(Path(workpath).resolve())
  
  # timeunit/timeprecision
  extra_env['COCOTB_HDL_TIMEUNIT'] = '1ns'
  extra_env['COCOTB_HDL_TIMEPRECISION'] = '100ps'
  # simulation 'x' resolve
  # COCOTB_RESOLVE_X=[VALUE_ERROR, ZEROS, ONES, RANDOM] )
  extra_env['COCOTB_RESOLVE_X'] = 'RANDOM'
  
  # -------------------------------------------------------------------
  extra_env['LOGLEVEL'] = loglevel
  extra_env['COCOTB_REDUCED_LOG_FMT'] = longformat
  # -------------------------------------------------------------------
  
  # Include(s) directories, path from sim_build/test_id/
  compile_args = [f"-I{d}" for d in include_dirs]
  
  # -------------------------------------------------------------------
  # Note: wave generation is managed by cocotb-test with env. variable "WAVES=1 python script_test.py"
  extra_args = []
  # Verilator
  if sim == 'verilator':
    extra_args.append('--assert')
    # remove warnings OK to sim (this is not linting)
    for arg in  ['fatal', 'UNOPT', 'UNOPTFLAT', 'UNUSED', 'WIDTH']:
      extra_args.append(f'-Wno-{arg}')
      
    if waves != '-1':
      extra_args.append('--trace-params')
      
    if coverage != '-1':
      extra_args.append('--coverage')
    
  elif sim == 'icarus':
    pass
    
  # -------------------------------------------------------------------
  logging.info(f'Running test: {test_name} on UUT: {top_level}')
  
  simulator.run(
    toplevel=top_level,
    module=module,
    python_search=[str(workpath)],
    verilog_sources=verilog_sources,
    vhdl_sources=vhdl_sources,
    toplevel_lang=toplevel_lang,
    includes=include_dirs,
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
    extra_env=extra_env
  )
