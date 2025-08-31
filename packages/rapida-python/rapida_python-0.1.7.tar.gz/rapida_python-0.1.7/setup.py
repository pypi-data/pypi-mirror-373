from setuptools import setup

setup(
    name="rapida-python",
    package_data={"rapida": ["py.typed"], "rapida.clients.protos": ["*.py"]},
)
