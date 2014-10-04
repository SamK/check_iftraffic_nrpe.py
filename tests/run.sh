#!/bin/bash
#set -x
set -e

function execute(){
    echo -e "> \e[90mDark \"$*\"\e[39mDefault"
    $*
}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
cd ..
DIR="$( pwd )"

FINAL_MSG=''

function h1() {
    echo $@
    echo "==========="
}

function h2() {
    echo $@
    echo "-----------"
}

PYTHON_PATH=$DIR/python
VENV_PATH=$DIR/virtualenv
TMP=$DIR/tmp
PKG_PREFIX="Python"

short_version(){
    local long_version=$1
    local short_version="${long_version%.*}"
    echo $short_version
}

function download_python() {
    local version=$1
    local foldername=$PKG_PREFIX-$version
    local pkgname=$foldername.tgz

    if [ ! -f "/${TMP}/${pkgname}" ]; then
        h2 Downloading Python $version
        execute cd $TMP
        execute wget -q https://www.python.org/ftp/python/$version/$pkgname
        execute cd ..
    fi
}

function install_python(){
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
        execute cd ../..
    fi
}

function download_virtualenv() {
    local version=$1
    local foldername=virtualenv-$version
    local pkgname=$foldername.tar.gz
    if [ ! -f "$TMP/$pkgname" ]; then
        h2 downloading virtualenv $version
        execute cd $TMP
        execute wget -q http://pypi.python.org/packages/source/v/virtualenv/$pkgname
        execute cd ..
    fi
}
function install_virtualenv(){
    local version=$1
    local python_version=$2
    local python_short_version=$( short_version $python_version )
    if [ ! -f $PYTHON_PATH/bin/virtualenv-$python_short_version ]; then
        h2 installing virtualenv $version
        execute cd $TMP
        execute tar xzf virtualenv-$version.tar.gz
        execute cd virtualenv-$version
        execute $PYTHON_PATH/bin/python$python_short_version setup.py install
        execute cd ../..
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
    local python_version=$1
    local python_short_version=$( short_version $python_version )
    local venv_dir="$VENV_PATH/$python_version"
    if [ ! -d "$venv_dir" ]; then
        local pep8_version=
        local pylint_version=
        local PYTHON_BIN="$PYTHON_PATH/bin/python$python_short_version"
        local VIRTUALENV="$PYTHON_PATH/bin/virtualenv-$python_short_version"
        h2 Creating virtualenv for Python-$python_version $VIRTUALENV
        if [ "$python_short_version" == "2.4" ]; then
            pep8_version='==1.2'
        fi
        execute $PYTHON_BIN $VIRTUALENV $venv_dir
        activate_virtualenv $python_version
        if [ "$python_short_version" == "2.7" ]; then
            execute pip install pep8
        fi
        if [ "$python_short_version" == "2.4" ]; then
            execute pip install argparse
            # astroid wants unittest2 unittest2>=0.5.1
            execute pip install 'unittest2==0.5.1'
            # pylint installs astroid (which latests version is not 2.4 compatible)
            execute pip install 'astroid==1.0.0'
        fi
        echo "Executing \"pip install pylint$pylint_version\""
        execute pip install pylint$pylint_version
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
        execute $VENV_PATH/$python_version/bin/pylint -E ./check_iftraffic_nrpe.py
        if [ "$?" != "0" ]; then
            FINAL_MSG="${FINAL_MSG}Errors during pylint of Python $python_version\n"
        fi
        execute $VENV_PATH/$python_version/bin/pylint -r n ./check_iftraffic_nrpe.py
        set -e
    fi
    h2 Running $VENV_PATH/$python_version/bin/pep8
    execute $VENV_PATH/$python_version/bin/pep8 --ignore=E111,E221,E701,E127 --show-source --show-pep8 ./check_iftraffic_nrpe.py
    h2 unittests
    execute ./tests/unittests.py
    deactivate
}

function run_full_tests_version(){
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

# pip install argparse:
#   - tsocks timeout
#   - proxy:  error:14090086:SSL routines:SSL3_GET_SERVER_CERTIFICATE:certificate verify failed
run_full_tests_version 2.7.8 1.11.6

# pip install pylint
#   - tsocks: timeout
run_full_tests_version 3.4.1 1.11.6
 
echo '##############'
echo '#  finished  #'
echo '##############'

echo -e $FINAL_MSG

