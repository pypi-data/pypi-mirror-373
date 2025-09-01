from setuptools import setup, find_packages
import PyAsyncScheduler as package

setup(
    name='PyAsyncScheduler',
    version=package.__version__,
    py_modules=['PyAsyncScheduler'],
    packages=find_packages(include=[]),
    install_requires=[],
    scripts=[],
    author="Maurice Lambert",
    author_email="mauricelambert434@gmail.com",
    maintainer="Maurice Lambert",
    maintainer_email="mauricelambert434@gmail.com",
    description='An asynchronous task scheduler, with cron syntax, intervals, limits, dynamic configuration, and optional vault integration.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mauricelambert/PyAsyncScheduler",
    project_urls={
        "Github": "https://github.com/mauricelambert/PyAsyncScheduler",
        "Documentation": "https://mauricelambert.github.io/info/python/code/PyAsyncScheduler.html",
    },
    include_package_data=True,
    classifiers=[
        "Topic :: System",
        "Environment :: Console",
        "Topic :: System :: Shells",
        'Operating System :: POSIX',
        "Natural Language :: English",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Topic :: System :: System Shells",
        'Operating System :: MacOS :: MacOS X',
        "Programming Language :: Python :: 3.8",
        'Operating System :: Microsoft :: Windows',
        "Topic :: System :: Systems Administration",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Libraries",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
    keywords=['scheduler', 'cron', 'async', 'task-scheduler', 'background-tasks', 'vault'],
    platforms=['Windows', 'Linux', "MacOS"],
    license="GPL-3.0 License",
    entry_points = {
        'console_scripts': [
            'PyAsyncScheduler = PyAsyncScheduler:main'
        ],
    },
    python_requires='>=3.8',
)