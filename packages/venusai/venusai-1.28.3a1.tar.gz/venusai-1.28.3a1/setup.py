from setuptools import setup, find_packages

setup(
    name='venusai',
    version='1.28.3a1',
    packages=find_packages(),
    author='Mert Sirakaya',
    install_requires=['venai'],
    description='Install `venai` instead of this package.',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)