import sys
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Determine platform-specific dependencies
install_requires = [
    "msgpack",
    "protobuf",
    "cryptography",
    "bcrypt"
]

# uvloop is only available on Unix-like systems (Linux, macOS)
if sys.platform != "win32":
    install_requires.append("uvloop")

setup(
    name="sockstream",
    version="1.0.2",
    author="Ayam Maximilian",
    author_email="ayammaxmillian@gmail.com",
    description="A Python package for handling socket communications with advanced functionality",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ayammaximilian/sockstream",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=install_requires,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
        "performance": [
            "uvloop; sys_platform != 'win32'",  # Only on Unix-like systems
        ],
        "all": [
            "uvloop; sys_platform != 'win32'",  # Only on Unix-like systems
        ],
    },
)
