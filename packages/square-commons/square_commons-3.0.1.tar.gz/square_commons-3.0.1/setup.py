from setuptools import find_packages, setup

package_name = "square_commons"

setup(
    name=package_name,
    version="3.0.1",
    packages=find_packages(),
    install_requires=[
        "configparser>=6.0.0",
        "requests>=2.32.3",
        "pytest>=8.3.3",
        "pytest-mock>=3.14.0",
        "Deprecated>=1.2.18",
    ],
    extras_require={},
    author="Parth Mukesh Mangtani",
    author_email="thepmsquare@gmail.com",
    description="helper module containing common functions for all my python modules.",
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
