from pydicom import dcmread

ds = dcmread("anonimized_SPECT_1h.dcm")
print(ds)