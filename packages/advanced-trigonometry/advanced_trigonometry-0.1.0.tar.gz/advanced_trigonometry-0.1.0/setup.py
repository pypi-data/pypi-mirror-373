
from setuptools import setup, find_packages

setup(
    name='advanced_trigonometry',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        # No external dependencies other than standard library modules (math, cmath)
    ],
    author='[Ankit kumar singh]',
    author_email='[singhkumar50866@gmail.com]',
    description='A Python library for advanced trigonometry with support for complex numbers and different angle units.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    # Removed the invalid URL
    # url='[https://github.com/Dada09898/Ankit_kumar_singh_all-trigo_library]',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha', # Or other appropriate status
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    python_requires='>=3.6', # Specify minimum Python version
)
