from setuptools import find_packages, setup

package_name = "square_file_store_helper"

setup(
    name=package_name,
    version="3.0.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "kiss_headers>=2.4.3",
        "square_commons>=2.0.0",
    ],
    author="Parth Mukesh Mangtani",
    author_email="thepmsquare@gmail.com",
    description="helper to access the file store layer for my personal server.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url=f"https://github.com/thepmsquare/{package_name}",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
