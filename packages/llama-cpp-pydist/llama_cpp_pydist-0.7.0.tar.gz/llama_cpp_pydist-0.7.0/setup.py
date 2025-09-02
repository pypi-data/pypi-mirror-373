from setuptools import setup, find_packages

setup(
    name='llama_cpp_pydist',
    version='0.7.0',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": ["*.txt", "*.rst"],
        # And include any *.dat files found in the 'data' subdirectory
        # of the 'mypkg' package, also:
        "llama_cpp": ["vendor_llama_cpp_pydist/llama.cpp/**/*", "binaries/*"],  # Added binaries/*
    },
    install_requires=[
        # Add any dependencies here
    ],
    entry_points={
        'console_scripts': [
            # Add any command line scripts here
        ],
    },
    author='Shamit Verma',
    author_email='oss@shamit.in',
    description='A Python package for Llama CPP.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/shamitv/llama_cpp',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)
