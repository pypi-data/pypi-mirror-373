import setuptools
import os

def get_version():
    tag = os.getenv('PANCHAM_VERSION')
    return tag

setuptools.setup(
    version=get_version()
)