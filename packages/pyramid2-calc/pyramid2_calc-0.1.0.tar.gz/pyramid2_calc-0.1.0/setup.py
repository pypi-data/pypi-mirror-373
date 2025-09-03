from setuptools import setup, find_packages

setup(
    name="pyramid2_calc",        
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],         
    python_requires=">=3.7",
    author="Vornsk",
    author_email="kangcori@email.com",
    description="Execute ELF files and calculate the result",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Vornsk/pyramid2_calc", 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

