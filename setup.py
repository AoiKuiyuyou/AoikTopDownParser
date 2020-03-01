# coding: utf-8
from __future__ import absolute_import

from setuptools import find_packages
from setuptools import setup


setup(
    name='AoikTopDownParser',

    version='0.3.0',

    description=(
        'A top-down recursive descent predictive or backtracking parser'
        ' generator.'
    ),

    long_description="""`Documentation on Github
<https://github.com/AoiKuiyuyou/AoikTopDownParser>`_""",

    url='https://github.com/AoiKuiyuyou/AoikTopDownParser',

    author='Aoi.Kuiyuyou',

    author_email='aoi.kuiyuyou@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent ',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],

    keywords=(
        'top down recursive descent predictive backtracking parser generator'
    ),

    package_dir={'': 'src'},

    packages=find_packages('src'),

    package_data={
        'aoiktopdownparser': [
            'demo/*/*',
            'gen/*',
        ],
    },

    entry_points={
        'console_scripts': [
            'aoiktopdownparser=aoiktopdownparser.__main__:main',
        ],
    },
)
