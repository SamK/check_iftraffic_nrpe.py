#!/bin/bash
#set -x
set -e

## Directories
# tests directory
BINTESTS_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Root directory
ROOT_PATH=$( dirname $BINTESTS_PATH )
# Where to put all the builds
BUILDS_PATH="${ROOT_PATH}/builds"
mkdir -p "$BUILDS_PATH"
# python binaries
PYTHON_PATH=$BUILDS_PATH/python
# virtualenv directories
VENV_PATH=$BUILDS_PATH/virtualenv
# downlads
TMP=$BUILDS_PATH/tmp

## Parameters

# Common name of the tarball
PKG_PREFIX="Python"

# Final output of the tests
FINAL_MSG=''

function execute(){
    # Prints the command line before executing a command
    echo -en "\e[32m"
    echo -e "> \"$*\""
    echo -en "\e[0m"
    $*
}

function h1() {
    # Header 1
    echo -en "\e[32m"
    echo $@
    echo "==========="
    echo -en "\e[0m"
}

function h2() {
    # Header 2
    echo -en "\e[32m"
    echo $@
    echo "-----------"
    echo -en "\e[0m"
}

function short_version(){
    # Return the short version of a Python version
    local long_version=$1
    local short_version="${long_version%.*}"
    echo $short_version
}

function download_python() {
    # download python based on the version
    local version=$1
    local foldername=$PKG_PREFIX-$version
    local pkgname=$foldername.tgz

    if [ ! -f "/${TMP}/${pkgname}" ]; then
        h2 Downloading Python $version
        execute cd $TMP
        execute wget -q https://www.python.org/ftp/python/$version/$pkgname
    fi
}

function install_python(){
    # install python based on the version
    local version=$1
    local short_version=$( short_version $version )
    local configure_opts=''
    if [ ! -f $PYTHON_PATH/bin/python${short_version} ]; then
        h2 installing Python $version
        execute cd $TMP
        execute tar xzf $PKG_PREFIX-$version.tgz
        execute cd $PKG_PREFIX-$version
        [ "$short_version" == "2.4" -o "$short_version" == "2.7" ] && sed -i 's/^#zlib/zlib/' Modules/Setup.dist
        [ "$short_version" == "2.4" -o "$short_version" == "2.7" ] && sed -i '/^#_ssl/,/^$/ s/^#//' Modules/Setup.dist
        # Avoid buffer overflow during "make"
        [ "$short_version" == "2.4" ] && configure_opts="BASECFLAGS=-U_FORTIFY_SOURCE"
        # Avoid "No module named _sha256" during venv creation
        [ "$short_version" == "2.7" ] && sed -i 's/^#_sha/_sha/' Modules/Setup.dist
        execute ./configure $configure_opts --prefix=${PYTHON_PATH} --with-ssl
        execute make
        execute make install
    fi
}

function download_virtualenv() {
    # download the virtualenv package based on the version
    local version=$1
    local foldername=virtualenv-$version
    local pkgname=$foldername.tar.gz
    if [ ! -f "$TMP/$pkgname" ]; then
        h2 downloading virtualenv $version
        execute cd $TMP
        execute wget -q http://pypi.python.org/packages/source/v/virtualenv/$pkgname
    fi
}
function install_virtualenv(){
    # install virtualenv
    # $1 = virtualenv version
    # $2 = python version
    local version=$1
    local python_version=$2
    local python_short_version=$( short_version $python_version )
    if [ ! -f $PYTHON_PATH/bin/virtualenv-$python_short_version ]; then
        h2 installing virtualenv $version
        execute cd $TMP
        execute tar xzf virtualenv-$version.tar.gz
        execute cd virtualenv-$version
        execute $PYTHON_PATH/bin/python$python_short_version setup.py install
    fi
}

function activate_virtualenv(){
    local version=$1
    execute source $VENV_PATH/$version/bin/activate
}

function deactivate_virtualenv(){
    execute deactivate
}

function create_virtualenv(){
    # setup a virtuel environment
    # $1 = Python version
    local python_version=$1
    local python_short_version=$( short_version $python_version )
    local venv_dir="$VENV_PATH/$python_version"
    if [ ! -d "$venv_dir" ]; then
        local pep8_version=
        local pylint_version=
        local PYTHON_BIN="$PYTHON_PATH/bin/python$python_short_version"
        local VIRTUALENV="$PYTHON_PATH/bin/virtualenv-$python_short_version"
        h2 Creating virtualenv for Python-$python_version $VIRTUALENV
        execute $PYTHON_BIN $VIRTUALENV $venv_dir
        activate_virtualenv $python_version
        if [ "$python_short_version" == "2.7" ]; then
            execute pip install pep8
        fi
        if [ "$python_short_version" == "2.4" ]; then
            pep8_version='==1.2'
            #pylint_version='==0.28.0' # requiert astroid
            pylint_version='==0.15.2'
            execute pip install argparse
            # astroid wants unittest2 unittest2>=0.5.1
            execute pip install 'unittest2==0.5.1'
            # impossible to find a compatible version on pypi
            # execute pip install 'logilab-astng==0.19.0'
        fi
        echo "Executing \"pip -q install pylint$pylint_version\""
        execute pip -q install pylint$pylint_version
        deactivate_virtualenv
    fi
}

function activate_pyvenv(){
    local version=$1
    source $VENV_PATH/$version/bin/activate
}

function deactivate_pyvenv(){
    deactivate
}


function create_pyvenv(){
    local python_version=$1
    local python_short_version=$( short_version $python_version )
    local PYTHON_BIN="$PYTHON_PATH/bin/python$python_short_version"
    local PYVENV_BIN="$PYTHON_PATH/bin/pyvenv-$python_short_version"
    if [ ! -d $VENV_PATH/$python_version ]; then
        h2 Creating pyvenv For Python $python_short_version
        execute $PYTHON_BIN $PYVENV_BIN $VENV_PATH/$python_version
        execute activate_pyvenv $python_version
        execute pip install pylint
        execute pip install pep8
        execute deactivate_pyvenv
    fi
}

function run_tests() {
    # run the tests on a specific python version
    # $1 = Python version
    #
    # Actual tests:
    # * pylint (where version != 2.4)
    # * pep8
    # * ./tests/unittests.py
    local version=$1
    local python_short_version=$( short_version $version )
    h1 "Running tests for Python-$version"
    if [ "${python_version:0:1}" == "3" ]; then
        activate_pyvenv $python_version
    else
        activate_virtualenv $python_version
    fi
    if [ "$version" != "2.4" ]; then
        h2 Running Pylint...
        set +e
        execute cd $ROOT_PATH
        execute $VENV_PATH/$python_version/bin/pylint --output-format=colorized --rcfile=/dev/null -E ./check_iftraffic_nrpe.py
        FINAL_MSG="${FINAL_MSG}Execution of pylint of Python $python_version: "
        if [ "$?" == "0" ]; then
            FINAL_MSG="${FINAL_MSG}OK\n"
        else
            FINAL_MSG="${FINAL_MSG}Errors\n"
        fi
        execute $VENV_PATH/$python_version/bin/pylint --output-format=colorized --rcfile=/dev/null -r n ./check_iftraffic_nrpe.py
        R=$?
        set -e
        if [ "$R" != "0" ]; then
            FINAL_MSG="${FINAL_MSG}  Pylint exit code was $R\n"
        fi
    fi
    h2 Running $VENV_PATH/$python_version/bin/pep8
    execute $VENV_PATH/$python_version/bin/pep8 --ignore=E111,E221,E701,E127 --show-source --show-pep8 ./check_iftraffic_nrpe.py
    h2 unittests
    execute ./tests/unittests.py
    deactivate
}

function run_full_tests_version(){
    # Prepare the environments and Execute the tests
    # Arguments:
    # $1 = Python version
    # $2 = Virtualenv version
    mkdir -p "$TMP" "$VENV_PATH" "$PYTHON_PATH"
    local python_version=$1
    local virtualenv_version=$2
    download_python $python_version
    install_python $python_version
    if [ "${python_version:0:1}" == "3" ]; then
        create_pyvenv $python_version
    else
        download_virtualenv $virtualenv_version
        install_virtualenv $virtualenv_version $python_version
        create_virtualenv $python_version
    fi
    run_tests $python_version
}

# 2.4 plante a l'install de argparse :/
#run_full_tests_version 2.4.4 1.7.2

run_full_tests_version 2.7.8 1.11.6
run_full_tests_version 3.4.1 1.11.6
 
echo '##############'
echo '#  finished  #'
echo '##############'

echo -e $FINAL_MSG

