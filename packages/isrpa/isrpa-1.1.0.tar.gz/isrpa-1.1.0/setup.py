from setuptools import setup, find_packages

setup(
    name='isrpa',
    version='1.1.0',
    packages=find_packages(),
    install_requires=["requests", "tldextract"],
    author='ysq',
    author_email='wuzhengjun@i-search.com.cn',
    description='isrpa package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/mypackage',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)