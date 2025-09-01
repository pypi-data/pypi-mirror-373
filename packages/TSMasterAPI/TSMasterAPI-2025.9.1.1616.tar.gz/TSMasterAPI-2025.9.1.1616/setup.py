'''
Author: seven 865762826@qq.com
Date: 2023-03-24 09:26:29
LastEditors: seven 865762826@qq.com
LastEditTime: 2023-11-24 11:46:54
FilePath: \VSCode_Pro\Python_Pro\TSMasterApi\setup.py
'''
from distutils.core import setup
import os
from setuptools import find_packages
import sys
_curr_path = os.path.dirname(__file__)
sys.path.append(_curr_path)
# import time
from TSMasterAPI import __version__
# time_tuple = time.localtime(time.time())
# AVersion = f'v{time_tuple[0]}.{time_tuple[1]}.{time_tuple[2]}.{time_tuple[3]}'

with open("README.rst", "r",encoding="utf-8") as f:
  long_description = f.read()

# 
setup(name='TSMasterAPI',  # 包名
      version=__version__,  # 版本号
      description='Use TSMaster hardware',
      long_description=long_description,
      author='seven',
      author_email='865762826@qq.com',
      install_requires=[],
      license='Apache License',
      packages=find_packages(),
      include_package_data=True,
      data_files=[
        ('./TSMasterAPI/windows/bin', ['./TSMasterAPI/windows/bin/TSMaster.dll']),
        ('./TSMasterAPI/windows/bin64', ['./TSMasterAPI/windows/bin64/TSMaster.dll'])
      ],
      platforms=["WINDOWS"],
      classifiers=[
          'Intended Audience :: Developers',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Topic :: Software Development :: Libraries'
      ],
      )
