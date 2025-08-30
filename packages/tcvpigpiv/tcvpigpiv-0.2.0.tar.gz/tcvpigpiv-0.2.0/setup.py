from setuptools import setup, find_packages

setup(
    name='tcvpigpiv',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[],
    author='Dan Chavas',
    author_email='drchavas@gmail.com',
    description='Calculate the tropical cyclone ventilated Potential Intensity (vPI) and the Genesis Potential Index using vPI (GPIv) from gridded datafiles. See Chavas Camargo Tippett (2025, J. Clim.) for details.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/drchavas/tcvpigpiv',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    license='MIT',
#    license_files=['LICENSE'],
    python_requires='>=3.6',
)
