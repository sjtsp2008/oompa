from setuptools import setup, find_packages

# does this presume that pip can find oompa?
from oompa import version


setup (
    name             = "oompa",
    version          = version.__version__,
    description      = "Code Tracking/Discovery, Task Helper",
    packages         = find_packages(),
    install_requires = ["click >=4.0.0",
                        ],

    test_suite       = 'nose.collector',
    tests_require    = ['nose'],
    
    # entry_points     = {'console_scripts': ['run-the-app = deployme:main']}

)
