from setuptools import setup, find_packages

setup(
    name="sysstra",
    version="0.1.4.0.7",
    description="Official Python Library for Sysstra Algo Trading",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Anurag Singh Kushwah",
    author_email="anurag@sysstra.com",
    url="https://github.com/sysstra/sysstra",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[  # Dependencies
        "requests",
        "numpy",
        "pandas_ta",
        "redis",
        "pandas"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
