@echo off
: gmsge_nt.cmd: Command Line Interface for Windows NT
: GAMS Development Corporation, Washington, DC, USA  1996
:
:  %1  Scratch directory with a '\' at the end
:  %2  Working directory with a '\' at the end
:  %3  Parameter file
:  %4  Control file
:  %5  System directory
:  %6  Solver name
:
: The command line length in NT is "pretty long".

gmsge_nx.exe    "%~4"
