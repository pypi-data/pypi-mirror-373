##########
ut_xls
##########

********
Overview
********

.. start short_desc

**Excel 'Utilities'**

.. end short_desc

.. start long_desc

**The package ut_xls ís a collection of interface modules to the following 'Python Excel Utilities'**

.. end long_desc

#. *openpyxl*
#. *pyexcelerate*
#. *pandas dataframe excel functions*
#. *polars dataframe excel functions*

************
Installation
************

.. start installation

The package ``ut_xls`` can be installed from PyPI.

To install with ``pip``:

.. code-block:: shell

	$ python -m pip install ut_xls

.. end installation

*************
Package files
*************

lassification
==============

The Package ``ut_xls`` consist of the following file types (c.f.: **Appendix**: `Python Terminology`):

#. **Special files:**

   a. *py.typed*

#. **Special modules:**

   a. *__init__.py*
   #. *__version__.py*

#. **Sub-packages**

   #. **op**

      a. *__init__.py*
      #. *doaoa.py*
      #. *doaoa.py*
      #. *iocwb.py*
      #. *ioipathnmwb.py*
      #. *ioipathwb.py*
      #. *ioipathws.py*
      #. *ioopatnmwb.py*
      #. *ioopatwb.py*
      #. *ioupatwb.py*
      #. *ro.py*
      #. *wb.py*
      #. *ws.py*

   #. **pd**

      a. *__init__.py*
      #. *ioipathnmwb.py*
      #. *ioipathwb.py*
      #. *ioopathwb.py*

   #. **pe**

      a. *__init__.py*
      #. *doaos.py*
      #. *doaod.py*
      #. *iocwb.py*
      #. *ioopathnmwb.py*
      #. *ioopathwb.py*

   #. **pl**

      a. *__init__.py*
      #. *ioipathwb.py*

*******
Modules
*******

Overview
========

The Modules of Package ``ut_xls`` could be classified into the 
following module file types:

#. **I/O modules**

   a. *I/O Control module*
   #. *I/O Input modules*
   #. *I/O Output modules*
   #. *I/O Update modules*

#. **Workbook modules**

   a. *Workbook modules using openpyxl*
   #. *Workbook modules using pyexcelerate*

#. **Worksheet modules**

#. **Cell (Row) modules**


******************
I/O Control Module
******************

Overview
========

  .. I/O-Control-Module-label:
  .. table:: *I/O Control Module*

   +------+--------------------------------------+
   |Name  |Description                           |
   +======+======================================+
   |ioc.py|I/O Control processing for excel files|
   +------+--------------------------------------+

ioc.py
======

Static classes
--------------

The I/O Control Module ``ioc.py`` contains the following static classes.

  .. Static-classes-of-I/O-Control-module-ioc.py-label:
  .. table:: *Static Classes of I/O Control Module ioc.py*

   +-------+-----------------------------------------------------------------+
   |Name   |Description                                                      |
   +=======+=================================================================+
   |IocWbOp|Manage I/O control for excel workbooks using openpyxl package    |
   +-------+-----------------------------------------------------------------+
   |IocWbPe|Manage I/O control for excel workbooks using pyexcelerate package|
   +-------+-----------------------------------------------------------------+

IocWbOp
-------

Methods
^^^^^^^

  .. Methods-of-static-class-IocWbOp-label:
  .. table:: *Methods of static class IocWbOp Com*

   +----+----------------------------------------+
   |Name|Description                             |
   +====+========================================+
   |get |get Workbook using the openpyxel package|
   +----+----------------------------------------+

get
^^^

  .. Parameter-of-IocWbOp-method-get-label:
  .. table:: *Parameter of Com method sh_kwargs*

   +---------+-----+--------------------+
   |Name     |Type |Description         |
   +=========+=====+====================+
   |\**kwargs|TyAny|current class       |
   +---------+-----+--------------------+

  .. Return-value-of-IocWPep-method-get-label:
  .. table:: *Return value of IocWbPe method get*

   +----+------+---------------------+
   |Name|Type  |Description          |
   +====+======+=====================+
   |    |TyWbpP|pyexcelerate Workbook|
   +----+------+---------------------+

IocWbPe
-------

Methods
^^^^^^^

  .. Methods-of-static-class-IocWbPe-label:
  .. table:: *Methods of static class IocWbPe Com*

   +----+-------------------------------------------+
   |Name|Description                                |
   +====+===========================================+
   |get |get Workbook using the pyexcelerate package|
   +----+-------------------------------------------+

get
^^^

  .. Parameter-of-static-class-IocWbPe-method-get-label:
  .. table:: *Parameter of.static.class.IocWbPe.method.get*

   +---------+-----+--------------------+
   |Name     |Type |Description         |
   +=========+=====+====================+
   |\**kwargs|TyAny|current class       |
   +---------+-----+--------------------+

  .. Return-value-of-IocWbPe-method-get-label:
  .. table:: *Return value of IocWbPe method get*

   +----+------+---------------------+
   |Name|Type  |Description          |
   +====+======+=====================+
   |    |TyWbPe|pyexcelerate Workbook|
   +----+------+---------------------+

*****************
Input I/O Modules
*****************

Overview
========

  .. Input I/O-Modules-label:
  .. table:: *Input I/O Modules*

   +------------+-------------------------------------------------------+
   |Name        |Description                                            |
   +============+=======================================================+
   |ioipath.py  |Run Input I/O for excel workbooks accessed by path     |
   +------------+-------------------------------------------------------+
   |ioipathnm.py|Run Input I/O for excel workbooks accessed by path name|
   +------------+-------------------------------------------------------+

ioipath.py
==========

Static classes
--------------

The Input I/O Module ``ioipath.py`` contains the following static classes.

  .. Static-classes-of-Input-I/O-module-ioipath.py-label:
  .. table:: *Static Classes of Input I/O Module ioipath.py*

   +-----------+----------------------------------------+
   |Name       |Description                             |
   +===========+========================================+
   |IoiPathWbPd|Run Input I/O for excel workbooks       |
   |           |accessed by path using pandas package   |
   +-----------+----------------------------------------+
   |IoiPathWbPl|Run Input I/O for excel workbooks       |
   |           |accessed by path using polaris package  |
   +-----------+----------------------------------------+
   |IoiPathWbOp|Run Input I/O for excel workbooks       |
   |           |accessed by path using openpyxel package|
   +-----------+----------------------------------------+
   |IoiPathWsOp|Run Input I/O for excel worksheets      |
   |           |accessed by path using openpyxel package|
   +-----------+----------------------------------------+

ioipathnm.py
============

Static classes
--------------

The I/O Input Module ``ioipathnm.py`` contains the following static classes.

  .. Static-classes-of-I/O-Input-module-ioipathnm.py-label:
  .. table:: *Static Classes of I/O Input Module ioipathnm.py*

   +-------------+---------------------------------------------+
   |Name         |Description                                  |
   +=============+=============================================+
   |IoiPathnmWbPd|Run Input I/O for excel workbooks            |
   |             |accessed by path name using pandas package   |
   +-------------+---------------------------------------------+
   |IoiPathnmWbPl|Run Input I/O for excel workbooks            |
   |             |accessed by path name using polaris package  |
   +-------------+---------------------------------------------+
   |IoiPathnmWbOp|Run Input I/O for excel workbooks            |
   |             |accessed by path name using openpyxel package|
   +-------------+---------------------------------------------+
   |IoiPathnmWsOp|Run Input I/O for excel worksheets           |
   |             |accessed by path name using openpyxel package|
   +-------------+---------------------------------------------+

******************
Output I/O Modules
******************

Overview
========

  .. Output-I/O-Modules-label:
  .. table:: *Output I/O Modules*

   +----------+-----------------------------------------------------------------+
   |Name      |Description                                                      |
   +==========+=================================================================+
   |ioowbop.py|Run Output I/O for excel workbooks using the openpyxel package   |
   +----------+-----------------------------------------------------------------+
   |ioowbpd.py|Run Output I/O for excel workbooks using the pandas package      |
   +----------+-----------------------------------------------------------------+
   |ioowbpe.py|Run Output I/O for excel workbooks using the pyexcelerate package|
   +----------+-----------------------------------------------------------------+

ioowbop.py
==========

Static classes
--------------

The Output I/O Module ``ioowbop.py`` contains the following static classes.

  .. Static-classes-of-Output-I/O-module-ioowbop.py-label:
  .. table:: *Static Classes of Output I/O Module ioowbop.py*

   +-------------+---------------------------------------------------+
   |Name         |Description                                        |
   +=============+===================================================+
   |IooPathWbOp  |Run Output I/O for excel workbook to file          |
   |             |referenced by path using the openpyxel package     |
   +-------------+---------------------------------------------------+
   |IooPathnmWbOp|Run Output I/O for excel workbook to file          |
   |             |referenced by path name using the openpyxel package|
   +-------------+---------------------------------------------------+

ioowbpd.py
==========

Static classes
--------------

The Output I/O Module ``ioowbpd.py`` contains the following static classes.

  .. Static-classes-of-Output-I/O--module-ioowbpd.py-label:
  .. table:: *Static Classes of Output I/O Module ioowbpd.py*

   +-----------+-------------------------------------------------+
   |Name       |Description                                      |
   +===========+=================================================+
   |IooPathPdDf|Run Output I/O for pandas dataframe to excel file|
   |           |referenced by path using the pandas writer       |
   +-----------+-------------------------------------------------+

ioowbpe.py
==========

Static classes
--------------

The I/O Output Module ``ioowbpe.py`` contains the following static classes.

  .. Static-classes-of-Output-I/O-module-ioowbpe.py-label:
  .. table:: *Static Classes of Output I/O Module ioowbpe.py*

   +-------------+------------------------------------------------------+
   |Name         |Description                                           |
   +=============+======================================================+
   |IooPathWbPe  |Run Output I/O for excel workbook to file             |
   |             |referenced by path using the pyexcelerate package     |
   +-------------+------------------------------------------------------+
   |IooPathnmWbPe|Run Output I/O for excel workbook to file             |
   |             |referenced by path name using the pyexcelerate package|
   +-------------+------------------------------------------------------+

ioupath.py
==========

Static classes
--------------

The I/O Update Module ``ioupath.py`` contains the following static class.

  .. Static-class-of-Update-I/O-module-ioupath.py-label:
  .. table:: *Static Class of Update I/O Module ioupath.py*

   +-----------+---------------------------------------------------+
   |Name       |Description                                        |
   +===========+===================================================+
   |IouPathWbOp|Run Update I/O of Excel template referenced by path|
   |           |by object using the openpyxel package              |
   +-----------+---------------------------------------------------+

Workbook Modules using the package openpyxel 
============================================

Overview
========

  .. Workbook-Module-using-the-package-openpyxel-label:
  .. table:: **Workbook Module using the package openpyxel**

   +-------+-----------------------------------------------------+
   |Name   |Description                                          |
   +=======+=====================================================+
   |wbop.py|Excel Workbook management using the openpyxel package|
   +-------+-----------------------------------------------------+

wbop.py
=======

Classes
-------

The Workbook Module ``wbop.py`` contains the following static class.

  .. Static-class-of-Workbook-module-wbop.py-label:
  .. table:: *Static class of Workbook Module wbop.py*

   +----+-----------------------------------------------------+
   |Name|Description                                          |
   +====+=====================================================+
   |WbOp|Excel Workbook processing using the openpyxel package|
   +----+-----------------------------------------------------+

***********************************************
Workbook Modules using the package pyexcelerate
***********************************************

Overview
========

  .. Workbook-Module-using-the-package-pyexcelerate-label:
  .. table:: **Workbook Module using the package pyexcelerate**

   +-------+--------------------------------------------------------+
   |Name   |Description                                             |
   +=======+========================================================+
   |wbpe.py|Excel Workbook management using the pyexcelerate package|
   +-------+--------------------------------------------------------+

wbpe.py
=======

Classes
-------

The Workbook Module ``wbpe.py`` contains the following static class.

  .. Static-class-of-Workbook-module-wbpe.py-label:
  .. table:: *Static class of Workbook Module wbpe.py*

   +----+--------------------------------------------------------+
   |Name|Description                                             |
   +====+========================================================+
   |WbPe|Excel Workbook processing using the pyexcelerate package|
   +----+--------------------------------------------------------+

*********************************************
Worksheet Modules using the package openpyxel
*********************************************

Overview
========

  .. Worksheet-Module-using-the-package-openpyxel-label:
  .. table:: **Worksheet-Module-using-the-package-openpyxel**

   +-------+-----------------------------------------------------+
   |Name   |Description                                          |
   +=======+=====================================================+
   |wbpe.py|Excel Worksheet management using the openpyxl package|
   +-------+-----------------------------------------------------+

wsop.py
=======

Classes
-------

The Worksheet Module ``wsop.py`` contains the following static class.

  .. Static-class-of-Worksheet-module-wsop.py-label:
  .. table:: *Static class of Worksheet Module wsop.py*

   +----+------------------------------------------------------+
   |Name|Description                                           |
   +====+======================================================+
   |WsOp|Excel Worksheet processing using the openpyxel package|
   +----+------------------------------------------------------+

****************************************
Cell Modules using the package openpyxel
****************************************

Overview
========

  .. Cell-Module-using-the-package-openpyxel-label:
  .. table:: **Cell-Module-using-the-package-openpyxel**

   +-------+----------------------------------------------------+
   |Name   |Description                                         |
   +=======+====================================================+
   |rwop.py|Excel Cell management using the pyexcelerate package|
   +-------+----------------------------------------------------+

rwop.py
=======

Classes
-------

The Cell Module ``rwop.py`` contains the following static class.

  .. Static-class-of-Cell-module-wsop.py-label:
  .. table:: *Static class of Cell Module wsop.py*

   +----+-------------------------------------------------+
   |Name|Description                                      |
   +====+=================================================+
   |RwOp|Excel Cell processing using the openpyxel package|
   +----+-------------------------------------------------+

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
