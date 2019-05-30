import os

from setuptools import setup, find_packages

about = {}

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'bakker', '__version__.py')) as f:
    exec(f.read(), about)

with open(os.path.join(here, 'README.md'), encoding='UTF-8') as f:
    long_description = f.read()


setup(
    name='bakker',
    version=about['__version__'],
    author='Nico Duldhardt, Friedrich Carl Schöne',
    author_email='...',
    description='A versioned backup tool.',
    long_description=long_description,
    license='MIT',
    url='...',
    packages=find_packages(exclude=['tests', 'resources' 'benchmarks']),
    entry_points={
        'console_scripts': ['bakker=bakker.cli:cli',],
    },
    package_data={},
    python_requires='>=3.5',
    setup_requires=[],
    install_requires=[
        'xxhash==1.3.0',
        'Click==7.0',
    ],
    extras_require={},
    include_package_data=True,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: System :: Archiving',
        'Topic :: System :: Archiving :: Backup',
        'Operating System :: POSIX :: Linux',
    ]
)