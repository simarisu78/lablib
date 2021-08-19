import sys
from glob import glob
from os.path import basename
from os.path import splitext
import subprocess

from setuptools import setup,find_packages
from setuptools.command.test import test as TestCommand

class VirtualEnvTest(TestCommand):

    description = 'run unit test in virtual environment (e.g. barcode reader is not connected)'
    user_options = []

    def run_tests(self):
        self._run(['pytest', '-c', 'pytest_env.ini'])
        
    def _run(self, command):
        try:
            subprocess.check_call(command)
        except Exception as e:
            pass

def _requires_from_file(filename):
    return open(filename).read().splitlines()

        
setup(
packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-cov"],
    cmdclass={'envtest':VirtualEnvTest},
    install_requires=_requires_from_file('requirements.txt'),
)
