from setuptools import setup, find_packages

setup(
    name='tscytopred',
    version='0.0.2',
    description='A Deep Learning Framework for Inferring Cytokine Expression Trajectories from Irregular Longitudinal Gene Expression Data',
    author='miniymay',
    author_email='joungmin@vt.edu',
    url='https://github.com/joungmin-choi/TSCytoPred',
    install_requires=['torch', 'pandas', 'os', 'numpy', 'sys', 'datetime',],
    packages=find_packages(exclude=[]),
    keywords=['tscytopred'],
    python_requires='>=3.6',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
