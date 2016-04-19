
![MaJOrCA](./_doc/source/logo_MaJOrCA.png)
# Multiple JObs CreAtor

[![Build Status](https://travis-ci.org/ESeNonFossiIo/MaJOrCA.svg?branch=master)](https://travis-ci.org/ESeNonFossiIo/MaJOrCA) [![Coverage Status](https://coveralls.io/repos/github/ESeNonFossiIo/MaJOrCA/badge.svg?branch=master)](https://coveralls.io/github/ESeNonFossiIo/MaJOrCA?branch=master) [![codecov.io](https://codecov.io/github/ESeNonFossiIo/MaJOrCA/coverage.svg?branch=master)](https://codecov.io/github/ESeNonFossiIo/MaJOrCA?branch=master) [![Code Issues](https://www.quantifiedcode.com/api/v1/project/18dfccfa2b8b4c36bc65aa7dd95aaba4/badge.svg)](https://www.quantifiedcode.com/app/project/18dfccfa2b8b4c36bc65aa7dd95aaba4)

# Introduction

MaJOrCA is a generator of `prm` files from a blueprint `prm` file

Consider a prm like this:
``` prm
# Listing of Parameters
# ---------------------
subsection Finite element system
  set Dimension of problem = __DIM__[[2]]

  # Gauss quadrature order
  set Quadrature order  = 3
end

subsection Geometry
  # Global refinement level
  set Global refinement   = __REF__[[2]]

  # Global grid scaling factor
  set Grid scale          = 1e-3

  # Ratio of applied pressure to reference pressure
  set Pressure ratio p/p0 = __NU__
end
```
and consider the case we would like to run the same simulation but for different
values of `Global refinement`.

`MaJOrCA` is able to read a `conf` file where it is possible to specify this 
requirement:
``` conf
[GENERAL]

# Char used to separe multiple values, used to generate
# several runs
SEP = ||

# Parsing token: surround variables names with this token
# to make substitutions
PTOKEN = __

# Name of the prm file:
PRM_FILENAME = parameters.prm

...

################################################################################
## SIMULATIONS:
################################################################################

[Simulation_01]

...

# Parameters
DIM=2
NU=1
REF=9 || 8
```

## Configure
1. modify `./MaJOrCA.py -c your_conf.conf`
2. modify `your_conf.conf`
3. launch `./MaJOrCA.py -f your_conf.conf`

## Uasge:

This program takes a `prm` file like this:

```conf
subsection Navier Stokes Interface  
  set Preconditioner                   = __PREC__
  set div-grad stabilization           = __DIV_GRAD__[[1]]
  set nu [Pa s]                        = __NU__[[0.1]]
  set rho [kg m^3]                     = 1.0
end
```

and generate all `sh` or `pbs` scripts to launch your simulation.

In `your_conf.conf` you have to specify the values of your simulation (separated by a semilcon in case of multiple run):
```
[simulation_name]
NU=0.1;0.01;0.001
PREC=default
DIV_GRAD=
```
In this case the program will generate 3 runs, one for each `NU` and will assign to `DIV_GRAD` the default value (1).

## Note:
- In `conf` file you can generate multiple jobs adding new sections
- For every varibale you can select multiples choice separating each entry with 
  a semicolon

## makefile
- `clean` : remove unused file.
- `qsub` :  submit all `pbs` file. 
- `sh` :  submit all `sh` file. 
