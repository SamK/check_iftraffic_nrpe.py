import fabric.api as fab

def upload(somewhere):
    """ Upload the package somewhere ("somewhere" is a section in the ~/.pypi file)
    """
    fab.local('mkdir -p check_iftraffic_nrpe')
    fab.local('cp check_iftraffic_nrpe.py check_iftraffic_nrpe')
    fab.local('python setup.py sdist upload -r {}'.format(somewhere))

def register(somewhere):
    """ Register the package (must be done once)
    """
    fab.local('python setup.py register -r {}'.format(somewhere))
