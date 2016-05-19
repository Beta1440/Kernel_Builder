
from setuptools import setup, find_packages
import sys, os

setup(name='kbuilder',
    version='0.1.0',
    description="Automate compilling the Linux kernel for android devices",
    long_description="Automate compilling the Linux kernel for android devices",
    classifiers=[],
    keywords='',
    author='Dela Anthonio',
    author_email='dell.anthonio@gmail.com',
    url='https://github.com/Sublime-Development/kernel_builder',
    license='GPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    install_requires=[
        ### Required to build documentation
        # "Sphinx >= 1.0",
        ### Required for testing
        # "nose",
        # "coverage",
        ### Required to function
        'cement',
        ],
    setup_requires=[],
    entry_points="""
        [console_scripts]
        kbuilder = kbuilder.cli.main:main
    """,
    namespace_packages=[],
    )
