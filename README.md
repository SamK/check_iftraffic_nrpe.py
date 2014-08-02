check_iftraffic_nrpe.py
=======================

This is a Nagios plugin to check network traffic with NRPE on Linux.
This script has been created because I like writing Python scripts.
It returns perfdata values in B/s (bytes per seconds).

Installation
--------

* The latest stable release can be found here: https://github.com/samyboy/check_iftraffic_nrpe.py/releases
* Copy the file `check_iftraffic_nrpe.py` into your favorite folder (examples: `/usr/lib/nagios/plugins/, /usr/local/bin)

Prerequisites
-------------

* Python
* The python-argparse library

Compatibility
-------------

* This script has been tested under Python 2.7 only.
* It is not compatible with Python 2.4
* It has been tested under Nagios 3.x only.

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

Print library documentation:

    pydoc ./check_iftraffic_nrpe.py

Testing the code:

    # Check Python syntax
    pylint -E check_iftraffic_nrpe.py
    # Follow PEP8 style guide:
    pep8 --ignore=E111,E221,E701 --show-source --show-pep8 check_iftraffic_nrpe.py
    # Execute unit tests
    ./unittests/unittests.py
    # Crazy lint
    pylint -r n check_iftraffic_nrpe.py


Author
------

Samuel Krieg <my_first_name.my_last_name at gmail dot com>

