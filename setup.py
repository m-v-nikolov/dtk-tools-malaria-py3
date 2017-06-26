from setuptools import setup, find_packages
from simtools.Utilities.General import files_in_dir

setup(name='malaria',
      version='$VERSION$',
      packages=find_packages(),
      package_data={'': files_in_dir('malaria')},
      install_requires=[]
      )
