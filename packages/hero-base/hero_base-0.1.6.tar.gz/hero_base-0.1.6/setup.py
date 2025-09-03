from setuptools import setup, find_packages

setup(
    name='hero-base',
    packages=find_packages(),
    author='Baidu',
    author_email='wangdejiang@baidu.com',
    description='Base for hero',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown', 
    url='https://github.com/baidu/hero-tools',
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache License 2.0",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3.12",
        "Typing :: Typed",
    ],
    python_requires='>=3.12',
    package_data={
        'base': [],
    },
)
