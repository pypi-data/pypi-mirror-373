from setuptools import (
    find_packages,
    setup,
)

VERSION = '0.0.13'


try:
    long_description = open('README.md', 'rt').read()
except IOError:
    long_description = ''

with open('requirements.txt', encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [
    x.strip()
    for x in all_reqs if
    'git+' not in x
]

setup(
    name='behave_bo',
    version=VERSION,

    description='Electronic Document Management',
    long_description=long_description,

    author='Stepan Lushchiy',
    author_email='s.lushchiy@bars.group',

    url='http://docs.budg.bars.group/behave_bo/',
    download_url='',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
    ],

    platforms=['Any'],

    scripts=[],

    provides=[],

    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,

    package_data={
        '': [],
    },

    install_requires=install_requires,

    zip_safe=False,
)
