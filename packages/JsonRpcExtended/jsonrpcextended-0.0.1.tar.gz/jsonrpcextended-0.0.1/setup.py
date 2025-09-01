from setuptools import setup, find_packages

setup(
    name='JsonRpcExtended',
    version='0.0.1',
    py_modules=['JsonRpcExtended'],
    packages=find_packages(include=[]),
    install_requires=[],
    scripts=[],
    author="Maurice Lambert",
    author_email="mauricelambert434@gmail.com",
    maintainer="Maurice Lambert",
    maintainer_email="mauricelambert434@gmail.com",
    description='A remote procedure call (RPC) framework based on JSON-RPC, extended to support alternative data formats and structures such as CSV, XML, binary and python calls.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mauricelambert/JsonRpcExtended",
    project_urls={
        "Github": "https://github.com/mauricelambert/JsonRpcExtended",
        "Documentation": "https://mauricelambert.github.io/info/python/code/JsonRpcExtended.html",
    },
    include_package_data=True,
    classifiers=[
        'Operating System :: POSIX',
        "Natural Language :: English",
        "Topic :: System :: Networking",
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        'Operating System :: MacOS :: MacOS X',
        "Programming Language :: Python :: 3.8",
        'Operating System :: Microsoft :: Windows',
        "Topic :: System :: Systems Administration",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Libraries",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
    keywords=['RPC', 'JSON-RPC', 'CSV', 'Protocol', 'py-RPC'],
    platforms=['Windows', 'Linux', "MacOS"],
    license="GPL-3.0 License",
    entry_points = {
        'console_scripts': [
            'JsonRpcExtended = JsonRpcExtended:main'
        ],
    },
    python_requires='>=3.8',
)
