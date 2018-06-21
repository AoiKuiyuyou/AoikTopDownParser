# coding: utf-8
from __future__ import absolute_import

from setuptools import find_packages
from setuptools import setup


with open('requirements.txt') as requirements_file:
    install_requires = requirements_file.read().splitlines()


setup(
    name='AoikTopDownParser',

    version='0.2.0',

    description='A top-down recursive-descendent parser generator.',

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
        'Operating System :: OS Independent ',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='top down recursive descendent parser generator',

    package_dir={'': 'src'},

    packages=find_packages('src'),

    package_data={
        'aoiktopdownparser': [
            'demo/*/*',
            'gen/me/*',
        ],
    },

    install_requires=install_requires,

    entry_points={
        'console_scripts': [
            'aoiktopdownparser=aoiktopdownparser.__main__:main',
        ],
    },
)
