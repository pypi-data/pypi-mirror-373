from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name="paGating",
    version="0.1.0",
    author="Aaryan Guglani",
    author_email="aaryanguglani.cs21@rvce.edu.in",
    description="Parameterized Activation Gating Framework for Flexible and Efficient Neural Networks",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/guglxni/paGating",
    project_urls={
        "Bug Tracker": "https://github.com/guglxni/paGating/issues",
        "Source Code": "https://github.com/guglxni/paGating",
        "Documentation": "https://github.com/guglxni/paGating#readme",
    },
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "torch>=1.9.0",
        "numpy>=1.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
        ],
        "export": [
            "onnx>=1.14.0",
            "onnxruntime>=1.15.0",
            "coremltools>=7.0",
        ],
        "benchmark": [
            "matplotlib>=3.4.0",
            "pandas>=1.3.0",
            "seaborn>=0.11.0",
            "tqdm>=4.61.0",
        ],
        "ml": [
            "transformers>=4.30.0",
            "datasets>=2.0.0",
            "accelerate>=0.20.0",
            "tf-keras>=2.13.1",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="deep-learning neural-networks activation-functions pytorch gating transformer",
    license="Apache-2.0"
)