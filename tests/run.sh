#!/bin/bash
#set -x
set -e

function h1() {
    echo $@
    echo "==========="
}

function h2() {
    echo $@
    echo "-----------"
}

LOCAL_PATH=$HOME/.local
VENV_PATH=$HOME/.virtualenv_iftraffic

# python 2.x
function create_venv() {
    h2 Creating venv with : "virtualenv --python=$1 $2"
    virtualenv --python=$1 $2
    h2 sourcing from $2
    source $2/bin/activate
    h2 installing components
    pip install pep8
    pip install argpase
    h2 deactivating
    deactivate
}

# python 3.x
function create_pyvenv() {
    h2 Creating pyvenv $2 with $1
    $1 $2
    h2 sourcing from $2
    source $2/bin/activate
    h2 installing components
    pip install pep8
    pip install argparse
    h2 deactivating
    deactivate
}

function run_tests() {
    h2 activating $1
    source $1/bin/activate
    h2 pylint
    $PYTHON_BIN pylint -E ./check_iftraffic_nrpe.py
    set +e
    $PYTHON_BIN pylint -r n ./check_iftraffic_nrpe.py
    set -e
    h2 pep8
    $PYTHON_BIN pep8 --ignore=E111,E221,E701,E127 --show-source --show-pep8 ./check_iftraffic_nrpe.py
    h2 unittests
    ./tests/unittests.py
    h2 deactivating
    deactivate
}

PYTHON_BIN=$LOCAL_PATH/bin/python2.4
VENV_NAME=env-2.4
h1 "Running tests for $PYTHON_BIN"
create_venv $PYTHON_BIN $VENV_PATH/$VENV_NAME
run_tests $VENV_PATH/$VENV_NAME

PYTHON_BIN=$LOCAL_PATH/bin/python2.7
VENV_NAME="env-2.7"
h1 "Running tests for $PYTHON_BIN"
create_venv $PYTHON_BIN $VENV_PATH/$VENV_NAME
run_tests $VENV_PATH/$VENV_NAME

# python 3.4
PYTHON_BIN=$LOCAL_PATH/bin/python3.4
VENV_NAME="pyvenv-3.4"
h1 "Running tests for $PYTHON_BIN"
create_pyvenv $PYTHON_BIN $VENV_PATH/$VENV_NAME
run_tests $PYTHON_BIN $VENV_PATH/$VENV_NAME


