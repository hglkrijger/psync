from setuptools import setup

setup(name='psync',
      version='0.1.0',
      packages=['psync'],
      entry_points={'console_scripts': ['psync = psync.__main__:main']})

