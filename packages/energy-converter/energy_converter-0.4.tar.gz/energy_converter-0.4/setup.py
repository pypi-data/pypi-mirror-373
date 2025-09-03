from setuptools import setup, find_packages

setup(
    name="energy-converter",
    version="0.4",
    packages=find_packages(),
    install_requires=[
        "pandas",
    ],
    description="Converter for translating from different time intervals and different units of measure",
    author="Artem Pleshakov",
    author_email="Artem.Pleshakov@imby.energy",
    url="https://github.com/Artem.Pleshakov/energy-converter",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
