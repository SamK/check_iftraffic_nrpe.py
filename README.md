check_iftraffic_nrpe.py
=======================

This is a Nagios plugin to check network traffic with NRPE on Linux.
This script has been created because I like writing Python scripts.

Installation
--------

* The latest stable release can be found here: https://github.com/samyboy/check_iftraffic_nrpe.py/releases
* Copy the file `check_iftraffic_nrpe.py` into the appropriate Nagios folder (example: `/usr/lib/nagios/plugins/`)

Prerequisites
-------------

* Python 2.x
* The python-argparse library

Compatibility
-------------

This script has been tested under Python 2.x only.
I don't know if it works unders Python 3.

This script has been tested under Nagios 3.x only.
I have no idea how it behaves with older versions.

Usage examples
--------------

How to get some help:

    check_iftraffic_nrpe.py --help

Query all interfaces except the loopback interface:

    check_iftraffic_nrpe.py -x lo

Query only eth1:

    check_iftraffic_nrpe.py -i eth1

Set warning value to 80% (default: warning=85, critical=98):

    check_iftraffic_nrpe.py -w 80

Define a Gigabit interface (the value must be in bytes):

    check_iftraffic_nrpe.py --bandwidth=131072000


Contributing
------------

* Submit bugs if you find some.
* Submit pull requests and I will happily merge them *when I have free time*.
Note that I must understand your code.

Development
----------

* Print library documentation

    LIB="check_iftraffic_nrpe" ;  python -c "import sys; sys.path.insert(0,'.'); import $LIB; import pydoc; pydoc.doc($LIB)"

* Check Python syntax

    pylint -E file.py

* Follow PEP8 style guide

    pep8 --ignore=E111,E221,E701 --show-source --show-pep8 check_iftraffic_nrpe.py

Author
------

Samuel Krieg <my_first_name.my_last_name at gmail dot com>

