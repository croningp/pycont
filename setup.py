from pycont._version import __version__

from setuptools import find_packages, setup
setup(name="pycont",
      version=__version__,
      description="Tools to work with Tricontinental Pumps",
      author="Jonathan Grizou",
      author_email='jonathan.grizou@glasgow.ac.uk',
      packages=find_packages(),
      )
