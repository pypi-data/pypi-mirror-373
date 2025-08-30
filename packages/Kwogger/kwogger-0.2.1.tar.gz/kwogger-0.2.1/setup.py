import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='Kwogger',
    author='Brad Corlett',
    description='A logging adapter that provides context data to each logging call over its lifetime.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.2.1',
    packages=['kwogger'],
    install_requires=[
        'termcolor'
    ],
    python_requires='>=3.6',
    classifiers=[
        'Operating System :: OS Independent'
    ]
)
