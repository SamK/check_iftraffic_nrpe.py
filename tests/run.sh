#!/bin/bash
set -e

echo "Pylint errors"
echo "============="

pylint -E ./check_iftraffic_nrpe.py

echo "Pylint notifications"
echo "===================="

set +e
pylint -r n ./check_iftraffic_nrpe.py
set -e

echo "pep8"
echo "===="

pep8 --ignore=E111,E221,E701 --show-source --show-pep8 ./check_iftraffic_nrpe.py

echo "Unit tests"
echo "=========="

#echo test for Python 2.4
#source ~/.virtualenv/env-2.4/bin/activate
#./unittests/unittests.py
#deactivate

# test for local python
/usr/bin/python ./unittests/unittests.py

# test for Python 2.7.3
source ~/.virtualenv/env-2.7.3/bin/activate
./unittests/unittests.py
deactivate

# test for Python 3.4
source ~/.virtualenv/pyvenv-3.4/bin/activate
./unittests/unittests.py
deactivate
