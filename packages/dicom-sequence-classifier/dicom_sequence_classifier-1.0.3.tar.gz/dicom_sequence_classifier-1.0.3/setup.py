from setuptools import setup, find_packages

setup(
    name="dicom-sequence-classifier",
    description="Python package based on Pydicom that scans, analyzes and try to classifies DICOM sequences by type",
    version="1.0.3",
    author="LICE - Commissione Neuroimmagini",
    author_email="dev@lice.it",
    packages=find_packages(),
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license='MIT',
    url="https://github.com/LICE-dev/dicom_sequence_classifier",
    install_requires=[
        "pydicom>=3.0.0"
    ],
    include_package_data=True,
)
