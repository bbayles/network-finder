from setuptools import setup, find_packages

setup(
    name='network_finder',
    version='0.1',
    license='Apache',
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
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    packages=find_packages(include=['network_finder']),
    test_suite='tests',
)
