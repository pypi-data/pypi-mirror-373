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
   +----+-------------------+----------------------------------------------------------+
   |Type|Directory Type     |File                                                      |
   +====+===================+==========================================================+
   |std |Log package        |<Site-packages-path>/<Log-package>/cfg/log.std.yml        |
   |    +-------------------+----------------------------------------------------------+
   |    |Application package|<Site-packages-path>/<application-package>/cfg/log.std.yml|
   |    +-------------------+----------------------------------------------------------+
   |    |Application        |<application-home-path>/cfg/log.std.yml                   |
   +----+-------------------+----------------------------------------------------------+
   |usr |Log package        |<site-packages-path>/ut_log/cfg/log.std.yml               |
   |    +-------------------+----------------------------------------------------------+
   |    |Application package|<site-packages-path>/ui_eviq_srr/cfg/log.usr.yml          |
   |    +-------------------+----------------------------------------------------------+
   |    |Application        |<application-path>/cfg/log.usr.yml                        |
   +----+-------------------+----------------------------------------------------------+

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

   +-----------------+-------------------------------+-------+-------+---------------+
   |Name             |Decription                     |Range  |Default|Example        |
   +=================+===============================+=======+=======+===============+
   |appl_data        |Application data directory     |       |       |/data/eviq     |
   +-----------------+-------------------------------+-------+-------+---------------+
   |tenant           |Application tenant name        |       |       |UMH            |
   +-----------------+-------------------------------+-------+-------+---------------+
   |package          |Application package name       |       |       |ui_eviq_srr    |
   +-----------------+-------------------------------+-------+-------+---------------+
   |cmd              |Application command            |       |       |evupreg        |
   +-----------------+-------------------------------+-------+-------+---------------+
   |pid              |Process ID                     |       |       |681025         |
   +-----------------+-------------------------------+-------+-------+---------------+
   |log_type         |Standard logging               |std    |std    |std            |
   |                 +-------------------------------+-------+       |               |
   |                 |Personal logging               |usr    |       |               |
   +-----------------+-------------------------------+-------+-------+---------------+
   |log_ts_type      |Seconds since 1.1.1970|ts      |ts     |ts     |ts             |
   |                 +-------------------------------+-------+       |               |
   |                 |Datetime                       |dt     |       |               |
   +-----------------+-------------------------------+-------+-------+---------------+
   |ts               |if ts_type == ts               |       |       |1750096540     |
   |                 +-------------------------------+-------+-------+---------------+
   |                 |if ts_type == dt               |       |       |20250618.203010|
   +-----------------+-------------------------------+-------+-------+---------------+
   |log_sw_single_dir|Enable single log directory    |True   |True   |True           |
   |                 +-------------------------------+-------+       |               |
   |                 |Enable multiple log directories|False  |       |               |
   +-----------------+-------------------------------+-------+-------+---------------+

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
   +--------+--------------------------------------------+--------------------------+
   |error   |/appl/eviq/UMH/RUN/ui_eviq_srr/evdomap/logs/|errs_1749971151_240257.log|
   +--------+--------------------------------------------+--------------------------+
   |info    |/appl/eviq/UMH/RUN/ui_eviq_srr/evdomap/logs/|infs_1750096540_354710.log|
   +--------+--------------------------------------------+--------------------------+
   |warning |/appl/eviq/UMH/RUN/ui_eviq_srr/evdomap/logs/|wrns_1749971151_240257.log|
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

   +----------------+------------------------------+-------------------------------------------+
   |Name            |Definition                    |Example                                    |
   +================+==============================+===========================================+
   |{{dir_run_debs}}|debug run directory           |/data/eviq/UMH/RUN/ui_eviq_srr/evupreg/debs|
   +----------------+------------------------------+-------------------------------------------+
   |{{dir_run_infs}}|info run directory            |/data/eviq/UMH/RUN/ui_eviq_srr/evupreg/logs|
   +----------------+------------------------------+-------------------------------------------+
   |{{dir_run_wrns}}|warning run directory         |/data/eviq/UMH/RUN/ui_eviq_srr/evupreg/logs|
   +----------------+------------------------------+-------------------------------------------+
   |{{dir_run_errs}}|error run directory           |/data/eviq/UMH/RUN/ui_eviq_srr/evupreg/logs|
   +----------------+------------------------------+-------------------------------------------+
   |{{dir_run_crts}}|critical error run directory  |/data/eviq/UMH/RUN/ui_eviq_srr/evupreg/logs|
   +----------------+------------------------------+-------------------------------------------+
   |{{ts}}          |**if log_ts_type == 'ts'**    |1749483509                                 |
   |                |Timestamp since 1970 in [sec] |                                           |
   |                +------------------------------+-------------------------------------------+
   |                |**if log_ts_type == 'dt'**    |20250609 17:38:29 GMT+0200                 |
   |                |Datetime in tz 'Europe/Berlin'|                                           |
   +----------------+------------------------------+-------------------------------------------+
   |{{pid}}         |Process ID                    |79133                                      |
   +----------------+------------------------------+-------------------------------------------+
