from setuptools import setup, find_packages

setup(
    name='UrlTasker',
    version='0.0.1',
    py_modules=['UrlTasker'],
    packages=find_packages(include=[]),
    install_requires=[],
    scripts=[],
    author="Maurice Lambert",
    author_email="mauricelambert434@gmail.com",
    maintainer="Maurice Lambert",
    maintainer_email="mauricelambert434@gmail.com",
    description='A Python library for defining, templating, and executing configurable asynchronous actions triggered via URLs.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mauricelambert/UrlTasker",
    project_urls={
        "Github": "https://github.com/mauricelambert/UrlTasker",
        "Documentation": "https://mauricelambert.github.io/info/python/code/UrlTasker.html",
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
    keywords=['url', 'task', 'async', 'async-tasker', 'asynchronous'],
    platforms=['Windows', 'Linux', "MacOS"],
    license="GPL-3.0 License",
    entry_points = {
        'console_scripts': [
            'UrlTasker = UrlTasker:main'
        ],
    },
    python_requires='>=3.8',
)
