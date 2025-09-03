from pathlib import Path
from setuptools import setup

with open('argparse_decorations/__version__') as f:
    _version = f.readline().strip()

setup(name='argparse_decorations',
      version=_version,
      description='argparse wrapper around decorations',
      long_description_content_type="text/markdown",
      long_description=(Path(__file__).parent / 'README.md').read_text(),
      url='https://bitbucket.org/rmonico/argparse_decorations',
      author='Rafael Monico',
      author_email='rmonico1@gmail.com',
      license='GPL3',
      include_package_data=True,
      data_files=[('version file', ['argparse_decorations/__version__'])],
      packages=['argparse_decorations'],
      zip_safe=False)
