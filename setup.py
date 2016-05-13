import sys
import os
import io
from setuptools import find_packages
from setuptools import setup

HERE = os.path.dirname(__file__)
buildNumberFile = os.path.join(HERE, "BUILD_NUMBER")
versionFile = os.path.join(HERE, "VERSION")

buildNumber = "0"

assert sys.version_info >= (3, 2), 'Python 3.2+ required. Version found: %s' % sys.version_info

_base_version = "0.15.{buildNumber}"

if os.path.exists(versionFile):
    with io.open(versionFile, "r") as f:
        _version = f.read().split("=")[1]
else:
    _version = _base_version.format(buildNumber=buildNumber)


if __name__ == '__main__':

    if "--buildNumber" in sys.argv:
        i = sys.argv.index("--buildNumber") + 1
        buildNumber = sys.argv[i]
        print("Found build number '{0}'".format(buildNumber))
        print("Try to create build number file: {0}".format(buildNumberFile))
        with open(buildNumberFile, 'w') as f:
            f.write(buildNumber)
        _version = _base_version.format(buildNumber=buildNumber)
        sys.argv.remove("--buildNumber")
        sys.argv.remove(buildNumber)

        with open(versionFile, 'w') as f:
            print("Try to create version file: {0}".format(versionFile))
            f.write("version={0}".format(_version))



    setup(
        name='atlassian-python-api',
        description='Python Atlassian REST API Wrapper',
        long_description='Python Atlassian REST API Wrapper',
        license='Apache License 2.0',
        version=_version,
        download_url='https://github.com/MattAgile/atlassian-python-api',

        author='Matt Harasymczuk',
        author_email='code@mattagile.com',
        url='http://mattagile.com/',

        packages=find_packages(),
        package_data={'': ['LICENSE', 'README.rst'], 'atlassian': ['*.py']},
        package_dir={'atlassian': 'atlassian'},
        include_package_data=True,

        zip_safe=False,
        install_requires=['requests'],
        extras_require={
            'PEP8': ['pep8']
        },

        platforms='Platform Independent',

        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: Apache Software License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Operating System :: POSIX',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.0',
            'Programming Language :: Python :: 3.1',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Topic :: Internet',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Software Development :: Libraries :: Application Frameworks']
    )

