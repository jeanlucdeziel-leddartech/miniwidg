import miniwidg
from setuptools import setup

with open("README.md", 'r') as file:
    long_description = file.read()

setup(name = miniwidg.__name__,
      version = miniwidg.__version__,
      author = miniwidg.__author__,
      author_email = 'jluc1011@hotmail.com',
      url = 'https://github.com/wackyweasel/miniwidg.git',
      description = 'Minimalist widget based control panels for quick and simple parameter manipulation',
      long_description = long_description,
      long_description_content_type = 'text/markdown',
      packages = ['miniwidg'],
      install_requires = [
          'tk',
          'pynput',
      ],
    )