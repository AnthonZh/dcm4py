



from dcm4py import dcm2npy, npy2dcm


hu_pixels, meta_data_dicm = dcm2npy('LDCT_raw/full_1mm/L067', normalize=True) 
npy2dcm(npy_array=hu_pixels,meta_data_dict=meta_data_dicm, dcm_out_path='LDCT_test/full_1mm/L067',patient_id='L067', denormalize=True)
