import numpy as np
import os
import matplotlib.pyplot as plt
import pydicom
import cv2

DICOM_FILES = []

PATH = "G:\\BMU\\Research\\Bio-Mechanics\\Scans\\Rockland CT\\DICOM\\Abdomen 24Y\\S30"

for file in os.listdir(PATH):
    DICOM_FILES.append(pydicom.dcmread(os.path.join(PATH, file)))

# skip files with no SliceLocation (eg scout views)
slices = []
skipcount = 0
for f in DICOM_FILES:
    if hasattr(f, 'SliceLocation'):
        slices.append(f)
    else:
        skipcount = skipcount + 1

print("skipped, no SliceLocation: {}".format(skipcount))

# ensure they are in the correct order
slices = sorted(slices, key=lambda s: s.SliceLocation)

# pixel aspects, assuming all slices are the same
ps = slices[0].PixelSpacing
ss = slices[0].SliceThickness
ax_aspect = ps[1]/ps[0]
sag_aspect = ps[1]/ss
cor_aspect = ss/ps[0]

# create 3D array
img_shape = list(slices[0].pixel_array.shape)
img_shape.append(len(slices))
img3d = np.zeros(img_shape)

# fill 3D array with the images from the files
for i, s in enumerate(slices):
    img2d = s.pixel_array
    img3d[:, :, i] = img2d

# plot 3 orthogonal slices
a1 = plt.subplot(2, 2, 1)
plt.imshow(img3d[:, :, img_shape[2]//2])
#a1.set_aspect(ax_aspect)

a2 = plt.subplot(2, 2, 2)
plt.imshow(img3d[:, img_shape[1]//2, :])
#im = cv2.cvtColor(img3d[:, img_shape[1]//2, :], cv2.COLOR_GRAY2BGR)
#im = cv2.cvtColor(c, cv2.COLOR_RGB2GREY)
print(img3d[:, img_shape[1]//2, :])
#a2.set_aspect(sag_aspect)

a3 = plt.subplot(2, 2, 3)
plt.imshow(img3d[img_shape[0]//2, :, :].T)
#a3.set_aspect(cor_aspect)



plt.show()
'''
def vtkImageToNumpy(image, pixelDims):
	# Get the 'vtkPointData' object from the 'vtkImageData' object
	pointData = image.GetPointData()
	# Get the `vtkArray` (or whatever derived type) which is needed for the `numpy_support.vtk_to_numpy` function
	arrayData = pointData.GetArray(0)
	# Convert the `vtkArray` to a NumPy array
	ArrayDicom = numpy_support.vtk_to_numpy(arrayData)
	# Reshape the NumPy array to 3D using 'ConstPixelDims' as a 'shape'
	ArrayDicom = ArrayDicom.reshape(pixelDims, order='F')

	return ArrayDicom
'''