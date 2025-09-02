from setuptools import setup, find_packages

setup(
    name='phg_vis', 
    version='1.1.1', 
    packages=find_packages(),
    include_package_data=True,
    description='A package for the PHG modeling language and 3D visualization tool.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='romeosoft',
    author_email='18858146@qq.com', 
    url='https://github.com/panguojun/Coordinate-System',
    classifiers=[ 
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
    ],
    python_requires='>=3.8',
    install_requires=[],
    package_data={
        'phg': ['phg.pyd'],
        '': ['vis/**/*'],
    },
    platforms=['Windows'],
)