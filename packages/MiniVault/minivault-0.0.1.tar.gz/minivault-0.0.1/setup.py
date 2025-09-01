from setuptools import setup, find_packages

setup(
    name='MiniVault',
    version='0.0.1',
    py_modules=['MiniVault'],
    packages=find_packages(include=[]),
    install_requires=[],
    scripts=[],
    author="Maurice Lambert",
    author_email="mauricelambert434@gmail.com",
    maintainer="Maurice Lambert",
    maintainer_email="mauricelambert434@gmail.com",
    description='A simple, lightweight vault implemented in pure Python for securely storing and retrieving secrets in light-duty applications.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mauricelambert/MiniVault",
    project_urls={
        "Github": "https://github.com/mauricelambert/MiniVault",
        "Documentation": "https://mauricelambert.github.io/info/python/code/MiniVault.html",
    },
    include_package_data=True,
    classifiers=[
        'Operating System :: POSIX',
        "Natural Language :: English",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
        'Operating System :: MacOS :: MacOS X',
        "Programming Language :: Python :: 3.8",
        'Operating System :: Microsoft :: Windows',
        "Topic :: System :: Systems Administration",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Libraries",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
    keywords=['vault', 'rc6', 'pure-python', 'lightweight-vault'],
    platforms=['Windows', 'Linux', "MacOS"],
    license="GPL-3.0 License",
    entry_points = {
        'console_scripts': [
            'MiniVault = MiniVault:main'
        ],
    },
    python_requires='>=3.8',
)
