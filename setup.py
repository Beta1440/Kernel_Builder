
from setuptools import setup, find_packages


setup(name='kbuilder',
      version='0.1.0',
      description="Automate compiling the Linux kernel for android devices",
      long_description="Automate compiling the Linux kernel for android devices",
      author='Dela Anthonio',
      author_email='dell.anthonio@gmail.com',
      url='https://github.com/Beta1440/kernel-builder',
      license='GPL',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Software Development :: Build Tools',
      ],
      keywords=(
          'kernel', 'builder', 'linux'
      ),
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
          'cached-property>=1.3.0',
          'cement==2.10.2',
          'colorlog>=2.10.0',
      ],
      setup_requires=[],
      entry_points="""
        [console_scripts]
        kbuilder = kbuilder.cli.main:main
    """,
      namespace_packages=[],
     )
