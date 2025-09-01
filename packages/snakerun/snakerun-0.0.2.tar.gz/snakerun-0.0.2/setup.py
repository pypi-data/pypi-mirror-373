from setuptools import setup, find_packages
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def read_requirements(filename):
    with open(os.path.join(BASE_DIR, "requirements", filename), "r", encoding="utf-8") as fh:
        return fh.read().splitlines()


# Long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirement sets
install_requires = read_requirements("requirements.txt")
test_requires = read_requirements("requirements_test.txt")
dev_requires = read_requirements("requirements_dev.txt")

setup(
    name="snakerun",
    version="0.0.2",
    author="Ishan Bhat",
    author_email="ishan2003bhat@gmail.com",
    description="A Python based CLI game for playing classical snake game",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=install_requires,
    extras_require={
        "test": test_requires,
        "dev": dev_requires,
        "all": test_requires + dev_requires,
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "snakerun=snakerun.cli:main",
        ],
    },
    keywords="snake game python cli",
    include_package_data=True,
)
