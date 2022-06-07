#!/usr/bin/env python
import os
from setuptools import setup, Command

class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')

setup(name='tap-nasa',
	version="0.1.0",
	description="Singer.io tap to extract data from NASA API",
	author="Michel Ebner",
	classifiers=["Programming Language :: Python :: 3 :: Only"],
	py_modules=["tap_nasa"],
	install_requires=[
		'backoff',
		'requests',
		'simplejson',
		'singer-python'
	],
	entry_points='''
		[console_scripts]
		tap-nasa=tap_nasa:main
	''',
	packages=['tap_nasa'],
	cmdclass={
		'clean': CleanCommand,
	},
)