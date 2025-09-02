""" Setup Package Configuration
"""
from setuptools import setup, find_packages


setup(
    name="changelist-init",
    version="0.2.1",
	author='DK96-OS',
	description='Initialize and update Changelists information.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/DK96-OS/changelist-init/",
    project_urls={
        "Issues": "https://github.com/DK96-OS/changelist-init/issues",
        "Source Code": "https://github.com/DK96-OS/changelist-init/"
    },
	license='GPLv3',
    packages=find_packages(exclude=['test', 'test.*']),
    install_requires=[
        'changelist-data >= 0.2.4, < 0.3',
    ],
    entry_points={
        'console_scripts': [
            'changelist-init=changelist_init.__main__:main',
            'cl-init=changelist_init.__main__:main',
            'cl_init=changelist_init.__main__:main',
        ],
    },
    python_requires='>=3.10',
    keywords=['changelist', 'git', 'vcs'],
    classifiers=[
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ]
)