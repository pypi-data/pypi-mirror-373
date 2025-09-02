from setuptools import setup, find_packages

setup(
    name='DangQu',
    version='0.1.1',
    description='dangqu sdk',
    author='DMJ-11740',
    author_email='rpa@lumi.com',
    packages=find_packages(),
    install_requires=[
        'requests',
        'oauthlib',
        'requests-oauthlib',
        'pillow',
        'numpy'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
