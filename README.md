# check_iftraffic_nrpe.py

This is a Nagios plugin to check network traffic with NRPE on Linux.
This script has been created because I like writing Python scripts.

Here are some of the features:

 * available units: (kilo|Mega|Giga|Tera)(Bytes|bits)
 * excludes or includes interfaces based on name, regexp or type (type can be: "ethernet", "ppp", "loopback" or "sit")
 * understands computer reboots
 * understand counter resets (32bits or 64bits)

## Installation

### Manual installation

* The latest stable release can be found here: https://github.com/SamK/check_iftraffic_nrpe.py/releases
* Copy the file `check_iftraffic_nrpe.py` into your favorite folder (examples: `/usr/lib/nagios/plugins/, /usr/local/bin)

### Package installation

    pip install check_iftraffic_nrpe

## Prerequisites

* Python
* The python-argparse library

## Compatibility

* Tested under Python versions 2.7 and 3.4
* It is not compatible with Python 2.4: See issue #21
* It has been tested under Nagios 3.x only.

## Usage examples

How to get some help:

    check_iftraffic_nrpe.py --help

Query all interfaces except the loopback interface:

    check_iftraffic_nrpe.py -x lo

Query only eth1:

    check_iftraffic_nrpe.py -i eth1

Set warning value to 80% (default: warning=85, critical=98):

    check_iftraffic_nrpe.py -w 80

Define a Gigabit interface.
All commands below define the same bandwith but output different units of metrics.

    check_iftraffic_nrpe.py --bandwidth=125000     # default unit is Bps
    check_iftraffic_nrpe.py --bandwidth=125        --unit=kBps
    check_iftraffic_nrpe.py --bandwidth=0.125000   --unit=MBps
    check_iftraffic_nrpe.py --bandwidth=1          --unit=Gbps
    check_iftraffic_nrpe.py --bandwidth=1000       --unit=Mbps
    check_iftraffic_nrpe.py --bandwidth=1000000    --unit=kbps
    check_iftraffic_nrpe.py --bandwidth=1000000000 --unit=bps


## Contributing

* Submit bugs if you find some.
* Submit pull requests and I will happily merge them *when I have free time*.
Note that I must understand your code.

## Development

Print library documentation:

    pydoc ./check_iftraffic_nrpe.py

Testing the code:

    ./tests/run.sh

This script will download and create all the appropriate Python versions and virtual environnements.

## Author

Samuel Krieg <my_first_name.my_last_name at gmail dot com>

### Contributors

@georgehansper, @hgrohne-cygnusnetworks-de, @tbc

