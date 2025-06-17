from setuptools import setup, find_packages
from fusion import __version__

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name="fusion-sync",
    version=__version__,
    description="Keep your files in sync",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Mohammad Mallaee",
    license="GPLv3",
    packages=find_packages(),
    install_requires=[
        "pytermgui",
        "argcomplete"
    ],
    package_data={
        "fusion": ["configs/*"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "fusion=fusion.__main__:main",
        ],
    },
)
