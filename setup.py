from setuptools import setup
from Cython.Build import cythonize

setup(
    name='2048project',
    version='0.0.0',
    # packages=[''],
    url='',
    license='',
    author='Adam Kinsey',
    author_email='adamkinsey273@gmail.com',
    description='Python 2048 Clone with AutoPlay',
    ext_modules=cythonize("Utils.pyx",
                          include_path=["C:\\Users\\Stephanie\\Documents\\Machine Learning\\2048\\2048project"],
                          gdb_debug=True),
    zip_safe= False
)
