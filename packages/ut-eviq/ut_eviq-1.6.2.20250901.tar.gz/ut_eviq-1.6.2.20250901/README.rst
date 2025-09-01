#######
ut_eviq
#######

********
Overview
********

.. start short_desc

**Utilities for EcoVadis IQ Processing**

.. end short_desc

************
Installation
************

.. start installation

The Python Package ``ut_eviq`` can be installed from PyPI.

To install with ``pip``:

.. code-block:: shell

	$ python -m pip install ut_eviq

.. end installation

***************
Package logging 
***************

(c.f.: **Appendix**: `Package Logging`)

*************
Package files
*************

Classification
==============

The Files of Package ``ut_eviq`` could be classified into the follwing file types: (c.f.: **Appendix**: `Python Glossary`):

#. **Special files**

   a. *py.typed*

#. **Special modules**

   a. *__init__.py*
   #. *__version__.py*

#. **Sub-Package**

   a. *xls*

      #. **Special files**

         a. *py.typed*

      #. **Special modules**

         a. *__init__.py*
         #. *__version__.py*

      #. **Modules**

         a. *cfg.py*
         a. *taskin.py*
         a. *taskioc.py*
         a. *utils.py*

**************
Package Module
**************

Module: utils
=============

Classes of Modul: utils
-----------------------

The Module ``utils.py`` contains the the follwing static classes.

  .. utils.py-classes-label:
  .. table:: utils.py classes*

   +--------+---------------------------------------+
   |Name    |Description                            |
   +========+=======================================+
   |Evup    |Manage EcoVadis upload workbook        |
   +--------+---------------------------------------+
   |Evex    |Manage EcoVadis export workbook        |
   +--------+---------------------------------------+
   |Evin    |Manage EcoVadis inputworkbook (provided|
   |        |by external systems like OmniTracker)  |
   +--------+---------------------------------------+
   |EvinEvex|Check EcoVadis input workbook against  |
   |        |EcoVadis export workbook               |
   +--------+---------------------------------------+
   |EvexEvin|Check EcoVadis Export workbook against |
   |        |EcoVadis input workbook                |
   +--------+---------------------------------------+

Class: Evup
-----------

The static Class ``Evup`` contains the subsequent methods.

Methods of Class: Evup
^^^^^^^^^^^^^^^^^^^^^^                  

  .. Evup-methods-label:
  .. table:: Evup methods*

   +---------------+--------------------------------------------------------------+
   |Name           |Description                                                   |
   +===============+==============================================================+
   |sh_aod_evup_adm|Create and show the array of dictionaries for given dictionary|
   |               |of arrays of dictionaries and given operation by applying the |
   |               |union function to the array of dictionaries.                  |
   +---------------+--------------------------------------------------------------+

Class: Evex
-----------

The static Class ``Evex`` contains the subsequent methods.

Methods of Class: Evex
^^^^^^^^^^^^^^^^^^^^^^

  .. Evex-methods-label:
  .. table:: Evex methods*

   +----------------------+-----------------------------------------------------+
   |Name                  |Description                                          |
   +======================+=====================================================+
   |sh_d_evex             |Migrate an EcoVadis export dataframe to a dictionary.|
   +----------------------+-----------------------------------------------------+
   |sh_d_evup_del_from_dic|Migrate an EcoVadis export dictionary to a dictionary|
   |                      |for the EcoVadis upload delete sheet.                |
   +----------------------+-----------------------------------------------------+
   |sh_d_evup_del_from_df |Migrate an EcoVadis export dataframe row to a        |
   |                      |dictionary for the EcoVadis upload delete sheet.     |
   +----------------------+-----------------------------------------------------+
   |map                   |Map the EcoVadis IQ sustainability risk rating in the|
   |                      |array of EcoVadis disk dictionaries to the risk      |
   |                      |rating defined by UMH.                               |
   +----------------------+-----------------------------------------------------+

Class: Evin
-----------

The static Class ``Evin`` contains the subsequent methods.

Evin: Methods
^^^^^^^^^^^^^

  .. Evin-methods-label:
  .. table:: Evin methods*

   +----------------------------+-----------------------------------------------------+
   |Name                        |Description                                          |
   +============================+=====================================================+
   |sh_d_evup_adm               |Migrate an OmniTracker export dictionary to a        |
   |                            |EcoVadis upload dictionary.                          |
   +----------------------------+-----------------------------------------------------+
   |sh_aod_evup_adm             |Migrate an array of OmniTracker export dictionaries  |
   |                            |to an array of EcoVadis upload dictionaries.         |
   +----------------------------+-----------------------------------------------------+
   |verify_duns                 |Verify the field 'DUNS-Nummer' for all dictionaries  |
   |                            |of the given array of OmniTracker export dictionaries|
   |                            |if the verification is requested.                    |
   +----------------------------+-----------------------------------------------------+
   |verify_objectid             |Verify the field 'Eindeutige ID' for all dictionaries|
   |                            |of the given array of OmniTracker export dictionaries|
   |                            |if the verification is requested.                    |
   +----------------------------+-----------------------------------------------------+
   |verify_countrycode          |Verify the field 'Landesvorwahl' for all dictionaries|
   |                            |of the given array of OmniTracker export dictionaries|
   |                            |if the verification is requested.                    |
   +----------------------------+-----------------------------------------------------+
   |verify_town_in_country      |Verify the field 'Stadt' together with the field     |
   |                            |'Landesvorwahl' for all dictionaries of the given    | 
   |                            |array of OmniTracker export dictionaries if the      |
   |                            |verification is requested.                           |
   +----------------------------+-----------------------------------------------------+
   |verify_postalcode_in_country|Verify the field 'Postleitzahl' together with the    |
   |                            |field 'Landesvorwahl' for all dictionaries of the    |
   |                            |given array of OmniTracker export dictionaries if the|
   |                            |verification is requested.                           |
   +----------------------------+-----------------------------------------------------+
   |verify                      |Verify all fields of all dictionaries of the given   |
   |                            |array of OmniTracker export dictionaries if the      |
   |                            |verification is requested and return the verification|
   |                            |status controlled by the verify ignore switches.     |
   +----------------------------+-----------------------------------------------------+
   |verify_aod_evin             |Apply the verify function to all dictionaries of the |
   |                            |array of Omnitracker export dictionaries.            |
   +----------------------------+-----------------------------------------------------+
   |sh_doaod_adm_new            |Migrate array of Omnitracker export dictionaries     |
   |                            |to dictionary of array of EcoVadis upload            |
   |                            |dictionaries for Admin processing                    |
   +----------------------------+-----------------------------------------------------+

Class: EvexEvin
---------------

The static Class ``EvexEvin`` contains the subsequent methods.

EvexEvin: Methods
^^^^^^^^^^^^^^^^^

  .. EvexEvin-methods-label:
  .. table:: EvexEvin methods*

   +--------+--------------------------------------------------------------+
   |Name    |Description                                                   |
   +========+==============================================================+
   |join_del|Join the Array of EcoVadis export dictionaries with the       |
   |        |dataframe of OmniTracker export records for delete processing.| 
   +--------+--------------------------------------------------------------+

Class: EvinEvex
---------------

The static Class ``EvinEvex`` contains the subsequent variables and methods.

EvinEvex: Variables
^^^^^^^^^^^^^^^^^^^

  .. EvinEvex-variabless-label:
  .. table:: EvinEvex variables*

   +--------+-----------------------------------------------------------------------+
   |Name    |Description                                                            |
   +========+=======================================================================+
   |msg_evex|Message that could be displayed when processing the EcoVadis export.   |
   +--------+-----------------------------------------------------------------------+
   |msg_evin|Message that could be displayed when processing the OmniTracker export.|
   +--------+-----------------------------------------------------------------------+

Methods of class: EvinEvex
^^^^^^^^^^^^^^^^^^^^^^^^^^

  .. EvinEvex-methods-label:
  .. table:: EvinEvex methods*

   +---------------+-----------------------------------------------------------+
   |Name           |Description                                                |
   +===============+===========================================================+
   |query_with_keys|Query EcoVadis dataframe with multiple keys and country    |
   |               |code until row is found and return row.                    |
   +---------------+-----------------------------------------------------------+
   |query          |Query EcoVadis dataframe with OmniTracker export keys:     |
   |               |'Eindeutige ID' or 'DUNS-Nummer' or keys form array of keys|
   |               |until row is found.                                        |
   +---------------+-----------------------------------------------------------+
   |join_adm       |Join the Array of OmniTracke export dictionaries with the  |
   |               |dataframe of EcoVadis export records for admin processing. | 
   +---------------+-----------------------------------------------------------+
   |join_del       |Join the Array of OmniTracke export dictionaries with the  |
   |               |dataframe of EcoVadis export records for delete processing.| 
   +---------------+-----------------------------------------------------------+
   |sh_d_evup_adm  |Show change status and EcoVadis upload dictionary for      |
   |               |OmniTracker export- and EcoVadis export-dictionary         |
   +---------------+-----------------------------------------------------------+

########
Appendix
########

***************
Package Logging
***************

Description
===========

Logging use the module **log.py** of the logging package **ut_log**.
The module supports two Logging types:

#. **Standard Logging** (std) or 
#. **User Logging** (usr).

The Logging type can be defined by one of the values 'std' or 'usr' of the parameter log_type; 'std' is the default.
The different Logging types are configured by one of the following configuration files:

#. **log.std.yml** or 
#. **log.usr.yml** 
  
The configuration files can be stored in different configuration directories (ordered by increased priority):

#. <package directory of the log package **ut_log**>/**cfg**,
#. <package directory of the application package **ui_eviq_srr**>/**cfg**,
#. <application directory of the application **eviq**>/**cfg**,

The active configuration file is the configuration file in the directory with the highest priority.

Examples
========
  
Site-packages-path = **/appl/eviq/.pyenv/versions/3.11.12/lib/python3.11/site-packages**
Log-package = **ut_log**
Application-package = **ui_eviq_srr**
Application-home-path = **/appl/eviq**
  
.. Examples-of-log-configuration-files-label:
.. table:: **Examples of log configuration-files**

   +-----------------------------------------------------------------------------------+
   |Log Configuration                                                                  |
   +----+-------------------+----------------------------------------------+-----------+
   |Type|Directory Type     |Directory                                     |File       |
   +====+===================+==============================================+===========+
   |std |Log package        |<Site-packages-path>/<Log-package>/cfg        |log.std.yml|
   |    +-------------------+----------------------------------------------+           |
   |    |Application package|<Site-packages-path>/<application-package>/cfg|           |
   |    +-------------------+----------------------------------------------+           |
   |    |Application        |<application-home-path>/cfg                   |           |
   +----+-------------------+----------------------------------------------+-----------+
   |usr |Log package        |<site-packages-path>/ut_log/cfg               |log.usr.yml|
   |    +-------------------+----------------------------------------------+           |
   |    |Application package|<site-packages-path>/ui_eviq_srr/cfg          |           |
   |    +-------------------+----------------------------------------------+           |
   |    |Application        |<application-path>/cfg                        |           |
   +----+-------------------+----------------------------------------------+-----------+

Log message types
=================

Logging defines log file path names for the following log message types: .

#. *debug*
#. *info*
#. *warning*
#. *error*
#. *critical*

Log types and Log directories
-----------------------------

Single or multiple Application log directories can be used for each message type:

.. Log-types-and-Log-directories-label:
.. table:: *Log types and directoriesg*

   +--------------+---------------+
   |Log type      |Log directory  |
   +--------+-----+--------+------+
   |long    |short|multiple|single|
   +========+=====+========+======+
   |debug   |dbqs |dbqs    |logs  |
   +--------+-----+--------+------+
   |info    |infs |infs    |logs  |
   +--------+-----+--------+------+
   |warning |wrns |wrns    |logs  |
   +--------+-----+--------+------+
   |error   |errs |errs    |logs  |
   +--------+-----+--------+------+
   |critical|crts |crts    |logs  |
   +--------+-----+--------+------+

Application parameter for logging
---------------------------------

.. Application-parameter-used-in-log-naming-label:
.. table:: *Application parameter used in log naming*

   +-----------------+--------------+-----+------------------+-------+-----------+
   |Name             |Decription    |Value|Description       |Default|Example    |
   +=================+==============+=====+==================+=======+===========+
   |appl_data        |data directory|     |                  |       |/data/eviq |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |tenant           |tenant name   |UMH  |                  |       |UMH        |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |package          |package name  |     |                  |       |ui_eviq_srr|
   +-----------------+--------------+-----+------------------+-------+-----------+
   |cmd              |command       |     |                  |       |evupreg    |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |log_type         |Logging Type  |std: |Standard logging  |std    |std        |
   |                 |              +-----+------------------+       |           |
   |                 |              |usr: |User Logging      |       |           |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |log_ts_type      |Logging       |ts:  |Sec since 1.1.1970|ts     |ts         |
   |                 |timestamp     +-----+------------------+       |           |
   |                 |type          |dt:  |Datetime          |       |           |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |log_sw_single_dir|Use single log|True |use single dir.   |True   |True       |
   |                 |directory     +-----+------------------+       |           |
   |                 |              |False|use muliple dir.  |       |           |
   +-----------------+--------------+-----+------------------+-------+-----------+

Log files naming
----------------

Naming Conventions (table format)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Naming-conventions-for-logging-file-paths-label:
.. table:: *Naming conventions for logging file paths*

   +--------+----------------------------------------------+-------------------+
   |Type    |Directory                                     |File               |
   +========+==============================================+===================+
   |debug   |/<appl_data>/<tenant>/RUN/<package>/<cmd>/debs|debs_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+
   |critical|/<appl_data>/<tenant>/RUN/<package>/<cmd>/logs|crts_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+
   |error   |/<appl_data>/<tenant>/RUN/<package>/<cmd>/logs|errs_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+
   |info    |/<appl_data>/<tenant>/RUN/<package>/<cmd>/logs|infs_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+
   |warning |/<appl_data>/<tenant>/RUN/<package>/<cmd>/logs|rnsg_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+

Naming Conventions (tree format)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

 <appl_data>   Application data folder
 │
 └── <tenant>  Application tenant folder
     │
     └── RUN  Applications RUN folder for Application log files
         │
         └── <package>  RUN folder of Application package: <package>
             │
             └── <cmd>  RUN folder of Application command <cmd>
                 │
                 ├── debs  Application command debug messages folder
                 │   │
                 │   └── debs_<ts>_<pid>.log  debug messages for
                 │                            run of command <cmd>
                 │                            with pid <pid> at <ts>
                 │
                 └── logs  Application command log messages folder
                     │
                     ├── crts_<ts>_<pid>.log  critical messages for
                     │                        run of command <cmd>
                     │                        with pid <pid> at <ts>
                     ├── errs_<ts>_<pid>.log  error messages for
                     │                        run of command <cmd>
                     │                        with pid <pid> at <ts>
                     ├── infs_<ts>_<pid>.log  info messages for
                     │                        run of command <cmd>
                     │                        with pid <pid> at <ts>
                     └── wrns_<ts>_<pid>.log  warning messages for
                                              run of command <cmd>
                                              with pid <pid> at <ts>

Naming Examples (table format)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Naming-conventions-for-logging-file-paths-label:
.. table:: *Naming conventions for logging file paths*

   +--------+--------------------------------------------+--------------------------+
   |Type    |Directory                                   |File                      |
   +========+============================================+==========================+
   |debug   |/appl/eviq/UMH/RUN/ui_eviq_srr/evdomap/debs/|debs_1750096540_354710.log|
   +--------+--------------------------------------------+--------------------------+
   |critical|/appl/eviq/UMH/RUN/ui_eviq_srr/evdomap/logs/|crts_1749971151_240257.log|
   +--------+                                            +--------------------------+
   |error   |                                            |errs_1749971151_240257.log|
   +--------+                                            +--------------------------+
   |info    |                                            |infs_1750096540_354710.log|
   +--------+                                            +--------------------------+
   |warning |                                            |wrns_1749971151_240257.log|
   +--------+--------------------------------------------+--------------------------+

Naming Examples (tree format)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

  /data/eviq/UMH/RUN/ui_eviq_srr/evdomap  Run folder of
  │                                       of function evdomap
  │                                       of package ui_eviq_srr
  │                                       for teanant UMH
  │                                       of application eviq
  │
  ├── debs  debug folder of Application function: evdomap
  │   │
  │   └── debs_1748609414_314062.log  debug messages for run 
  │                                   of function evdomap     
  │                                   using pid: 314062 at: 1748609414
  │
  └── logs  log folder of Application function: evdomap
      │
      ├── errs_1748609414_314062.log  error messages for run
      │                               of function evdomap     
      │                               with pid: 314062 at: 1748609414
      ├── infs_1748609414_314062.log  info messages for run
      │                               of function evdomap     
      │                               with pid: 314062 at: 1748609414
      └── wrns_1748609414_314062.log  warning messages for run
                                      of function evdomap     
                                      with pid: 314062 at: 1748609414

Configuration files
===================

log.std.yml (jinja2 yml file)
-----------------------------

Content
^^^^^^^

.. log.std.yml-label:
.. code-block:: jinja

 version: 1

 disable_existing_loggers: False

 loggers:

     # standard logger
     std:
         # level: NOTSET
         level: DEBUG
         handlers:
             - std_debug_console
             - std_debug_file
             - std_info_file
             - std_warning_file
             - std_error_file
             - std_critical_file

 handlers:
 
     std_debug_console:
         class: 'logging.StreamHandler'
         level: DEBUG
         formatter: std_debug
         stream: 'ext://sys.stderr'

     std_debug_file:
         class: 'logging.FileHandler'
         level: DEBUG
         formatter: std_debug
         filename: '{{dir_run_debs}}/debs_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true

     std_info_file:
         class: 'logging.FileHandler'
         level: INFO
         formatter: std_info
         filename: '{{dir_run_infs}}/infs_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true

     std_warning_file:
         class: 'logging.FileHandler'
         level: WARNING
         formatter: std_warning
         filename: '{{dir_run_wrns}}/wrns_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true

     std_error_file:
         class: 'logging.FileHandler'
         level: ERROR
         formatter: std_error
         filename: '{{dir_run_errs}}/errs_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true
 
     std_critical_file:
         class: 'logging.FileHandler'
         level: CRITICAL
         formatter: std_critical
         filename: '{{dir_run_crts}}/crts_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true

     std_critical_mail:
         class: 'logging.handlers.SMTPHandler'
         level: CRITICAL
         formatter: std_critical_mail
         mailhost : localhost
         fromaddr: 'monitoring@domain.com'
         toaddrs:
             - 'dev@domain.com'
             - 'qa@domain.com'
         subject: 'Critical error with application name'
 
 formatters:

     std_debug:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_info:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_warning:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_error:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_critical:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_critical_mail:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'

Jinja2-variables
^^^^^^^^^^^^^^^^

.. log.std.yml-Jinja2-variables-label:
.. table:: *log.std.yml Jinja2 variables*

   +------------+-----------------------------+-------------------------------------------+
   |Name        |Definition                   |Example                                    |
   +============+=============================+===========================================+
   |dir_run_debs|debug run directory          |/data/eviq/UMH/RUN/ui_eviq_srr/evupreg/debs|
   +------------+-----------------------------+-------------------------------------------+
   |dir_run_infs|info run directory           |/data/eviq/UMH/RUN/ui_eviq_srr/evupreg/logs|
   +------------+-----------------------------+                                           |
   |dir_run_wrns|warning run directory        |                                           |
   +------------+-----------------------------+                                           |
   |dir_run_errs|error run directory          |                                           |
   +------------+-----------------------------+                                           |
   |dir_run_crts|critical error run directory |                                           |
   +------------+-----------------------------+-------------------------------------------+
   |ts          |Timestamp since 1970 in [sec]|1749483509                                 |
   |            |if log_ts_type == 'ts'       |                                           |
   |            +-----------------------------+-------------------------------------------+
   |            |Datetime in timezone Europe/ |20250609 17:38:29 GMT+0200                 |
   |            |Berlin if log_ts_type == 'dt'|                                           |
   +------------+-----------------------------+-------------------------------------------+
   |pid         |Process ID                   |79133                                      |
   +------------+-----------------------------+-------------------------------------------+

***************
Python Glossary
***************

.. _python-modules:

Python Modules
==============

Overview
--------

  .. Python-Modules-label:
  .. table:: *Python Modules*

   +--------------+---------------------------------------------------------+
   |Name          |Definition                                               |
   +==============+==========+==============================================+
   |Python modules|Files with suffix ``.py``; they could be empty or contain|
   |              |python code; other modules can be imported into a module.|
   +--------------+---------------------------------------------------------+
   |special Python|Modules like ``__init__.py`` or ``main.py`` with special |
   |modules       |names and functionality.                                 |
   +--------------+---------------------------------------------------------+

.. _python-functions:

Python Function
===============

Overview
--------

  .. Python-Function-label:
  .. table:: *Python Function*

   +---------------+---------------------------------------------------------+
   |Name           |Definition                                               |
   +===============+==========+==============================================+
   |Python function|Files with suffix ``.py``; they could be empty or contain|
   |               |python code; other modules can be imported into a module.|
   +---------------+---------------------------------------------------------+
   |special Python |Modules like ``__init__.py`` or ``main.py`` with special |
   |modules        |names and functionality.                                 |
   +---------------+---------------------------------------------------------+

.. _python-packages:

Python Packages
===============

Overview
--------

  .. Python Packages-Overview-label:
  .. table:: *Python Packages Overview*

   +---------------------+---------------------------------------------+
   |Name                 |Definition                                   |
   +=====================+=============================================+
   |Python package       |Python packages are directories that contains|
   |                     |the special module ``__init__.py`` and other |
   |                     |modules, sub packages, files or directories. |
   +---------------------+---------------------------------------------+
   |Python sub-package   |Python sub-packages are python packages which|
   |                     |are contained in another python package.     |
   +---------------------+---------------------------------------------+
   |Python package       |directory contained in a python package.     |
   |sub-directory        |                                             |
   +---------------------+---------------------------------------------+
   |Python package       |Python package sub-directories with a special|
   |special sub-directory|meaning like data or cfg                     |
   +---------------------+---------------------------------------------+

Special python package sub-directories
--------------------------------------

  .. Special-python-package-sub-directory-Examples-label:
  .. table:: *Special python package sub-directories*

   +-------+------------------------------------------+
   |Name   |Description                               |
   +=======+==========================================+
   |bin    |Directory for package scripts.            |
   +-------+------------------------------------------+
   |cfg    |Directory for package configuration files.|
   +-------+------------------------------------------+
   |data   |Directory for package data files.         |
   +-------+------------------------------------------+
   |service|Directory for systemd service scripts.    |
   +-------+------------------------------------------+

.. _python-files:

Python Files
============

Overview
--------

  .. Python-files-label:
  .. table:: *Python files*

   +--------------+---------------------------------------------------------+
   |Name          |Definition                                               |
   +==============+==========+==============================================+
   |Python modules|Files with suffix ``.py``; they could be empty or contain|
   |              |python code; other modules can be imported into a module.|
   +--------------+---------------------------------------------------------+
   |Python package|Files within a python package.                           |
   |files         |                                                         |
   +--------------+---------------------------------------------------------+
   |Python dunder |Python modules which are named with leading and trailing |
   |modules       |double underscores.                                      |
   +--------------+---------------------------------------------------------+
   |special       |Files which are not modules and used as python marker    |
   |Python files  |files like ``py.typed``.                                 |
   +--------------+---------------------------------------------------------+
   |special Python|Modules like ``__init__.py`` or ``main.py`` with special |
   |modules       |names and functionality.                                 |
   +--------------+---------------------------------------------------------+

.. _python-special-files:

Python Special Files
--------------------

  .. Python-special-files-label:
  .. table:: *Python special files*

   +--------+--------+--------------------------------------------------------------+
   |Name    |Type    |Description                                                   |
   +========+========+==============================================================+
   |py.typed|Type    |The ``py.typed`` file is a marker file used in Python packages|
   |        |checking|to indicate that the package supports type checking. This is a|
   |        |marker  |part of the PEP 561 standard, which provides a standardized   |
   |        |file    |way to package and distribute type information in Python.     |
   +--------+--------+--------------------------------------------------------------+

.. _python-special-modules:

Python Special Modules
----------------------

  .. Python-special-modules-label:
  .. table:: *Python special modules*

   +--------------+-----------+----------------------------------------------------------------+
   |Name          |Type       |Description                                                     |
   +==============+===========+================================================================+
   |__init__.py   |Package    |The dunder (double underscore) module ``__init__.py`` is used to|
   |              |directory  |execute initialisation code or mark the directory it contains   |
   |              |marker     |as a package. The Module enforces explicit imports and thus     |
   |              |file       |clear namespace use and call them with the dot notation.        |
   +--------------+-----------+----------------------------------------------------------------+
   |__main__.py   |entry point|The dunder module ``__main__.py`` serves as package entry point |
   |              |for the    |point. The module is executed when the package is called by the |
   |              |package    |interpreter with the command **python -m <package name>**.      |
   +--------------+-----------+----------------------------------------------------------------+
   |__version__.py|Version    |The dunder module ``__version__.py`` consist of assignment      |
   |              |file       |statements used in Versioning.                                  |
   +--------------+-----------+----------------------------------------------------------------+

Python classes
==============

Overview
--------

  .. Python-classes-overview-label:
  .. table:: *Python classes overview*

   +-------------------+---------------------------------------------------+
   |Name               |Description                                        |
   +===================+===================================================+
   |Python class       |A class is a container to group related methods and|
   |                   |variables together, even if no objects are created.|
   |                   |This helps in organizing code logically.           |
   +-------------------+---------------------------------------------------+
   |Python static class|A class which contains only @staticmethod or       |
   |                   |@classmethod methods and no instance-specific      |
   |                   |attributes or methods.                             |
   +-------------------+---------------------------------------------------+

Python methods
==============

Overview
--------

  .. Python-methods-overview-label:
  .. table:: *Python methods overview*

   +--------------+-------------------------------------------+
   |Name          |Description                                |
   +==============+===========================================+
   |Python method |Python functions defined in python modules.|
   +--------------+-------------------------------------------+
   |Python class  |Python functions defined in python classes.|
   |method        |                                           |
   +--------------+-------------------------------------------+
   |Python special|Python class methods with special names and|
   |class method  |functionalities.                           |
   +--------------+-------------------------------------------+

Python class methods
--------------------

  .. Python-class-methods-label:
  .. table:: *Python class methods*

   +--------------+----------------------------------------------+
   |Name          |Description                                   |
   +==============+==============================================+
   |Python no     |Python function defined in python classes and |
   |instance      |decorated with @classmethod or @staticmethod. |
   |class method  |The first parameter conventionally called cls |
   |              |is a reference to the current class.          |
   +--------------+----------------------------------------------+
   |Python        |Python function defined in python classes; the|
   |instance      |first parameter conventionally called self is |
   |class method  |a reference to the current class object.      |
   +--------------+----------------------------------------------+
   |special Python|Python class functions with special names and |
   |class method  |functionalities.                              |
   +--------------+----------------------------------------------+

Python special class methods
----------------------------

  .. Python-methods-examples-label:
  .. table:: *Python methods examples*

   +--------+-----------+--------------------------------------------------------------+
   |Name    |Type       |Description                                                   |
   +========+===========+==============================================================+
   |__init__|class      |The special method ``__init__`` is called when an instance    |
   |        |object     |(object) of a class is created; instance attributes can be    |
   |        |constructor|defined and initalized in the method. The method us a single  |
   |        |method     |parameter conventionally called ``self`` to access the object.|
   +--------+-----------+--------------------------------------------------------------+

#################
Table of Contents
#################

.. contents:: **Table of Content**
