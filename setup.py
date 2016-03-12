from setuptools import setup, find_packages

# does this presume that pip can find oompa?
from oompa import version


def readme():
    with open('README.rst') as f:
        return f.read()


setup (
    name             = "oompa",
    description      = "Code Tracking/Discovery, Task Helper",
    version          = version.__version__,

    long_description = readme(),
    
    # classifiers: [
    #    ]

    # keywords = "",

    # url = "",
    
    # author = "",
    # author_email = "".

    # license = "",

    install_requires = [ "click      >= 4.0.0",
                         "github3.py >= 1.0.0a4",
                        ],

    packages         = find_packages(),

    scripts = [
        "scripts/tracker",
        ],
    
    test_suite       = 'nose.collector',
    tests_require    = ['nose'],

    include_package_data = True,
    
    # entry_points     = {'console_scripts': ['run-the-app = deployme:main']}

)
