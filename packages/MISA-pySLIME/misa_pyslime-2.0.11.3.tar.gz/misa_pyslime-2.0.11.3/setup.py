from setuptools import setup, find_packages
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent.resolve()

# Long description from README
long_description = (HERE / 'README.md').read_text(encoding='utf-8')

setup(
    name='MISA_pySLIME',
    version='2.0.11.3',
    description='Millstone Hill Incoherent Scatter Radar Spatial-Linear Ionospheric Modeling Engine',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Mateo Cardona Serrano (them)',
    author_email='mcardonaserrano@berkeley.edu',
    url='https://github.com/mcardonaserrano/MISA_pySLIME',
    packages=find_packages(exclude=['*.egg-info']),
    python_requires='>=3.8',
    install_requires=[
        'numpy',
        'pandas',
        'xarray',
        'netCDF4',
        'scipy',
        'scikit-learn',
        'tqdm',
        'requests',
    ],
    include_package_data=True,
    package_data={
        # match the importable package name for .npy models
        'MISA_pySLIME': ['model/*.npy'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
