from setuptools import setup, find_packages

# Simple setup.py without license issues
setup(
    name="prismintelligence",
    version="0.0.2",
    author="Olaoluwasubomi Aduloju & Prism Intelligence",
    author_email="i@olaoluwasubomi.com",
    description="AI-Powered Image Intelligence Engine - See what others can't",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Prism-Intelligence/Prism",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=1.9.0",
        "torchvision>=0.10.0", 
        "transformers>=4.20.0",
        "ultralytics>=8.0.0",
        "Pillow>=8.0.0",
        "numpy>=1.21.0",
        "requests>=2.25.0",
    ],
    include_package_data=True,
)