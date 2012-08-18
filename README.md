check_iftraffic_nrpe
====================

Nagios plugin to check network traffic with NRPE on Linux.

Prerequisites
-------------

* Python
* The argparse library: `apt-get install python-argparse`

Usage examples
--------------

How to get some help:

    check_iftraffic_nrpe.py --help

Query all interfaces except the loopback interface

    check_iftraffic_nrpe.py -x lo

Query only eth1

    check_iftraffic_nrpe.py -i eth1

Set warning value to 80% (default: warning=85, critical=98)

    check_iftraffic_nrpe.py -w 80

Define a Gigabit interface (the value must be in bytes).

    check_iftraffic_nrpe.py --bandwidth=131072000


