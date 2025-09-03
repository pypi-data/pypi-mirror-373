from os import path, mkdir
from setuptools import setup, find_namespace_packages


with open('.version', 'r') as f:
    VERSION = f.read()


f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

config_folder = path.expanduser('~') + '/.grepsr'
if not path.exists(config_folder):
    mkdir(config_folder)

if not path.exists(config_folder + '/tmp'):
    mkdir(config_folder + '/tmp')

print("\033[95mThankyou for installing gcli\033[0m\n")

setup(
    name='grepsr-cli',
    install_requires=requirements,
    version=VERSION,
    description='A Cli tool for Grepsr Developers',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='grepsr',
    author_email='dev@grepsr.com',
    url='https://bitbucket.org/grepsr/grepsr-cli/',
    license='unlicensed',
    packages=find_namespace_packages(exclude=['ez_setup', 'tests*']),
    package_data={'grepsrcli': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        gcli = grepsrcli.main:main
    """
)
