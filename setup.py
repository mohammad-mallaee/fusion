from setuptools import setup, find_packages

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name="fusion-sync",
    version="0.1.1",
    description="Keep your files in sync",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Mohammad Mallaee",
    license="GPLv3",
    packages=find_packages(),
    install_requires=[
        "pytermgui",
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
