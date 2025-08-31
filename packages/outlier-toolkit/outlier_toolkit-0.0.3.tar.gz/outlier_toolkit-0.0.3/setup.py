from setuptools import setup, find_packages

setup(
    name="outlier_toolkit",
    version="0.0.3",
    author="Irene Betsy D",
    author_email="betsydnicholraja@gmail.com",
    license="Apache License 2.0",
    description="A Python library for identifying and handling outliers",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/irenebetsy/outlier_library",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    keywords="outlier IQR ZScore Winsorization binning data preprocessing analytics",
    project_urls={
        "Bug Tracker": "https://github.com/irenebetsy/outlier_library/issues",
        "Documentation": "https://github.com/irenebetsy/outlier_library#readme",
        "Source Code": "https://github.com/irenebetsy/outlier_library",
    },
)
