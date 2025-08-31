from setuptools import setup, find_packages

setup(
    name='tik_device_generator',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'SignerPy',
    ],
    author='S1',
    author_email='your.email@example.com',
    description='A library to generate TikTok device information.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/tik_device_generator',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)


