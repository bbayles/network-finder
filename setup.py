from os import getenv
from platform import python_implementation
from setuptools import Extension, find_packages, setup

if (getenv('NO_CYTHON') == 'true') or (python_implementation() != 'CPython'):
    ext_modules = []
else:
    cython_extension = Extension(
        'network_finder.network_finder',
        ['network_finder/network_finder.c'],
        extra_compile_args=["-O3"]
    )
    ext_modules = [cython_extension]


setup(
    name='network_finder',
    version='0.5',
    license='MIT',
    url='https://github.com/bbayles/network-finder',

    description='Matches IP addresses to encompassing networks',
    long_description=(
        'This project provides a means of matching IP (IPv4 and IPv6)'
        'addresses and subnets to networks that contain them. For example, '
        '192.0.2.128 is contained by 192.0.2.0/24.'
    ),

    author='Bo Bayles',
    author_email='bbayles@gmail.com',

    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],

    packages=find_packages(include=['network_finder']),
    test_suite='tests',
    ext_modules=ext_modules,
)
