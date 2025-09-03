import setuptools
from ptcookiechecker._version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ptcookiechecker",
    description="Cookie security testing tool",
    author="Penterep",
    author_email="info@penterep.com",
    url="https://www.penterep.com/",
    version=__version__,
    license="GPLv3",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Environment :: Console",
        "Topic :: Security",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    python_requires='>=3.9',
    install_requires=["ptlibs>=1.0.15,<2"],
    entry_points = {'console_scripts': ['ptcookiechecker = ptcookiechecker.ptcookiechecker:main']},
    include_package_data= True,
    long_description=long_description,
    long_description_content_type="text/markdown",
        project_urls = {
        "homepage":   "https://www.penterep.com/",
        "repository": "https://github.com/penterep/ptcookiechecker",
        "tracker":    "https://github.com/penterep/ptcookiechecker/issues",
    }
)