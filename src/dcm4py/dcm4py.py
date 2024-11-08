from typing import Iterable
import pydicom
import numpy as np
import os
#Readme & MIT License & dependencies
def dcm2npy(input_path: str, normalize=False, norm_range:Iterable=(0,1)):
    r"""
    Converts a directory of DICOM slices into a numpy array.

    Parameters
    ----------
    input_path : string
        The path to the directory containing all the DICOM slices.
    normalize: bool, optional
        If the returned numpy arrays should be normalized. Defaults to ``normalize=False``.
    norm_range: array_like, optional
        If normalize is True, the range of values which the numpy array should be normalized to.
    
    Returns
    -------
    slices : ndarray
        A 3-dimensional ndarray which contains all the slice's pixel arrays in order.
    dataset: ndarray
        An ndarray which contains the meta data for each slice in the same order as ``slices``.
    """
    file_names = os.listdir(input_path) 
    dataset = [pydicom.dcmread(os.path.join(input_path, s)) for s in file_names] 
    dataset.sort(key=lambda x: float(x.ImagePositionPatient[2])) 
    slices = [pydicom.pixels.pixel_array(s) for s in dataset]
    dataset = np.array(dataset)
    slices = np.array(slices)
    
    if normalize:
        assert norm_range is not None
        slices = normalize_array(slices, min_value=0, max_value=4095, norm_range=norm_range)

    return slices, dataset

def normalize_array(arr: np.ndarray, min_value: float, max_value: float, norm_range: Iterable=(0,1)): 
    r"""
    Normalizes an array to a specific range.

    Parameters
    ----------
    arr : ndarray
        The ndarray to be normalized.
    min_value : float
        The minimum value of the array.
    max_value : float
        The maximum value of the array.
    norm_range : array_like, optional
        The range to normalize the array. Defaults to ``norm_range=(0, 1)``.
    
    Returns
    -------
    scaled_arr : ndarray
        An ndarray which is normalized to ``norm_range``.
    """
    normalized_arr = (arr - min_value) / (max_value - min_value) 
    scaled_arr = normalized_arr * (norm_range[1] - norm_range[0]) + norm_range[0]
    return scaled_arr

def npy2dcm(output_path:str, slices:np.ndarray, dataset:np.ndarray, denormalize:bool=False, denormalize_range:Iterable=None):
    r"""
    Converts a ndarray into a series of DICOM files.

    Parameters
    ----------
    output_path : str
        The path to the directory for the new DICOM files.
    slices : ndarray
        An array of slices to be saved as new DICOM files.
    dataset : ndarray
        An array of pydicom datasets containing the metadata for each corresponding slice in ``slices``.
    denormalize : bool
        If the slices need to be denormalized.
    denormalize_range : Iterable
        The range of values that the array is currently normalized to.
    """
    assert len(slices) == len(dataset)
    if denormalize:
        assert denormalize_range is not None
        slices = normalize_array(slices, denormalize_range[0], denormalize_range[1], norm_range=(0, 4095)).astype(np.uint16)

    for i in range(len(slices)):
        ds = dataset[i]
        pixel_array = slices[i]
        pydicom.pixels.set_pixel_data(ds, pixel_array, ds.PhotometricInterpretation, ds.BitsStored)
        ds.save_as(os.path.join(output_path, f'Slice {i}.dcm'))