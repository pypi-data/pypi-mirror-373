import os
import sys
import torch
from setuptools import setup, find_packages
from torch.utils.cpp_extension import CUDAExtension, BuildExtension

# Compilation flags for different GPU architectures
arch_flags = [
    # V100 (Volta)
    '-gencode=arch=compute_70,code=sm_70',
    
    # A100 (Ampere)
    '-gencode=arch=compute_80,code=sm_80',
    
    # RTX 30/40 series (Ampere)
    '-gencode=arch=compute_86,code=sm_86',
    
    # RTX 4090 & L4 (Ada Lovelace)
    '-gencode=arch=compute_89,code=sm_89',
    
    # PTX fallback for future compatibility
    '-gencode=arch=compute_89,code=compute_89'
]

# Check if CUDA source files exist
cuda_src_dir = 'biwkv4'  # Relative to setup.py directory
cpp_file = os.path.join(cuda_src_dir, 'biwkv4_op_new.cpp')
cu_file = os.path.join(cuda_src_dir, 'biwkv4_cuda_new.cu')

if not os.path.exists(cpp_file):
    raise FileNotFoundError(f"C++ source file not found: {cpp_file}")
if not os.path.exists(cu_file):
    raise FileNotFoundError(f"CUDA source file not found: {cu_file}")

ext_modules = [
    CUDAExtension(
        name='biwkv4_cuda',  # Python module name for import
        sources=[cpp_file, cu_file],
        extra_compile_args={
            'cxx': ['-O3', '-fPIC'],
            'nvcc': [
                '-O3', 
                '--use_fast_math',
                '--maxrregcount=60',
                '--ptxas-options=-v',  # Show register usage
                '--compiler-options=-fPIC'
            ] + arch_flags
        }
    )
]

# Platform compatibility check
if sys.platform == 'win32':
    raise RuntimeError("CUDA extension compilation not supported on Windows")
elif sys.platform == 'darwin':
    print("Warning: macOS has limited CUDA support, recommend compiling on Linux")

# Read README for long description
long_description = ""
if os.path.exists('README.md'):
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='biwkv4-cuda',
    version='0.3.0',
    author='Ashen002',
    author_email='zourenjiex@gmail.com',
    description='BiWKV4 CUDA Kernel for PyTorch',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    ext_modules=ext_modules,
    cmdclass={'build_ext': BuildExtension},
    install_requires=[
        'torch>=2.0.0',  # Ensure support for latest CUDA extension API
        'torchvision>=0.15.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Operating System :: POSIX :: Linux',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.8',
    include_package_data=True,
    zip_safe=False,
    keywords=['pytorch', 'cuda', 'biwkv4', 'vision-rwkv', 'deep-learning'],
)