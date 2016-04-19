.. MaJOrCA documentation master file, created by
   sphinx-quickstart on Thu Apr 14 16:43:20 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MaJOrCA's documentation!
========================

Contents:

.. toctree::
   :maxdepth: 2


.. image:: https://travis-ci.org/ESeNonFossiIo/MaJOrCA.svg?branch=master
  :target: https://travis-ci.org/ESeNonFossiIo/MaJOrCA

.. image:: https://coveralls.io/repos/github/ESeNonFossiIo/MaJOrCA/badge.svg?branch=master
  :target: https://coveralls.io/github/ESeNonFossiIo/MaJOrCA?branch=master

.. image:: https://codecov.io/github/ESeNonFossiIo/MaJOrCA/coverage.svg?branch=master
  :target: https://codecov.io/github/ESeNonFossiIo/MaJOrCA?branch=master

.. image:: https://www.quantifiedcode.com/api/v1/project/18dfccfa2b8b4c36bc65aa7dd95aaba4/badge.svg
  :target: https://www.quantifiedcode.com/app/project/18dfccfa2b8b4c36bc65aa7dd95aaba4
  :alt: Code issues

Configure
---------
  1. modify `./create_job.py -c your_conf.conf`
  2. modify `your_conf.conf`
  3. launch `./create_job.py -f your_conf.conf`

Usage:
------

  This program takes a `prm` file like this:

.. code:: conf
  subsection Navier Stokes Interface  
    set Preconditioner                   = __PREC__
    set div-grad stabilization           = __DIV_GRAD__[[1]]
    set nu [Pa s]                        = __NU__[[0.1]]
    set rho [kg m^3]                     = 1.0
  end


  and generate all `sh` or `pbs` scripts to launch your simulation.

  In `your_conf.conf` you have to specify the values of your simulation (separated by a semilcon in case of multiple run):

.. code:: conf
  [simulation_name]
  NU=0.1;0.01;0.001
  PREC=default
  DIV_GRAD=


  In this case the program will generate 3 runs, one for each `NU` and will assign to `DIV_GRAD` the default value (1).

Note:
-----
  - In `conf` file you can generate multiple jobs adding new sections
  - For every varibale you can select multiples choice separating each entry with 
    a semicolon
    
makefile
--------
  - `clean` : remove unused file.
  - `qsub` :  submit all `pbs` file. 
  - `sh` :  submit all `sh` file. 


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

