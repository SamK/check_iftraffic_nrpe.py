#!/bin/bash
#set -x
set -e


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
cd ..
DIR="$( pwd )"

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

function prepare_tests(){
    /bin/rm -rf $VENV_PATH
    mkdir -p $PYTHON_PATH
    mkdir -p $VENV_PATH
    mkdir -p $TMP
}

function download_python() {
    local version=$1
    local foldername=$PKG_PREFIX-$version
    local pkgname=$foldername.tgz

    h2 Downloading Python $version
    cd $TMP
    if [ -f "$pkgname" ]; then
        echo "File $pkgname already exists, not downlading."
    else
        wget -q https://www.python.org/ftp/python/$version/$pkgname
    fi
    cd ..
}

function install_python(){
    local version=$1
    local configure_opts=''
    h2 installing Python $version

    if [ -f $PYTHON_PATH/bin/python${version} ]; then
        echo "Python-$version is already installed...skipping."
    else
        cd $TMP
        tar xzf $PKG_PREFIX-$version.tgz
        cd $PKG_PREFIX-$version
        [ "$version" == "2.4" ] && sed -i 's/^#zlib/zlib/' Modules/Setup.dist
        [ "$version" == "2.4" ] && sed -i.bak '/^#_ssl/,/^$/ s/^#//' Modules/Setup.dist
        [ "$version" == "2.4" ] && configure_opts="BASECFLAGS=-U_FORTIFY_SOURCE"
        echo ./configure $configure_opts --prefix=${PYTHON_PATH} --with-ssl
        ./configure $configure_opts --prefix=${PYTHON_PATH} --with-ssl
        make
        make install
        cd ../..
    fi
}

function download_virtualenv() {
    local version=$1
    local foldername=virtualenv-$version
    local pkgname=$foldername.tar.gz
    h1 downloading virtualenv $version
    cd $TMP
    if [ -f "$pkgname" ]; then
        echo "File $pkgname already exists, not downlading."
    else
        wget -q http://pypi.python.org/packages/source/v/virtualenv/$pkgname
    fi
    cd ..
}

function install_virtualenv(){
    local version=$1
    h1 installing virtualenv $version
    if [ "$version" == "1.7.2" -a -f $PYTHON_PATH/bin/virtualenv-2.4 ]; then
        echo "virtualenv-$version is already installed...skipping."
    else
        cd $TMP
        tar xzf virtualenv-$version.tar.gz
        cd virtualenv-$version
        $PYTHON_PATH/bin/python2.4 setup.py install
        cd ../..
    fi
}

function activate_virtualenv(){
    local version=$1
    source $VENV_PATH/$version/bin/activate
}

function deactivate_virtualenv(){
    deactivate
}

function create_virtualenv(){
    local version=$1
    h2 Creating virtualenv $version
    if [ -d $VENV_PATH/$version ]; then
        echo "Virtual env $VENV_PATH/$version already exists."
    else
        local PYTHON_BIN="/usr/bin/python"
        local VIRTUALENV="virtualenv"
        if [ "$version" == "2.4" ]; then
            local VIRTUALENV="$PYTHON_PATH/bin/virtualenv-2.4"
            local PYTHON_BIN="$PYTHON_PATH/bin/python2.4"
            local pip_pep8_version='==1.2'
        fi
        $PYTHON_BIN $VIRTUALENV $VENV_PATH/$version
        activate_virtualenv $version
        echo pip install pep8$pip_pep8_version
        pip install pep8$pip_pep8_version
        pip install argparse
        pip install pylint
        deactivate_virtualenv
    fi
}

function run_tests() {
    local version=$1
    activate_virtualenv $version
    h2 Using binary $PYTHON_BIN
    $VENV_PATH/$version/bin/pylint -E ./check_iftraffic_nrpe.py
    set +e
    $VENV_PATH/$version/bin/pylint -r n ./check_iftraffic_nrpe.py
    set -e
    h2 pep8
    $VENV_PATH/bin/pep8 --ignore=E111,E221,E701,E127 --show-source --show-pep8 ./check_iftraffic_nrpe.py
    h2 unittests
    ./tests/unittests.py
    h2 deactivating
    deactivate
}

function run_full_tests_version(){
    local version=$1
    prepare_tests
    download_python $version
    install_python $version
    download_virtualenv 1.7.2
    install_virtualenv 1.7.2
    create_virtualenv $version
    run_tests $version
}

run_full_tests_version 2.4
run_full_tests_version 2.7
exit 0
run_full_tests_version 3.4
 


