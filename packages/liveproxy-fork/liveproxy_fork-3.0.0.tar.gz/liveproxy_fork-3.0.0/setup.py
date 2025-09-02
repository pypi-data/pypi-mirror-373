#!/usr/bin/env python3
import codecs
import os
import re

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(
        r'''^__version__ = ['"]([^'"]*)['"]''',
        version_file,
        re.M,
    )
    if version_match:
        return version_match.group(1)

    raise RuntimeError('Unable to find version string.')


long_description = read('README.md')

setup(
    name='liveproxy-fork',
    version=find_version('liveproxy', '__init__.py'),
    description='LiveProxy can redirect Livestreams to your favorite player',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/amjiddader/liveproxy',
    project_urls={
        'Source': 'https://github.com/amjiddader/liveproxy/',
        'Tracker': 'https://github.com/back-to/liveproxy/issues',
    },
    author='amjiddader',
    author_email='amjiddader@gmail.com',
    packages=['liveproxy'],
    entry_points={'console_scripts': ['liveproxy=liveproxy.main:main']},
    python_requires='>=3.6, <4',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Multimedia :: Video',
    ],
    keywords='LiveProxy Streamlink Youtube-DL YT-DLP',
)
