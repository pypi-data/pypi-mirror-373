from setuptools import setup, find_packages

setup(
    name='pyvisalgo',
    version='0.1.1',
    packages=find_packages(),
    install_requires=['pygame'],
    author='Kiyong Kim',
    description='Python-based algorithm visualization framework for teaching.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)