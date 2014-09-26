#!/bin/bash
set -e

#echo test for Python 2.4
#source ~/.virtualenv/env-2.4/bin/activate
#./unittests/unittests.py
#deactivate

echo test for local python
/usr/bin/python ./unittests/unittests.py

echo test for Python 2.7.3
source ~/.virtualenv/env-2.7.3/bin/activate
./unittests/unittests.py
deactivate

echo test for Python 3.4
source ~/.virtualenv/pyvenv-3.4/bin/activate
./unittests/unittests.py
deactivate
