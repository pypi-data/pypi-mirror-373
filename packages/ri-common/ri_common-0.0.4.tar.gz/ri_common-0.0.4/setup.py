import os
import setuptools

with open(os.path.join('riu', 'resources', 'README.md')) as f:
    long_description = f.read()

_VERSION = '0.0.4'

_REQUIREMENTS = [
    'build',
    'twine',
    'python-dateutil',
]

setuptools.setup(
    name='ri-common',
    version=_VERSION,
    description="Common, reusable utilities",
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[],
    author='Dustin Oprea',
    author_email='dustin@randomingenuity.com',
    packages=setuptools.find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    package_data={
        'riu': [
            'resources/README.md',
            'resources/requirements.txt',
            'resources/requirements-testing.txt',
        ],
    },
    install_requires=_REQUIREMENTS,
    scripts=[
    ],
)
