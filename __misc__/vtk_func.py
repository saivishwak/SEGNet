import vtk
from vtk.util import numpy_support

def Apply_Threshold(reader, lower_bound, in_value, out_value):
	threshold = vtk.vtkImageThreshold()
	threshold.SetInputConnection(reader.GetOutputPort())
	threshold.ThresholdByLower(lower_bound)  # remove all soft tissue
	threshold.ReplaceInOn()
	threshold.SetInValue(in_value)  # set all values below 400 to 0
	threshold.ReplaceOutOn()
	threshold.SetOutValue(out_value)  # set all values above 400 to 1
	threshold.Update()
	return threshold

def DMC(threshold):
	dmc = vtk.vtkDiscreteMarchingCubes()
	dmc.SetInputConnection(threshold.GetOutputPort())
	dmc.GenerateValues(1, 1, 1)
	dmc.Update()
	return dmc

def Win_Renderer(WIN_WIDTH, WIN_HEIGHT):
	window = vtk.vtkRenderWindow()
	# Sets the pixel width, length of the window.
	window.SetSize(WIN_WIDTH, WIN_HEIGHT)

	interactor = vtk.vtkRenderWindowInteractor()
	interactor.SetRenderWindow(window)

	renderer = vtk.vtkRenderer()
	window.AddRenderer(renderer)
	renderer.AddActor(actor)
	renderer.SetBackground(1.0, 1.0, 1.0)

	camera = renderer.MakeCamera()
	camera.SetPosition(-500.0, 245.5, 122.0)
	camera.SetFocalPoint(301.0, 245.5, 122.0)
	camera.SetViewAngle(30.0)
	camera.SetRoll(-90.0)
	renderer.SetActiveCamera(camera)

	window.Render()
	interactor.Start()

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