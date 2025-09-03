#from distutils.core import setup
# import setuptools
from setuptools import setup, find_packages
from mdbq import __version__ as v

setup(name='mdbq',
      version=v.VERSION,
      author='xigua, ',
      author_email="2587125111@qq.com",
      url='https://pypi.org/project/mdbq',
      long_description='''
      世界上最庄严的问题：我能做什么好事？
      ''',
      packages=find_packages(include=['mdbq', 'mdbq.*']),
      package_data={
          'mdbq': [],
      },
      exclude_package_data={
          'mdbq': ['conf', 'conf.*', 'spd.txt'],
      },
      package_dir={'requests': 'requests'},
      license="MIT",
      python_requires='>=3.6',
      )
