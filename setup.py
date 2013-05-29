from setuptools import setup, find_packages

dependencies = ['hgtools', 'jinja2', 'keyring', 'pyrax', 'python-dateutil',
                'PyYAML', 'requests']

setup(
    name='serverherald',
    description=('serverherald announces when a new Rackspace OpenStack Cloud '
                 'Server becomes ACTIVE by polling the API. It supports '
                 'multiple notification methods, with email being the most '
                 'popular.'),
    keywords='rackspace cloud openstack serverherald',
    version='1.0.0',
    author='Matt Martz',
    author_email='matt.martz@rackspace.com',
    install_requires=dependencies,
    entry_points={'console_scripts':
                  ['serverherald=serverherald.shell:main']},
    packages=find_packages(exclude=['vagrant', 'tests', 'examples', 'doc']),
    package_data={
        'serverherald': ['templates/*'],
    },
    license='Apache License (2.0)',
    classifiers=["Programming Language :: Python"],
    url='https://github.com/rackerlabs/serverherald',
)
