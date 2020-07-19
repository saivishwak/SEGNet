"""
MIT License

Copyright (c) 2020 K Sai Vishwak

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.util.numpy_support import numpy_to_vtk, get_vtk_array_type
import os

class VTK_Widget(QVTKRenderWindowInteractor):
	""" VTK Widget """

	def __init__(self, parent):
		super(VTK_Widget, self).__init__(parent)
		self.actor = None
		self.vti_write = False
		self.renderer = vtk.vtkRenderer()
		self.renderer.SetBackground(1, 1, 1)
		self.GetRenderWindow().AddRenderer(self.renderer)
		self.iren = self.GetRenderWindow().GetInteractor()
		self.iren.Initialize()
		self.iren.Start()

	def write_vti(self, array, spacing, filename = 'Polydata.vti', origin = (0, 0, 0)):
		vtkArray = numpy_to_vtk(num_array= array.flatten('F'), deep=True,
		                    array_type=get_vtk_array_type(array.dtype))

		imageData = vtk.vtkImageData()
		imageData.SetOrigin(origin)
		imageData.SetSpacing(spacing)
		imageData.SetDimensions(array.shape)
		imageData.GetPointData().SetScalars(vtkArray)

		writer = vtk.vtkXMLImageDataWriter()
		if os.sep=='\\':
			writer.SetFileName(".\\__vtk_files__\\{}".format(filename))
		else:
			writer.SetFileName("__vtk_files__/{}".format(filename))
		writer.SetInputData(imageData)
		writer.Write()
		self.vti_write = True

	def clean_gui(self):
		self.actor = None
		self.vti_write = False
		self.renderer = vtk.vtkRenderer()
		self.renderer.SetBackground(1, 1, 1)
		self.GetRenderWindow().AddRenderer(self.renderer)
		self.iren = self.GetRenderWindow().GetInteractor()
		self.iren.Initialize()
		self.iren.Start()

	def show_render(self):
		self.reader = vtk.vtkXMLImageDataReader()
		if os.sep=='\\':
			self.reader.SetFileName('.\\__vtk_files__\\Polydata.vti')
		else:
			self.reader.SetFileName('__vtk_files__/Polydata.vti')
		self.reader.Update()

		self.surface = vtk.vtkMarchingCubes()
		self.surface.SetInputData(self.reader.GetOutput())
		self.surface.ComputeNormalsOn()
		self.surface.SetValue(0, 1)

		renderer = vtk.vtkRenderer()
		renderer.SetBackground(1, 1, 1)

		renderWindow = vtk.vtkRenderWindow()
		renderWindow.AddRenderer(renderer)

		interactor = vtk.vtkRenderWindowInteractor()
		interactor.SetRenderWindow(renderWindow)

		smoothing_iterations = 15
		pass_band = 0.001
		feature_angle = 120.0
		self.smoother = vtk.vtkWindowedSincPolyDataFilter()
		self.smoother.SetInputConnection(self.surface.GetOutputPort())
		self.smoother.SetNumberOfIterations(smoothing_iterations)
		self.smoother.BoundarySmoothingOff()
		self.smoother.FeatureEdgeSmoothingOff()
		self.smoother.SetFeatureAngle(feature_angle)
		self.smoother.SetPassBand(pass_band)
		self.smoother.NonManifoldSmoothingOn()
		self.smoother.NormalizeCoordinatesOn()
		self.smoother.Update()

		self.mapper = vtk.vtkPolyDataMapper()
		self.mapper.SetInputConnection(self.smoother.GetOutputPort())
		self.mapper.ScalarVisibilityOff()

		self.actor = vtk.vtkActor()
		self.actor.SetMapper(self.mapper)
		self.actor.GetProperty().SetColor(0.105, 0.980, 0)
		self.actor.GetProperty().SetAmbient(0.3)
		self.actor.GetProperty().SetDiffuse(0.5)
		#actor.GetProperty().SetSpecular(0.1);
		style = vtk.vtkInteractorStyleTrackballCamera()
		self.iren.SetInteractorStyle(style)
		self.renderer.AddActor(self.actor)
		self.renderer.ResetCamera()
		self.iren.Initialize()
		self.iren.Start()

	def export_stl(self, filename):
		reader = vtk.vtkXMLImageDataReader()
		if os.sep=='\\':
			reader.SetFileName('.\\__vtk_files__\\Polydata.vti')
		else:
			reader.SetFileName('__vtk_files__/Polydata.vti')
		reader.Update()

		surface = vtk.vtkMarchingCubes()
		surface.SetInputData(reader.GetOutput())
		surface.ComputeNormalsOn()
		surface.SetValue(0, 1)

		stlWriter = vtk.vtkSTLWriter()
		stlWriter.SetFileName(filename)
		stlWriter.SetInputConnection(surface.GetOutputPort())
		stlWriter.Write()