# Works, yet beta.toml over-installs the .gsdict files?
#
from __future__ import unicode_literals
from distutils.core import setup
from setuptools import find_packages, find_namespace_packages

# ---from glob import glob as glob
# ---aFiles = glob("Hershey01//GsDict//*.gsdict")
# defer to README.md:
aFiles = [
    "MightyMaxims/MightyMaxims2025.sqlt3",
    ]

zFiles = [
    ('MightyMaxims',aFiles)
    ]

setup(name='MightyMaxims',
      author="Randall Nagy",
      description="Mighty Memorable Quotations",
      author_email="r.a.nagy@gmail.com",
      url="http://soft9000.com",
      download_url="https://github.com/soft9000/DoctorQuote",
      platforms="Cross-Platform CLI / TUI",
      packages=find_namespace_packages(),
      data_files=zFiles)
