
# dcm4py

`dcm4py` is a Python library for converting DICOM images to NumPy arrays and vice versa, allowing you to convert NumPy arrays back into DICOM images.

## Features

- Convert DICOM images to NumPy arrays for easy manipulation.
- Optionally normalize the NumPy arrays with a custom range.
- Convert processed NumPy arrays back into DICOM format.

## Installation

You can install requirements via pip:

```bash
pip install -r requirements.txt
```

## Usage

### Convert DICOM to NumPy

To generate a numpy array from DICOM images, use the dcm2npy function and input the path to the directory of DICOM images. The `normalize` parameter to `True`  to normalize the array values, and the range to normalize to can be defined in the `norm_range` parameter.

```python
from dcm4py import dcm2npy
slices, dataset = dcm2npy('/path/to/input_directory', normalize=True, norm_range=(0, 1))
```

### Convert NumPy to DICOM

After processing the `slices` NumPy array, you can convert it back to DICOM images in a specified folder using the npy2dcm function. If the array was previously normalized, it can be denormalized by setting the `denormalize` parameter to `True`. The current range of the array must be specified.

```python
from dcm4py import npy2dcm
npy2dcm(output_path='/path/to/output_directory', slices=slices, dataset=dataset, denormalize=True, current_range=(0, 1))
```
