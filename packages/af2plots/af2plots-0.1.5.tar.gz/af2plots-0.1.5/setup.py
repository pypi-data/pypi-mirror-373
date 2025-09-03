#!/usr/bin/env python

from setuptools import setup, find_packages

import subprocess
import os,sys,re
sys.path.insert(0, f'{os.path.dirname(__file__)}/af2plots')
import af2plots

def get_git_describe(abbrev=7):
    import af2plots.version
    return af2plots.version.__version__


VERSION = get_git_describe()

setup(name='af2plots',
      version=VERSION,
      description='AF2 plots plots',
      url='https://git.embl.de/gchojnowski/af2plots',
      author='Grzegorz Chojnowski',
      author_email='gchojnowski@embl-hamburg.de',
      license=None,
      packages=['af2plots'],
      package_data={'af2plots':['../examples/PIAQ_test_af2mmer_dimer/input/*', '../examples/PIAQ_test_af2mmer_dimer/input/msas/A/*'] },
      entry_points={
          "console_scripts": [
            "af2plots = af2plots.__main__:main",
            ],
      }
     )
