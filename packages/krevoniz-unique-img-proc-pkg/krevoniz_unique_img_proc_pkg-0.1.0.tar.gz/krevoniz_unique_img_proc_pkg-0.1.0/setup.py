from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="krevoniz_unique_img_proc_pkg",
    version="0.1.0",
    author="Krevoniz",
    author_email="krevoniz@gmail.com",
    description="Pacote de processamento de imagens usando Python",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/krevoniz/image_processing_pkg",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Portuguese (Brazilian)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
)