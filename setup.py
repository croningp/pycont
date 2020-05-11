from setuptools import find_packages, setup

VERSION = '1.0.1'

setup(name="pycont",
      version=VERSION,
      description="Tools to work with Tricontinental Pumps",
      author="Jonathan Grizou",
      author_email='jonathan.grizou@glasgow.ac.uk',
      packages=find_packages(),
      package_data={
            "commanduino": ["py.typed"]
      },
      include_package_data=True,
      )
