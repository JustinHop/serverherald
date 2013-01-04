from setuptools import setup, find_packages

dependencies = ['hgtools', 'keyring', 'PyYAML', 'requests', 'pyrax', 'jinja2']

setup(
    name='serverherald',
    description='Notification utility that announces new servers',
    keywords='rackspace cloud',
    version='0.0.1',
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
    url='https://changethis.com',
)
