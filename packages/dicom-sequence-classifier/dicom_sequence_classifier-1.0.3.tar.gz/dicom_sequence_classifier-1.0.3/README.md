<h1 align="center"> DICOM Sequence Classifier</h1><br>

## Table of Contents

- [Introduction](#introduction)
- [Supported MR Manufacturers](#supported-MR-manufacturers)
- [Supported Series](#supported-series)
- [Installation](#installation)
- [Example](#example)
- [Authors](#authors)
- [Feedback](#feedback)
- [License](#license)
- [Changelog](#changelog)


## Introduction

**DICOM Sequence Classifier** is a Python package based on Pydicom that scans, analyzes and try to classifies DICOM sequences by type.
The classification is based on DICOM metadata.


## Supported MR manufacturers

* **GE**
* **Siemens**
* **Philips**


## Supported Series

* **3D T1**
* **2D T2**
* **2D Flair**
* **2D Flair**
* **3D Flair**
* **3D Venous**
* **DTI**
* **PET**

## Installation

Pipy (#TODO Add Link)

```
pip3 install swane
```

## Example

Pipy (#TODO Add Link)

```
path = "your_dicom_file_path"
dicom = load_dicom_file(path)
meta = extract_metadata(dicom)
print("meta classification", classify_dicom(meta))
```

## Authors
**DICOM Sequence Classifier** is designed and developed by [LICE Neuroimaging Commission](https://www.lice.it/), term 2021-2024, with the main contribution by [Power ICT Srls](https://powerictsoft.com/).


## Feedback
If you want to leave us your feedback on **SWANe** please fill the following [**Google Form**](https://forms.gle/ewUrNzwjQWanPxVF7).

For any advice on common problems or issues, please contact us at the following e-mail: [dev@lice.it](mailto:dev@lice.it).


## License

This project is licensed under the [MIT](LICENSE) License - see the [LICENSE](LICENSE) file for details


## Changelog

### [1.0.0] - 2025-08-02

#### Added

- **Load DICOM method**
- **Extract Metadata method**
- **Classify DICOM method**