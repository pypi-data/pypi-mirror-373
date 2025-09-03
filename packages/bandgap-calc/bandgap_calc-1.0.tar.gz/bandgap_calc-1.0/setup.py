from setuptools import setup, find_packages

setup(
    name="bandgap-calc",  # pip install name
    version="1.0",
    author="SIMPAL KUMAR SUMAN",
    author_email="advancedbionanoxplore@gmail.com",
    description="A PyQt5-based GUI for bandgap estimation using Tauc plots",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bandgap-calc",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "scikit-learn",
        "PyQt5"
    ],
    entry_points={
        "console_scripts": [
            "bandgap-calc=bandgap_calc.gui:main"
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)


