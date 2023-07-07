from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in catering_module/__init__.py
from catering_module import __version__ as version

setup(
	name="catering_module",
	version=version,
	description="Catering Module Satu Meja",
	author="Satu Meja",
	author_email="satumeja@mail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
