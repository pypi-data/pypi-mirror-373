from setuptools import setup, find_packages

setup(
    name="sravanthi_tadi",
    version="0.1",
    packages=find_packages(),
    author="Rakesh",
    author_email="your.email@example.com",
    description="A personal intro package dedicated to Sravanthi",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
