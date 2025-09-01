import codecs
import os
from setuptools import setup, find_packages

# these things are needed for the README.md show on pypi (if you dont need delete it)
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

# you need to change all these
VERSION = '0.3.7'
DESCRIPTION = 'a look edge web library , support both win and mac '
LONG_DESCRIPTION = 'look-edge-web is a look edge web library ,support both win and mac'

setup(
    name="look_edge_web",
    version=VERSION,
    author="dkflex",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    package_data={
        'pyarmor_runtime_000000': ['pyarmor_runtime.pyd','__init__.py']
    },
    install_requires=["pywin32","psutil"],
    keywords=['python', 'look edge web', 'look-edge-web','windows'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)
