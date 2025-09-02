# -*- coding: utf-8 -*-
"""setup.py."""

from setuptools import setup

from os.path import join, dirname, abspath

# Single definition of __version__ in version.py
__version__ = 'UNDEFINED'
with open(join(dirname(__file__), 'mriqa', 'version.py')) as f:
    exec(f.read())

def readme(fname):
    path = abspath(join(dirname(__file__), fname))
    with open(path, encoding='utf-8') as f:
        return f.read()

config = {
    'name': 'mriqa',
    'description': 'Tools for MRI QA',
    'long_description': readme('README.md'),
    'long_description_content_type': 'text/markdown',
    'version': __version__,
    'author': 'Ronald Hartley-Davies',
    'author_email': 'R.Hartley-Davies@physics.org',
    'license': 'MIT',
    'url': 'https://bitbucket.org/rtrhd/mriqa.git',
    'download_url': 'https://bitbucket.org/rtrhd/mriqa/get/v%s.zip' % __version__,
    'tests_require': ['pytest'],
    'install_requires': [
        'numpy>=1.21.5',
        'scipy>=1.8.0',
        'matplotlib>=3.5.1',
        'pandas>=1.3.5',
        'xarray>=0.21.1',
        'scikit-image>0.18.3',
        'statsmodels>=0.13.2',
        'pydicom>=2.2.2',
        'dcmfetch>=0.3.2',
        'dcmextras>=0.3.5'
    ],
    'packages': ['mriqa', 'mriqa.xmlqa', 'mriqa.reports'],
    'package_data': {'mriqa': []},
    'scripts': [],
    'keywords': "mri qa phantom",
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13'
    ]
}

setup(**config)
