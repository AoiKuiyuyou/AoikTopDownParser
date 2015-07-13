# coding: utf-8
from __future__ import absolute_import
import os
from setuptools import find_packages
from setuptools import setup

setup(
    name='AoikTopDownParser',

    version='0.1.1',

    description="""A top-down recursive-descendent LL(n>=1) parser generator.""",

    long_description="""`Documentation on Github
<https://github.com/AoiKuiyuyou/AoikTopDownParser>`_""",

    url='https://github.com/AoiKuiyuyou/AoikTopDownParser',

    author='Aoi.Kuiyuyou',

    author_email='aoi.kuiyuyou@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords='top down recursive descendent parser generator',

    package_dir={'':'src'},

    packages=find_packages('src'),

    entry_points={
        'console_scripts': [
            'aoiktopdownparser=aoiktopdownparser.main.aoiktopdownparser:main',
        ],
    },
)
