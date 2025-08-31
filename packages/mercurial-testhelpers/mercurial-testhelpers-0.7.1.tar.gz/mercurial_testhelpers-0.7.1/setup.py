from setuptools import setup, find_packages

with open('install-requirements.txt', 'r') as install_reqf:
    install_req = [req.strip() for req in install_reqf]


setup(
    name='mercurial-testhelpers',
    version='0.7.1',
    author='Georges Racinet',
    author_email='georges.racinet@octobus.net',
    project_urls=dict(
        Source='https://foss.heptapod.net/mercurial/testhelpers',
        Tracker='https://foss.heptapod.net/mercurial/testhelpers/-/issues',
    ),
    description="Helpers to write Python tests involving "
    "Python internals of Mercurial",
    long_description='\n\n'.join((open('README.md').read(),
                                  open('CHANGELOG.md').read()
                                  )),
    long_description_content_type="text/markdown",
    keywords='hg mercurial testing',
    license='GPLv2+',
    packages=find_packages(exclude=['examples*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
        " :: GNU General Public License v2 or later (GPLv2+)",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Version Control :: Mercurial",
    ],
    install_requires=install_req,
)
