# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

TOPLEVEL_LANG ?= verilog
SIM ?= verilator
VERILOG_SOURCES = ../rtl/uart_tx_rx.sv
MODULE = uart_tx_rx_tb
TOPLEVEL = uart_tx_rx

include $(shell cocotb-config --makefiles)/Makefile.sim
