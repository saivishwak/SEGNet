import sys
import os
import numpy as np
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.util import numpy_support
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
#from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from scipy import ndimage

from PyQt5 import QtCore


class Dicom_Reader:
	def __init__(self, PATH = "G:\\BMU\\Research\\Bio-Mechanics\\Scans\\Rockland CT\\DICOM\\Abdomen 24Y\\S30"):
		self.reader = vtk.vtkDICOMImageReader()
		self.reader.SetDirectoryName(PATH)
		self.reader.Update()
		self._extent = self.reader.GetDataExtent()
		self.ConstPixelDims = [self._extent[1]-self._extent[0]+1, self._extent[3]-self._extent[2]+1, self._extent[5]-self._extent[4]+1]
		# Load spacing values
		self.ConstPixelSpacing = self.reader.GetPixelSpacing()

	def VTKtoNumpy(self):
		pointData = self.reader.GetOutput().GetPointData()
		arrayData = pointData.GetArray(0)
		self.ArrayDicom = numpy_support.vtk_to_numpy(arrayData)
		self.ArrayDicom = self.ArrayDicom.reshape(self.ConstPixelDims, order='F')
		return self.ArrayDicom


class VTK_Render():
	def __init__(self, reader):
		threshold = vtk.vtkImageThreshold()
		threshold.SetInputConnection(reader.GetOutputPort())
		threshold.ThresholdByLower(400)  # remove all soft tissue
		threshold.ReplaceInOn()
		threshold.SetInValue(0)  # set all values below 400 to 0
		threshold.ReplaceOutOn()
		threshold.SetOutValue(1)  # set all values above 400 to 1
		threshold.Update()
		dmc = vtk.vtkDiscreteMarchingCubes()
		dmc.SetInputConnection(threshold.GetOutputPort())
		dmc.GenerateValues(1, 1, 1)
		dmc.Update()
		smoothing_iterations = 15
		pass_band = 0.001
		feature_angle = 120.0
		smoother = vtk.vtkWindowedSincPolyDataFilter()
		smoother.SetInputConnection(dmc.GetOutputPort())
		smoother.SetNumberOfIterations(smoothing_iterations)
		smoother.BoundarySmoothingOff()
		smoother.FeatureEdgeSmoothingOff()
		smoother.SetFeatureAngle(feature_angle)
		smoother.SetPassBand(pass_band)
		smoother.NonManifoldSmoothingOn()
		smoother.NormalizeCoordinatesOn()
		smoother.Update()
		mapper = vtk.vtkPolyDataMapper()
		mapper.SetInputConnection(smoother.GetOutputPort())
		self.actor = vtk.vtkActor()
		self.actor.SetMapper(mapper)
		self.actor.GetProperty().SetColor(0.8,0.8,0.8) # (R,G,B)
		#actor.GetProperty().SetRepresentationToWireframe()  
		self.actor.GetProperty().SetRepresentationToSurface()

class MplCanvas(FigureCanvasQTAgg):

	def __init__(self, parent=None, width=10, height= 10, dpi = 100):
		fig = Figure(figsize=(width, height), dpi=dpi, facecolor='black')
		self.axes = fig.add_subplot(1,1,1)
		super(MplCanvas, self).__init__(fig)

class Panel(QtWidgets.QWidget):

	def __init__(self, title = "Enter title"):
		super().__init__()
		self.Title_Label = QLabel("{}".format(title), self)
		self.Title_Label.setStyleSheet('QLabel { background: #b5b5b5; border-radius: 0px; font-size: 12px; padding: 5px; font-weight: 485}')
		self.Dicom_Frame = QLabel(self)
		self.Dicom_Frame.setStyleSheet('QLabel { background: #b5b5b5; border-radius: 0px; font-size: 12px; padding: 5px; font-weight: 485}')
		self.data = np.zeros((512, 512))
		self.sc = MplCanvas(self, width= 10, height= 10, dpi= 100)
		#self.data = cv2.addWeighted(self.data, 100 - contra, self.data, 0, 0 - bright) --- contrast and brightness
		#self.data = ndimage.rotate(self.data, 90)
		self.sc.axes.imshow(self.data, cmap = 'gray')
		self.sc.axes.xaxis.set_visible(False)
		self.sc.axes.yaxis.set_visible(False)
		self.text_1 = ""
		self.text_2 = ""
		self.text_3 = ""
		self.text_4 = ""
		self.sc.axes.text(-280, 250, '{}'.format(self.text_1), fontsize=10, color = 'white')
		self.sc.axes.text(700, 250, '{}'.format(self.text_2), fontsize=10, color = 'white')
		self.sc.axes.text(260, 0, '{}'.format(self.text_3), fontsize=10, color = 'white')
		self.sc.axes.text(260, 550, '{}'.format(self.text_4), fontsize=10, color = 'white')
		
		self.Dicom_Frame = self.sc

		self.Max_Win = QLabel(self)
		#self.pixmap = QPixmap()
		#self.pixmap_Win = QPixmap('.\\Images\\maximize-window.png')
		#self.Max_Win.setPixmap(self.pixmap_Win)
		#self.Max_Win.setScaledContents(True)
		self.Max_Win.setFixedSize(18, 25)
		self.Max_Win.setStyleSheet('QLabel { background: #b5b5b5; border-radius: 0px;}')
		self.ScrollBar = QScrollBar(self)
		self.ScrollBar.setOrientation(Qt.Vertical)
		self.ScrollBar.setObjectName("ScrollBar")

	def update_text(self):
		#print("triggerred")
		self.sc.axes.text(-280, 250, '{}'.format(self.text_1), fontsize=10, color = 'white')
		self.sc.axes.text(700, 250, '{}'.format(self.text_2), fontsize=10, color = 'white')
		self.sc.axes.text(260, 0, '{}'.format(self.text_3), fontsize=10, color = 'white')
		self.sc.axes.text(260, 550, '{}'.format(self.text_4), fontsize=10, color = 'white')
	
	def update_Images(self):
		self.sc.axes.cla()
		self.sc.axes.text(-280, 250, '{}'.format(self.text_1), fontsize=10, color = 'white')
		self.sc.axes.text(700, 250, '{}'.format(self.text_2), fontsize=10, color = 'white')
		self.sc.axes.text(260, 0, '{}'.format(self.text_3), fontsize=10, color = 'white')
		self.sc.axes.text(260, 550, '{}'.format(self.text_4), fontsize=10, color = 'white')
		self.sc.axes.imshow(self.data, cmap = 'gray')


class MainWindow(QMainWindow):
	textChanged = QtCore.Signal(str)
	def __init__(self):
		super().__init__()
		self.TITLE = "SegNet"
		self.WIDTH = 900
		self.HEIGHT = 500
		self.InitUI()

	def InitUI(self):
		self.setWindowTitle(self.TITLE)
		self.setMinimumSize(self.WIDTH, self.HEIGHT)
		self.setWindowIcon(QIcon('.\\Images\\Logo.png'))
		self.setStyleSheet("""QMainWindow{
			background-color: white;}""")
		self.Grid_layout = QGridLayout()
		#self.Grid_layout.setColumnStretch(0, 3)
		self.Grid_layout.setSpacing(2)
		self.frame = QFrame()

		self.Panel_1 = Panel('Axial Slice')
		self.Panel_1.text_1 = "R"
		self.Panel_1.text_2 = "L"
		self.Panel_1.text_3 = "A"
		self.Panel_1.text_4 = "P"
		self.Panel_1.update_text()
		#self.Panel_1.ScrollBar.sliderMoved.connect(lambda: self.Panel_1.sliderval(self.Panel_1.ScrollBar.value()))
		#self.Panel_1.ScrollBar.valueChanged.connect(lambda: self.Panel_1.sliderval(self.Panel_1.ScrollBar.value()))
		self.Grid_layout.addWidget(self.Panel_1.Title_Label, 0, 0)
		self.Grid_layout.addWidget(self.Panel_1.Max_Win, 0, 1)
		self.Grid_layout.addWidget(self.Panel_1.Dicom_Frame, 1, 0)
		self.Grid_layout.addWidget(self.Panel_1.ScrollBar, 1, 1)

		self.Panel_2 = Panel('Sagittal Slice')
		self.Panel_2.text_1 = "P"
		self.Panel_2.text_2 = "A"
		self.Panel_2.text_3 = "T"
		self.Panel_2.text_4 = "B"
		self.Panel_2.update_text()
		self.Grid_layout.addWidget(self.Panel_2.Title_Label, 0, 2)
		self.Grid_layout.addWidget(self.Panel_2.Max_Win, 0, 3)
		self.Grid_layout.addWidget(self.Panel_2.Dicom_Frame, 1, 2)
		self.Grid_layout.addWidget(self.Panel_2.ScrollBar, 1, 3)

		self.Panel_3 = Panel('Coronal Slice')
		self.Panel_3.text_1 = "R"
		self.Panel_3.text_2 = "L"
		self.Panel_3.text_3 = "T"
		self.Panel_3.text_4 = "B"
		self.Panel_3.update_text()
		self.Grid_layout.addWidget(self.Panel_3.Title_Label, 2, 0)
		self.Grid_layout.addWidget(self.Panel_3.Max_Win, 2, 1)
		self.Grid_layout.addWidget(self.Panel_3.Dicom_Frame, 3, 0)
		self.Grid_layout.addWidget(self.Panel_3.ScrollBar, 3, 1)

		self.Panel_4 = Panel('Volume')
		self.Panel_4.Dicom_Frame = QVTKRenderWindowInteractor(self.frame)
		self.ren = vtk.vtkRenderer()
		self.ren.SetBackground(1, 1, 1)

		self.Panel_4.Dicom_Frame.GetRenderWindow().AddRenderer(self.ren)
		self.iren = self.Panel_4.Dicom_Frame.GetRenderWindow().GetInteractor()
		self.Grid_layout.addWidget(self.Panel_4.Title_Label, 2, 2)
		self.Grid_layout.addWidget(self.Panel_4.Max_Win, 2, 3)
		self.Grid_layout.addWidget(self.Panel_4.Dicom_Frame, 3, 2)
		self.Grid_layout.addWidget(self.Panel_4.ScrollBar, 3, 3)


		get_dic = QAction('&Import DICOM...', parent = self)
		get_dic.setShortcut('Ctrl+I')
		get_dic.setStatusTip('Select DICOM Folder')
		
		get_dic.triggered.connect(self.Panel_1.update_text)
		
		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(get_dic)

		#self.vtk = VTK_Render(self.DICOM_DATA.reader)
		#self.ren.AddActor(self.vtk.actor)
		#self.ren.ResetCamera()
		self.frame.setLayout(self.Grid_layout)
		self.setCentralWidget(self.frame)
		self.iren.Initialize()
		self.iren.Start()
		self.show()
		

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	sys.exit(app.exec_())
