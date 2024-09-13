import pydicom   
import os 

import SimpleITK as sitk
import numpy as np 
import time 

def get_original_pixels(npy_slices, data_dict,denormalize,norm_range):
    
    npy_slices = npy_slices.astype(np.float32)  
    
    for slice_number in range(npy_slices.shape[0]):
        slice_id = 'slice_' + str(slice_number)
        intercept = data_dict[slice_id]['intercept']
        slope = data_dict[slice_id]['slope']  

        if denormalize:
            npy_slices[slice_number,:,:] = denormalize_array(scaled_arr=npy_slices[slice_number,:,:],max_value=data_dict[slice_id]['max'] ,
                                                            min_value=data_dict[slice_id]['min'], norm_range=norm_range)
                                                            
        npy_slices[slice_number,:,:] -= intercept   
        if slope != 1:
            npy_slices[slice_number,:,:] = npy_slices[slice_number,:,:] / slope   
 
    return npy_slices.astype(np.int16)   


def get_pixels_hu(slices):
    image = np.stack([s.pixel_array for s in slices])  
    image = image.astype(np.uint16)
    image[image == -2000] = 0
    data_dict={}
    for slice_number in range(len(slices)):
        intercept = slices[slice_number].RescaleIntercept
        slope = slices[slice_number].RescaleSlope
        if slice_number not in data_dict.keys():
            data_dict[slice_number]={}
        data_dict[slice_number]['intercept']=intercept
        data_dict[slice_number]['slope']=slope
        if slope != 1:
            image[slice_number] = slope * image[slice_number].astype(np.float64)
            image[slice_number] = image[slice_number].astype(np.uint16)
        image[slice_number] += np.uint16(intercept)
    return np.array(image, dtype=np.uint16),data_dict
 
def normalize_array(arr, min_value, max_value, norm_range=[0,1]): 
    normalized_arr = (arr - min_value) / (max_value - min_value) 
    scaled_arr = normalized_arr * (norm_range[1] - norm_range[0]) + norm_range[0]
    return scaled_arr

def denormalize_array(scaled_arr, min_value, max_value, norm_range=[0,1]): 
    normalized_arr = (scaled_arr - norm_range[0]) / (norm_range[1] - norm_range[0]) 
    original_arr = normalized_arr * (max_value - min_value) + min_value
    return original_arr

def load_scan(path): 
    file_names = os.listdir(path) 
    slices = [pydicom.dcmread(os.path.join(path, s)) for s in file_names] 
    slices_with_filenames = list(zip(slices, file_names)) 
    slices_with_filenames.sort(key=lambda x: float(x[0].ImagePositionPatient[2])) 
    slices_sorted, file_names_sorted = zip(*slices_with_filenames) 
    
    try:
        slice_thickness = np.abs(slices_sorted[0].ImagePositionPatient[2] - slices_sorted[1].ImagePositionPatient[2])
        print('slice_thickness:', slice_thickness)
    except:
        slice_thickness = np.abs(slices_sorted[0].SliceLocation - slices_sorted[1].SliceLocation)
     
    for s in slices_sorted:
        s.SliceThickness = slice_thickness
     
    return slices_sorted, file_names_sorted



def writeSlices(series_tag_values, new_img, i, output_dir, writer,slice_meta):
    image_slice:sitk.Image = new_img[:, :, i] 
    for tag_value in series_tag_values:
        image_slice.SetMetaData(tag_value[0], tag_value[1])
    non_key_list= ['spacing','origin','intercept','slope',"0008|0012","0008|0013","0008|0060","0020|0032","0020|0013",'min','max' ]
    [non_key_list.append(tag_value[0]) for tag_value in series_tag_values]
    #add meta data for also slice_meta
    image_slice.SetMetaData("0008|0012", time.strftime("%Y%m%d"))  # Instance Creation Date
    image_slice.SetMetaData("0008|0013", time.strftime("%H%M%S"))  # Instance Creation Time
    image_slice.SetMetaData("0008|0060", "CT")  # Set the type to CT
 
    image_slice.SetMetaData("0020|0032", '\\'.join(map(str, new_img.TransformIndexToPhysicalPoint((0, 0, i)))))  # Image Position (Patient)
    image_slice.SetMetaData("0020|0013", str(i + 1))  # Instance Number
 
    image_slice.SetOrigin(slice_meta['origin']) 
    image_slice.SetSpacing(slice_meta['spacing']) 

    
    for k in slice_meta.keys():  
        if k not in non_key_list: 
            image_slice.SetMetaData(k, slice_meta[k]) 
    writer.SetFileName(os.path.join(output_dir, str(i) + '.dcm'))
    writer.Execute(image_slice)

def get_metadata(slice_path):
    mdata_dict={}
    dicom_image = sitk.ReadImage(slice_path)
    for k in dicom_image.GetMetaDataKeys():  
        mdata_dict[k]= dicom_image.GetMetaData(k) 
    #mdata_dict['direction']= dicom_image.GetDirection()
    mdata_dict['origin']= dicom_image.GetOrigin()
    mdata_dict['spacing']= dicom_image.GetSpacing() 
    return mdata_dict
 
def dcm2npy(pid_input_path, normalize=False, norm_range=[0,1]): 
 
    meta_data_dict={} 
    slices_sorted, file_names_sorted= load_scan(pid_input_path)
    hu_pixels,data_dict= get_pixels_hu(slices_sorted)
    if normalize:
        hu_pixels= hu_pixels.astype(np.float32 )   
    for i in range(len(slices_sorted)): 
        slice_id='slice_'+str(i)
        if slice_id not in meta_data_dict.keys():
                meta_data_dict[slice_id]={}
        meta_data_dict[slice_id]= get_metadata(os.path.join(pid_input_path,file_names_sorted[i]))
            
        meta_data_dict[slice_id]['intercept']= data_dict[i]['intercept']
        meta_data_dict[slice_id]['slope']= data_dict[i]['slope']
        #np.save(os.path.join(p_out_dir,slice_id+str('.npy')),hu_pixels[i,:,:]) 
        meta_data_dict[slice_id]['min']= float(np.amin(hu_pixels[i,:,:]))
        meta_data_dict[slice_id]['max']= float(np.amax(hu_pixels[i,:,:]))
        if normalize:
            hu_pixels[i,:,:]=normalize_array(arr=hu_pixels[i,:,:],min_value=meta_data_dict[slice_id]['min'],
                                               max_value=meta_data_dict[slice_id]['max'], norm_range=norm_range) 
            
    return hu_pixels, meta_data_dict
 

 

def npy2dcm(npy_array,meta_data_dict, dcm_out_path, patient_id, denormalize=False, norm_range=[0,1]): 
        
    if not os.path.exists(dcm_out_path):
        os.makedirs(dcm_out_path)
    orj_pixels = get_original_pixels(npy_slices=npy_array, data_dict=meta_data_dict, denormalize=denormalize, norm_range=norm_range) 
    new_img = sitk.GetImageFromArray(orj_pixels)
        
    modification_time = time.strftime("%H%M%S")
    modification_date = time.strftime("%Y%m%d")
    direction = new_img.GetDirection()
        
    series_tag_values = [
            ("0008|0031", modification_time),  # Series Time
            ("0008|0021", modification_date),  # Series Date
            ("0008|0008", "DERIVED\\SECONDARY"),  # Image Type
            ("0020|000e", "1.2.826.0.1.3680043.2.1125." + modification_date + ".1" + modification_time),  # Series Instance UID
            ("0020|0037", '\\'.join(map(str, (direction[0], direction[3], direction[6], direction[1], direction[4], direction[7])))),  # Image Orientation (Patient)
            ("0008|103e", patient_id)  # Series Description
        ]
 
    writer = sitk.ImageFileWriter()
    writer.KeepOriginalImageUIDOn() 
    for i in range(new_img.GetDepth()):
        slice_id = 'slice_' + str(i)
        slice_meta= meta_data_dict[slice_id]   
        writeSlices(series_tag_values, new_img, i, dcm_out_path, writer,slice_meta )
  
   