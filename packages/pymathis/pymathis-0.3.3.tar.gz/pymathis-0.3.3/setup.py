from setuptools import setup, find_packages



setup(
    name='pymathis',
    version='0.3.3',
    description='A library of interacting function to enable exchanges between MATHIS and python at each time steps',
    long_description='A library of interacting function to enable exchanges between MATHIS and python at each time steps',
    long_description_content_type='text/markdown',
    url='https://gitlab.com/CSTB/pymathis',
    author='Xavier FAURE, Francois DEMOUGE',
    author_email='xavier.faure@cstb.fr, francois.demouge@cstb.fr',
    license='GNU Lesser General Public License',
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=['psutil','matplotlib','f90nml'],
)
