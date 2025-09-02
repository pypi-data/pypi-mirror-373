# MIT License

# Copyright (c) 2024 dechin

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

""" Upload this project to pypi
$ python3 setup.py check
$ python3 setup.py sdist bdist_wheel
$ twine upload --repository-url https://upload.pypi.org/legacy/ fix-dist/*
"""

import os
import numpy as np
from pathlib import Path
from setuptools.command.build_ext import build_ext  
from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize

site_path = os.path.abspath('./build')
if 'LD_LIBRARY_PATH' in os.environ:
    os.environ['LD_LIBRARY_PATH'] += os.pathsep + site_path
else:
    os.environ['LD_LIBRARY_PATH'] = site_path

if "CUDA_PATH" not in os.environ:
    os.environ["CUDA_PATH"] = '/usr/local/cuda'
os.environ["PATH"] += os.pathsep + os.environ["CUDA_PATH"] + '/bin'

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

class BuildExt(build_ext):  
    def build_extensions(self):
        if not os.path.exists(site_path+'/cyfes/'):
            self.compiler.spawn(['mkdir', site_path+'/cyfes/'])

        self.compiler.spawn(['nvcc', '-shared', 'cyfes/kernels/FES.cu',
                             '-Xcompiler', '-fPIC', '-lcudart',
                             '--default-stream', 'per-thread',
                             '-o', 'cyfes/libcufes.so'])
        self.compiler.spawn(['nvcc', '-shared', 'cyfes/kernels/FES_f32.cu',
                             '-Xcompiler', '-fPIC', '-o', 
                             'cyfes/libcufes.1.so'])
        
        self.compiler.spawn(['mv', 'cyfes/libcufes.so', site_path+'/cyfes/'])
        self.compiler.spawn(['mv', 'cyfes/libcufes.1.so', site_path+'/cyfes/'])
        self.compiler.spawn(['patchelf', '--set-rpath', 
                             '$ORIGIN:$ORIGIN/../lib/python3.7/site-packages/CyFES.libs:'
                                '$ORIGIN/../lib/python3.8/site-packages/CyFES.libs:'
                                '$ORIGIN/../lib/python3.9/site-packages/CyFES.libs:'
                                '$ORIGIN/../lib/python3.10/site-packages/CyFES.libs', site_path+'/cyfes/libcufes.so'])
        
        super().build_extensions()

ext_modules = [  
    Extension(  
        "cyfes.wrapper",  
        ["cyfes/wrapper.pyx"],
        extra_compile_args=['-fopenmp'],
        extra_link_args=['-fopenmp'],
        include_dirs=[site_path+'/cyfes/', 
                      site_path+'/cyfes/extensions/',
                      str(Path(np.__file__).parent / 'core/include'),
                      str(Path(np.__file__).parent / '_core/include')]
    ), 
    Extension(  
        "cyfes.wrapper_f32",  
        ["cyfes/wrapper_f32.pyx"],
        include_dirs=[site_path+'/cyfes/', 
                      str(Path(np.__file__).parent / 'core/include'),
                      str(Path(np.__file__).parent / '_core/include')],
    ), 
] 

setup(
    name='CyFES',  
    description="Cython Based Fast FES Calculation Toolkit.",
    url='https://gitee.com/dechin/cy-fes',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=open('version.txt').readline().strip(),  
    license="MIT",
    author="Dechin CHEN",
    author_email="dechin.phy@gmail.com",
    install_requires=open('requirements.txt', 'r').readlines(),
    platforms="any",
    cmdclass={'build_ext': BuildExt},
    ext_modules=cythonize(ext_modules, force=True, compiler_directives={'language_level': "3"}),
    packages=find_packages(exclude=["tests", "examples", "*.pyc"]),
    include_package_data=True,
    data_files=[('cyfes', ['build/cyfes/libcufes.so',
                           'build/cyfes/libcufes.1.so',
                           'cyfes/kernels/FES.cuh',
                           'cyfes/kernels/FES_f32.cuh']),
                ]
)
