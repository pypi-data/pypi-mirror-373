######
ut_xml
######

Overview
********

.. start short_desc

**Utilities for Application Setup and Package Management**

.. end short_desc

Installation
************

.. start installation

The package ``ut_xml`` can be installed from PyPI or Anaconda.

To install with ``pip``:

.. code-block:: shell

	$ python -m pip install ut_xml

.. end installation

Package logging 
***************

(c.f.: **Appendix**: `Package Logging`)

Package files
*************

Classification
==============

The Package ``ut_xml`` consist of the following file types (c.f.: **Appendix**):

#. **Special files:** (c.f.: **Appendix:** *Special python package files*)

#. **Dunder modules:** (c.f.: **Appendix:** *Special python package modules*)

#. **Modules**

   a. *aob.py*
   a. *aox.py*
   #. *xml_.py*

Modules
*******

The Package ``ut_xml`` contains the following Modules.

  .. ut_xml-Modules-label:
  .. table:: *ut_xml Modules*

   +-------------+-----------------------+
   |Name         |Decription             |
   +=============+=======================+
   |aob.py       |Array of Bytes         |
   +-------------+-----------------------+
   |aox.py       |Array of Xml Objects   |
   +-------------+-----------------------+
   |xml2dic2.py  |Xml to dic migration   |
   +-------------+-----------------------+
   |xml2dicapc.py|Xml to dicapc migration|
   +-------------+-----------------------+
   |xml2dic.py   |Xml to dic migration   |
   +-------------+-----------------------+
   |xml\_.py     |Xml management         |
   +-------------+-----------------------+

Module: aob.py
==============

The Module ``aob.py`` contains the static class ``AoB``

aob.py Class: AoB
-----------------

The static Class ``AoB`` provides methods to manage Array of Bytes;
it contains the subsequent methods.

AoB Methods
^^^^^^^^^^^

  .. AoB-Methods-label:
  .. table:: *AoB Methods*

   +---------+------------------+
   |Name     |Description       |
   +=========+==================+
   |to_bytes |Create byte string|
   +---------+------------------+
   |to_dic   |Create dictionary |
   +---------+------------------+
   |to_string|Create string     |       
   +---------+------------------+

AoB Method: to_bytes
""""""""""""""""""""

Parameter
.........

  .. AoB-Method-to_bytes-Parameter-label:
  .. table:: *AoB Method to_bytes: Parameter*

   +----+-----+--------------+
   |Name|Type |Description   |
   +====+=====+==============+
   |aob |TyAoB|Array of bytes|
   +----+-----+--------------+

Return Value
............

  .. AoB-Method-to_byte-Return-Value-label:
  .. table:: *AoB Method to_byte: Return Value*

   +----+-------+-----------+
   |Name|Type   |Description|
   +====+=======+===========+
   |    |TyBytes|Byte string|
   +----+-------+-----------+

AoB Method: to_dic
""""""""""""""""""

Parameter
.........

  .. AoB-Method-to_dic-Parameter-label:
  .. table:: *AoB Method to_dic: Parameter*

   +----+-----+--------------+
   |Name|Type |Description   |
   +====+=====+==============+
   |aob |TyStr|Array of bytes|
   +----+-----+--------------+

Return Value
............

  .. AoB-Method-to_dic-Return-Value-label:
  .. table:: *AoB Method to_dic: Return Value*

   +----+-----+-----------+
   |Name|Type |Description|
   +====+=====+===========+
   |    |TyDic|Dictionary |
   +----+-----+-----------+

AoB Method: to_string
"""""""""""""""""""""

Parameter
.........

  .. AoB-Method-to_string-Parameter-label:
  .. table:: *AoB Method to_string: Parameter*

   +----+-----+--------------+
   |Name|Type |Description   |
   +====+=====+==============+
   |aob |TyStr|Array of bytes|
   +----+-----+--------------+

Return Value
............

  .. AoB-Method-to_string-Return-Value-label:
  .. table:: *AoB Method to_string: Return Value*

   +----+-----+-----------+
   |Name|Type |Description|
   +====+=====+===========+
   |    |TyStr|string     |
   +----+-----+-----------+

Module: aox.py
==============

The Module ``aox.py`` contains the static class ``AoX``

aox.py Class: AoX
-----------------

The static Class ``AoX`` provides methods to manage Array of Xml Objects;
it contains the subsequent methods.

AoX Methods
^^^^^^^^^^^

  .. AoX-Methods-label:
  .. table:: *AoX Methods*

   +-------+---------------------+
   |Name   |Description          |
   +=======+=====================+
   |to_aob |Create array of bytes|
   +-------+---------------------+
   |to_byte|Create byte string   |
   +-------+---------------------+

AoX Method: to_aob
""""""""""""""""""

Parameter
.........

  .. AoX-Method-to_aob-Parameter-label:
  .. table:: *AoX Method to_aob: Parameter*

   +----+-----+--------------------+
   |Name|Type |Description         |
   +====+=====+====================+
   |aox |TyAoX|Array of Xml objects|
   +----+-----+--------------------+

Return Value
............

  .. AoX-Method-to_aob-Return-Value-label:
  .. table:: *AoX Method to_aob: Return Value*

   +----+-----+---------------------+
   |Name|Type |Description          |
   +====+=====+=====================+
   |    |TyAoB|Array of byte strings|
   +----+-----+---------------------+

AoX Method: to_byte
"""""""""""""""""""

Parameter
.........

  .. AoX-Method-to_byte-Parameter-label:
  .. table:: *AoX Method to_byte: Parameter*

   +----+-----+--------------------+
   |Name|Type |Description         |
   +====+=====+====================+
   |aox |TyAoX|Array of Xml objects|
   +----+-----+--------------------+

Return Value
............

  .. AoX-Method-to_byte-Return-Value-label:
  .. table:: *AoX Method to_byte: Return Value*

   +----+------+-----------+
   |Name|Type  |Description|
   +====+======+===========+
   |    |TyByte|Byte string|
   +----+------+-----------+

Appendix
********

Package Logging
===============

Description
-----------

The Standard or user specifig logging is carried out by the log.py module of the logging
package ka_uts_log using the configuration files **ka_std_log.yml** or **ka_usr_log.yml**
in the configuration directory **cfg** of the logging package **ka_uts_log**.
The Logging configuration of the logging package could be overriden by yaml files with
the same names in the configuration directory **cfg** of the application packages.

Log message types
-----------------

Logging defines log file path names for the following log message types: .

#. *debug*
#. *info*
#. *warning*
#. *error*
#. *critical*

Application parameter for logging
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  .. Application-parameter-used-in-log-naming-label:
  .. table:: *Application parameter used in log naming*

   +-----------------+---------------------------+----------+------------+
   |Name             |Decription                 |Values    |Example     |
   +=================+===========================+==========+============+
   |dir_dat          |Application data directory |          |/otev/data  |
   +-----------------+---------------------------+----------+------------+
   |tenant           |Application tenant name    |          |UMH         |
   +-----------------+---------------------------+----------+------------+
   |package          |Application package name   |          |otev_xls_srr|
   +-----------------+---------------------------+----------+------------+
   |cmd              |Application command        |          |evupreg     |
   +-----------------+---------------------------+----------+------------+
   |pid              |Process ID                 |          |æevupreg    |
   +-----------------+---------------------------+----------+------------+
   |log_ts_type      |Timestamp type used in     |ts,       |ts          |
   |                 |logging files|ts, dt       |dt        |            |
   +-----------------+---------------------------+----------+------------+
   |log_sw_single_dir|Enable single log directory|True,     |True        |
   |                 |or multiple log directories|False     |            |
   +-----------------+---------------------------+----------+------------+

Log type and Log directories
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

Log files naming
^^^^^^^^^^^^^^^^

Naming Conventions
""""""""""""""""""

  .. Naming-conventions-for-logging-file-paths-label:
  .. table:: *Naming conventions for logging file paths*

   +--------+-------------------------------------------------------+-------------------------+
   |Type    |Directory                                              |File                     |
   +========+=======================================================+=========================+
   |debug   |/<dir_dat>/<tenant>/RUN/<package>/<cmd>/<Log directory>|<Log type>_<ts>_<pid>.log|
   +--------+-------------------------------------------------------+-------------------------+
   |info    |/<dir_dat>/<tenant>/RUN/<package>/<cmd>/<Log directory>|<Log type>_<ts>_<pid>.log|
   +--------+-------------------------------------------------------+-------------------------+
   |warning |/<dir_dat>/<tenant>/RUN/<package>/<cmd>/<Log directory>|<Log type>_<ts>_<pid>.log|
   +--------+-------------------------------------------------------+-------------------------+
   |error   |/<dir_dat>/<tenant>/RUN/<package>/<cmd>/<Log directory>|<Log type>_<ts>_<pid>.log|
   +--------+-------------------------------------------------------+-------------------------+
   |critical|/<dir_dat>/<tenant>/RUN/<package>/<cmd>/<Log directory>|<Log type>_<ts>_<pid>.log|
   +--------+-------------------------------------------------------+-------------------------+

Naming Examples
"""""""""""""""

  .. Naming-examples-for-logging-file-paths-label:
  .. table:: *Naming examples for logging file paths*

   +--------+--------------------------------------------+------------------------+
   |Type    |Directory                                   |File                    |
   +========+============================================+========================+
   |debug   |/data/otev/umh/RUN/otev_xls_srr/evupreg/logs|debs_1737118199_9470.log|
   +--------+--------------------------------------------+------------------------+
   |info    |/data/otev/umh/RUN/otev_xls_srr/evupreg/logs|infs_1737118199_9470.log|
   +--------+--------------------------------------------+------------------------+
   |warning |/data/otev/umh/RUN/otev_xls_srr/evupreg/logs|wrns_1737118199_9470.log|
   +--------+--------------------------------------------+------------------------+
   |error   |/data/otev/umh/RUN/otev_xls_srr/evupreg/logs|errs_1737118199_9470.log|
   +--------+--------------------------------------------+------------------------+
   |critical|/data/otev/umh/RUN/otev_xls_srr/evupreg/logs|crts_1737118199_9470.log|
   +--------+--------------------------------------------+------------------------+

Python Terminology
==================

Python packages
---------------

  .. Python packages-label:
  .. table:: *Python packages*

   +-----------+-----------------------------------------------------------------+
   |Name       |Definition                                                       |
   +===========+==========+======================================================+
   |Python     |Python packages are directories that contains the special module |
   |package    |``__init__.py`` and other modules, packages files or directories.|
   +-----------+-----------------------------------------------------------------+
   |Python     |Python sub-packages are python packages which are contained in   |
   |sub-package|another pyhon package.                                           |
   +-----------+-----------------------------------------------------------------+

Python package Sub-directories
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  .. Python package-Sub-directories-label:
  .. table:: *Python packages Sub-directories*

   +----------------------+-------------------------------+
   |Name                  |Definition                     |
   +======================+==========+====================+
   |Python package        |Sub-directories are directories|
   |sub-directory         |contained in python packages.  |
   +----------------------+-------------------------------+
   |Special Python package|Python package sub-directories |
   |sub-directory         |with a special meaning.        |
   +----------------------+-------------------------------+

Special python package Sub-directories
""""""""""""""""""""""""""""""""""""""

  .. Special-python-package-Sub-directories-label:
  .. table:: *Special python Sub-directories*

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

Python package files
^^^^^^^^^^^^^^^^^^^^

  .. Python-package-files-label:
  .. table:: *Python package files*

   +--------------+---------------------------------------------------------+
   |Name          |Definition                                               |
   +==============+==========+==============================================+
   |Python        |Files within a python package.                           |
   |package files |                                                         |
   +--------------+---------------------------------------------------------+
   |Special python|Package files which are not modules and used as python   |
   |package files |and used as python marker files like ``__init__.py``.    |
   +--------------+---------------------------------------------------------+
   |Python package|Files with suffix ``.py``; they could be empty or contain|
   |module        |python code; other modules can be imported into a module.|
   +--------------+---------------------------------------------------------+
   |Special python|Modules like ``__init__.py`` or ``main.py`` with special |
   |package module|names and functionality.                                 |
   +--------------+---------------------------------------------------------+

Special python package files
""""""""""""""""""""""""""""

  .. Special-python-package-files-label:
  .. table:: *Special python package files*

   +--------+--------+---------------------------------------------------------------+
   |Name    |Type    |Description                                                    |
   +========+========+===============================================================+
   |py.typed|Type    |The ``py.typed`` file is a marker file used in Python packages |
   |        |checking|to indicate that the package supports type checking. This is a |
   |        |marker  |part of the PEP 561 standard, which provides a standardized way|
   |        |file    |to package and distribute type information in Python.          |
   +--------+--------+---------------------------------------------------------------+

Special python package modules
""""""""""""""""""""""""""""""

  .. Special-Python-package-modules-label:
  .. table:: *Special Python package modules*

   +--------------+-----------+-----------------------------------------------------------------+
   |Name          |Type       |Description                                                      |
   +==============+===========+=================================================================+
   |__init__.py   |Package    |The dunder (double underscore) module ``__init__.py`` is used to |
   |              |directory  |execute initialisation code or mark the directory it contains as |
   |              |marker     |a package. The Module enforces explicit imports and thus clear   |
   |              |file       |namespace use and call them with the dot notation.               |
   +--------------+-----------+-----------------------------------------------------------------+
   |__main__.py   |entry point|The dunder module ``__main__.py`` serves as an entry point for   |
   |              |for the    |the package. The module is executed when the package is called by|
   |              |package    |the interpreter with the command **python -m <package name>**.   |
   +--------------+-----------+-----------------------------------------------------------------+
   |__version__.py|Version    |The dunder module ``__version__.py`` consist of assignment       |
   |              |file       |statements used in Versioning.                                   |
   +--------------+-----------+-----------------------------------------------------------------+

Python elements
---------------

  .. Python elements-label:
  .. table:: *Python elements*

   +---------------------+--------------------------------------------------------+
   |Name                 |Description                                             |
   +=====================+========================================================+
   |Python method        |Python functions defined in python modules.             |
   +---------------------+--------------------------------------------------------+
   |Special python method|Python functions with special names and functionalities.|
   +---------------------+--------------------------------------------------------+
   |Python class         |Classes defined in python modules.                      |
   +---------------------+--------------------------------------------------------+
   |Python class method  |Python methods defined in python classes                |
   +---------------------+--------------------------------------------------------+

Special python methods
^^^^^^^^^^^^^^^^^^^^^^

  .. Special-python-methods-label:
  .. table:: *Special python methods*

   +--------+------------+----------------------------------------------------------+
   |Name    |Type        |Description                                               |
   +========+============+==========================================================+
   |__init__|class object|The special method ``__init__`` is called when an instance|
   |        |constructor |(object) of a class is created; instance attributes can be|
   |        |method      |defined and initalized in the method.                     |
   +--------+------------+----------------------------------------------------------+

Table of Contents
=================

.. contents:: **Table of Content**
