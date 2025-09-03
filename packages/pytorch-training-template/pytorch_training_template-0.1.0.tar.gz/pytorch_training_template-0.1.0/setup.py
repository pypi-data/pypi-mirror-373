from setuptools import setup, find_packages

setup(
    name="pytorch_training_template",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A modular PyTorch training template for deep learning tasks",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pytorch-training-template",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0",
        "torchvision>=0.15",
        "numpy>=1.23",
        "matplotlib>=3.7",
        "tqdm>=4.65",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)