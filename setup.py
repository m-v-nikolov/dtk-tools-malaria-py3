from setuptools import setup, find_packages

import fnmatch
import os
included_files = []
include_filters = ['*.txt', '*.md', '*.csv']
for root, dirnames, filenames in os.walk('malaria'):
    for filter in include_filters:
        for filename in fnmatch.filter(filenames, filter):
            included_files.append(os.path.join(root, filename))

setup(name='malaria',
      version='$VERSION$',
      packages=find_packages(),
      package_data={'malaria': included_files},
      install_requires=[]
      )
