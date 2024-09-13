
# dcm4py

`dcm4py` is a Python library for converting DICOM images to NumPy arrays and vice versa, allowing you to convert NumPy arrays back into DICOM images.

## Features

- Convert DICOM images to NumPy arrays for easy manipulation.
- Optionally normalize the NumPy arrays with a custom range.
- Convert processed NumPy arrays back into DICOM format.

## Installation

You can install requirements via pip (if applicable, otherwise include manual installation instructions):

```bash
pip install -r requirements.txt
```

## Usage

### Convert DICOM to NumPy

To generate a NumPy array from DICOM images, submit the path to your raw DICOM image. You can set the `normalize` parameter to `True` if you want to normalize the array values, and you can define a normalization range.

```python
hu_pixels, meta_data_dict = dcm2npy('LDCT_raw/full_1mm/L067', normalize=True, norm_range=[0,1])
```

### Convert NumPy to DICOM

After processing the `hu_pixels` NumPy array, you can convert it back to DICOM images using the following code:

```python
npy2dcm(npy_array=hu_pixels, meta_data_dict=meta_data_dict, dcm_out_path='LDCT_test/full_1mm/L067', patient_id='L067', denormalize=True, norm_range=[0,1])
```
