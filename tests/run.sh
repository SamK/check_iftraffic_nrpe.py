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

short_version(){
    local long_version=$1
    local short_version="${long_version%.*}"
    echo $short_version
}

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
    local short_version=$( short_version $version )
    local configure_opts=''
    h2 installing Python $version

    if [ -f $PYTHON_PATH/bin/python${short_version} ]; then
        echo "Python-$version is already installed...skipping."
    else
        cd $TMP
        tar xzf $PKG_PREFIX-$version.tgz
        cd $PKG_PREFIX-$version
        [ "$short_version" == "2.4" -o "$short_version" == "2.7" ] && sed -i 's/^#zlib/zlib/' Modules/Setup.dist
        [ "$short_version" == "2.4" -o "$short_version" == "2.7" ] && sed -i '/^#_ssl/,/^$/ s/^#//' Modules/Setup.dist
        # Avoid buffer overflow during "make"
        [ "$short_version" == "2.4" ] && configure_opts="BASECFLAGS=-U_FORTIFY_SOURCE"
        # Avoid "No module named _sha256" during venv creation
        [ "$short_version" == "2.7" ] && sed -i 's/^#_sha/_sha/' Modules/Setup.dist
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
    local python_version=$2
    local python_short_version=$( short_version $python_version )
    h1 installing virtualenv $version
    if [ -f $PYTHON_PATH/bin/virtualenv-$python_short_version ]; then
        echo "virtualenv-$python_short_version is already installed...skipping."
    else
        cd $TMP
        tar xzf virtualenv-$version.tar.gz
        cd virtualenv-$version
        $PYTHON_PATH/bin/python$python_short_version setup.py install
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
set -x
    local python_version=$1
    local python_short_version=$( short_version $python_version )
    h2 Creating virtualenv For Python $python_short_version
    if [ -d $VENV_PATH/$python_version ]; then
        echo "Virtual env $VENV_PATH/$python_version already exists."
    else
        local pep8_version=
        local pylint_version=
        local PYTHON_BIN="$PYTHON_PATH/bin/python$python_short_version"
        local VIRTUALENV="$PYTHON_PATH/bin/virtualenv-$python_short_version"
        if [ "$python_short_version" == "2.4" ]; then
            local pep8_version='==1.2'
            local pylint_version='==123'
        fi
        $PYTHON_BIN $VIRTUALENV $VENV_PATH/$python_version
        activate_virtualenv $python_version
        echo "Executing \"pip install argparse$argparse_version\""
        pip install argparse
        if [ "$python_short_version" == "2.4" ]; then
            # astroid wants unittest2 unittest2>=0.5.1
            pip install 'unittest2==0.5.1'
            # pylint installs astroid (which latests version is not 2.4 compatible)
            pip install 'astroid==1.0.0'
        fi
        echo "Executing \"pip install pylint$pylint_version\""
        #pip install pylint
        deactivate_virtualenv
    fi
}

function run_tests() {
    local version=$1
    activate_virtualenv $version
    python -V
    if [ "$version" != "2.4" ]; then
        h2 Running $VENV_PATH/$version/bin/pylint
        $VENV_PATH/$version/bin/pylint -E ./check_iftraffic_nrpe.py
        set +e
        $VENV_PATH/$version/bin/pylint -r n ./check_iftraffic_nrpe.py
        set -e
    fi
    h2 Running $VENV_PATH/$version/bin/pep8
    $VENV_PATH/$version/bin/pep8 --ignore=E111,E221,E701,E127 --show-source --show-pep8 ./check_iftraffic_nrpe.py
    h2 unittests
    ./tests/unittests.py
    h2 deactivating
    deactivate
}

function run_full_tests_version(){
    local python_version=$1
    local virtualenv_version=$2
    prepare_tests
    download_python $python_version
    install_python $python_version
    download_virtualenv $virtualenv_version
    install_virtualenv $virtualenv_version $python_version
    create_virtualenv $python_version
    run_tests $python_version
}

run_full_tests_version 2.4 1.7.2
run_full_tests_version 2.7.8 1.11.6
run_full_tests_version 3.4.1 1.11.6
 
echo '##############'
echo '#     OK     #'
echo '##############'

