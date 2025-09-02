# -*- coding: utf-8 -*-
# setup.py
from setuptools import find_packages, setup
import sys
from va import __version__




with open('README.rst') as f:
    long_description = f.read()

if sys.version_info[0] == 2:
    cv = "opencv-python==4.2.0.32"
else:
    cv = "opencv-python"

setup(
    name="emdbva",
    version=__version__,
    packages=find_packages(),
    exclude_package_data={
        'va': ['test/*', 'va/onedepva.py', 'core/*', 'proc/*', 'validation/*', 'test_data/*'],
    },
    include_package_data=True,
    author="Zhe Wang",
    author_email="zhe@ebi.ac.uk",
    description="CryoEM validation toolkit",
    long_description=open("README.rst", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://test.pypi.org/project/va/",
    license="Apache License",
    keywords="EMDB,Cryoem, Validation",
    # setup_requires=[
    #     "setuptools",
    #     "wheel",
    #     "twine",
    setup_requires=[
        'numpy'
    ],
    install_requires=[
        "numpy",
        "scipy>=0.14",
        "scikit-learn",
        "Pillow",
        "memory-profiler",
        "matplotlib",
        "pandas",
        "biopython",
        "mrcfile",
        "torch",
        cv,
    ],
    classifiers=[
        # maturity
        'Development Status :: 2 - Pre-Alpha',
        # environment
        'Environment :: Console',
        # audience
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        # license
        'License :: OSI Approved :: Apache Software License',
        # python version
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 2.7',
    ],
    entry_points={
        'console_scripts': [
            'va = va.mainva:main',
        ]
    },
)
