from setuptools import setup

setup(
    name='papyru',
    version='2.10.0',
    description=(
        'minimal REST library with OpenAPI-based validation for django'),
    author='puzzleYOU GmbH',
    author_email='papyru@puzzleyou.net',
    url='http://www.puzzleyou.net/',
    license='AGPLv3',
    platforms=['any'],
    packages=[
        'papyru',
        'papyru.static',
        'papyru.varspool',
        'papyru.varspool.command'
    ],
    package_data={
      'papyru.varspool': ['assets/*'],
    },
    install_requires=[
        'Cerberus',
        'Django',
        'jsonschema',
        'pyyaml',
        'requests',
        'lxml',
        'python-dateutil',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    scripts=[
        'bin/generate_jsonschema.py'
    ]
)
