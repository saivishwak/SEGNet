import sys
import os
import numpy as np
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.util import numpy_support
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.TITLE = "DICOM Render"
		self.WIDTH = 800
		self.HEIGHT = 700
		self.InitUI()

	def InitUI(self):
		self.setWindowTitle(self.TITLE)
		self.setMinimumSize(self.WIDTH, self.HEIGHT)
		#self.setFixedWidth(self.WIDTH)
		#self.setFixedHeight(self.HEIGHT)  
		self.setWindowIcon(QIcon('.\\Images\\Logo.png'))
		self.setStyleSheet("""QMainWindow{
			background-color: black;}""")
		self.layout = QGridLayout()
		self.layout.setColumnStretch(0, 1)
		self.layout.setColumnStretch(1, 3)
		self.frame = QFrame()

		self.img_1 = QLabel(self)
		pixmap = QPixmap('.\\Images\\Black_color.jpg')
		self.img_1.setPixmap(pixmap)
		self.img_1.setScaledContents(True)

		self.img_2 = QLabel(self)
		pixmap_2 = QPixmap('.\\Images\\Black_color.jpg')
		self.img_2.setPixmap(pixmap_2)
		self.img_2.setScaledContents(True)

		self.img_3 = QLabel(self)
		pixmap_3 = QPixmap('.\\Images\\Black_color.jpg')
		self.img_3.setPixmap(pixmap_3)
		self.img_3.setScaledContents(True)
		#self.show()
		#self.get_dir()
		#self.layout.addWidget(self.img_1, 0, 0)
		self.horizontalScrollBar_1 = QScrollBar(self)
		self.horizontalScrollBar_1.setOrientation(Qt.Horizontal)
		self.horizontalScrollBar_1.setObjectName("horizontalScrollBar_1")
		self.horizontalScrollBar_1.sliderMoved.connect(self.sliderval)
		self.horizontalScrollBar_1.valueChanged.connect(self.sliderval)
		
		#self.layout.addWidget(self.horizontalScrollBar_1, 1, 0)

		#self.layout.addWidget(self.img_2, 0, 1)
		self.horizontalScrollBar_2 = QScrollBar(self)
		self.horizontalScrollBar_2.setOrientation(Qt.Horizontal)
		self.horizontalScrollBar_2.setObjectName("horizontalScrollBar_2")
		self.horizontalScrollBar_2.sliderMoved.connect(self.sliderval)
		self.horizontalScrollBar_2.valueChanged.connect(self.sliderval)
		
		#self.layout.addWidget(self.horizontalScrollBar_2, 1, 1)

		#self.layout.addWidget(self.img_3, 3, 0)
		self.horizontalScrollBar_3 = QScrollBar(self)
		self.horizontalScrollBar_3.setOrientation(Qt.Horizontal)
		self.horizontalScrollBar_3.setObjectName("horizontalScrollBar_3")
		self.horizontalScrollBar_3.sliderMoved.connect(self.sliderval)
		self.horizontalScrollBar_3.valueChanged.connect(self.sliderval)
		
		#self.layout.addWidget(self.horizontalScrollBar_3, 2, 0)

		vertical = QVBoxLayout()
		vertical.addWidget(self.img_1)
		vertical.addWidget(self.horizontalScrollBar_1)
		vertical.addWidget(self.img_2)
		vertical.addWidget(self.horizontalScrollBar_2)
		vertical.addWidget(self.img_3)
		vertical.addWidget(self.horizontalScrollBar_3)

		self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
		self.ren = vtk.vtkRenderer()
		self.ren.SetBackground(0, 0, 0)
		self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
		self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

		self.layout.addLayout(vertical, 0, 0)
		self.layout.addWidget(self.vtkWidget, 0, 1)

	
		exitAct = QAction("&Exit", self)
		exitAct.setShortcut('Ctrl+Q')
		exitAct.setStatusTip('Exit application')
		exitAct.triggered.connect(qApp.quit)

		get_dic = QAction('&Import DICOM', self)
		get_dic.setShortcut('Ctrl+O')
		get_dic.setStatusTip('Select DICOM Folder')
		get_dic.triggered.connect(self.get_dir)

		render_stl = QAction('&Render 3D', self)
		render_stl.setShortcut('Ctrl+R')
		render_stl.setStatusTip('Render 3D Folder')
		render_stl.triggered.connect(self.VTK_Render)

		set_back_B = QAction('&Black', self)
		set_back_B.setShortcut('Ctrl+B')
		set_back_B.setStatusTip("change BG Color to Black")
		set_back_B.triggered.connect(self.set_background_black)

		set_back_W = QAction('&White', self)
		set_back_W.setShortcut('Ctrl+W')
		set_back_W.setStatusTip("change BG Color to Black")
		set_back_W.triggered.connect(self.set_background_white)

		self.ThreshScrollBar = QSlider(self)
		self.ThreshScrollBar.setOrientation(Qt.Horizontal)
		self.ThreshScrollBar.valueChanged.connect(self.updateLabel)
		self.ThreshScrollBar.setRange(0, 800)
		#self.ThreshScrollBar.setPageStep(5)
		self.ThreshScrollBar.setFocusPolicy(Qt.NoFocus)
		toolbar = self.addToolBar("toolbar")
		toolbar.setStyleSheet("background-color:white;")
		toolbar.addWidget(self.ThreshScrollBar)
		self.label = QLabel("0",self)
		self.label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
		self.label.setMinimumWidth(80)
		self.label.setStyleSheet('QLabel { background: #9c9c9c; border-radius: 3px; font-size: 15px}') 
		toolbar.addWidget(self.label)

		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		toolsMenu = menubar.addMenu('&Tools')
		fileMenu.addAction(get_dic)
		fileMenu.addAction(exitAct)
		toolsMenu.addAction(render_stl)
		BG_Menu = QMenu('&BG Color', self)
		BG_Menu.addAction(set_back_B)
		BG_Menu.addAction(set_back_W)
		toolsMenu.addMenu(BG_Menu)

		self.frame.setLayout(self.layout)
		self.setCentralWidget(self.frame)
		#self.VTK_Render()
		self.show()
		self.get_dir()
		self.horizontalScrollBar_3.setMaximum(len(self.ArrayDicom)-1)
		self.horizontalScrollBar_2.setMaximum(len(self.ArrayDicom)-1)
		self.horizontalScrollBar_1.setMaximum(len(self.ArrayDicom)-1)

	def updateLabel(self, value):
		self.label.setText(str(value))

	def set_background_black(self):
		self.ren.SetBackground(0, 0, 0)

	def set_background_white(self):
		self.ren.SetBackground(1, 1, 1)

	def vtkImageToNumpy(self, image, pixelDims):
		pointData = image.GetPointData()
		arrayData = pointData.GetArray(0)
		ArrayDicom = numpy_support.vtk_to_numpy(arrayData)
		ArrayDicom = ArrayDicom.reshape(pixelDims, order='F')

		return ArrayDicom

	def Image_write(self):
		reader = vtk.vtkDICOMImageReader()
		reader.SetDirectoryName(self.PATH)
		reader.Update()
		_extent = reader.GetDataExtent()
		ConstPixelDims = [_extent[1]-_extent[0]+1, _extent[3]-_extent[2]+1, _extent[5]-_extent[4]+1]
		# Load spacing values
		ConstPixelSpacing = reader.GetPixelSpacing()

		self.ArrayDicom = np.array(self.vtkImageToNumpy(reader.GetOutput(), ConstPixelDims))
		cv2.imwrite(".\\Images\\img_1.png", cv2.resize(self.ArrayDicom[:, :, 0], (200, 200)))
		cv2.imwrite(".\\Images\\img_2.png", cv2.resize(self.ArrayDicom[:, 0, :], (200, 200)))
		cv2.imwrite(".\\Images\\img_3.png", cv2.resize(self.ArrayDicom[0, :, :], (200, 200)))

	def get_dir(self):
		options = QFileDialog.Options()
		fileName = str(QFileDialog.getExistingDirectory())
		if fileName:
			if os.sep=='\\':
			    fileName=fileName.replace('/', "\\")
		self.PATH = fileName
		print(self.PATH)
		self.Axial_images = []
		self.Sagittal_images = []
		self.Coronal_images = []
		
		reader = vtk.vtkDICOMImageReader()
		reader.SetDirectoryName(self.PATH)
		reader.Update()
		_extent = reader.GetDataExtent()
		ConstPixelDims = [_extent[1]-_extent[0]+1, _extent[3]-_extent[2]+1, _extent[5]-_extent[4]+1]
		# Load spacing values
		ConstPixelSpacing = reader.GetPixelSpacing()

		self.ArrayDicom = np.array(self.vtkImageToNumpy(reader.GetOutput(), ConstPixelDims))
		cv2.imwrite(".\\Images\\img_1.png", cv2.resize(self.ArrayDicom[:, :, 0], (200, 200)))
		cv2.imwrite(".\\Images\\img_2.png", cv2.resize(self.ArrayDicom[:, 0, :], (200, 200)))
		cv2.imwrite(".\\Images\\img_3.png", cv2.resize(self.ArrayDicom[0, :, :], (200, 200)))
		self.img_1.setPixmap(QPixmap(".\\Images\\img_1.png"))
		self.img_2.setPixmap(QPixmap(".\\Images\\img_2.png"))
		self.img_3.setPixmap(QPixmap(".\\Images\\img_3.png"))
		self.clean_gui()
		
	def sliderval(self):
		cv2.imwrite(".\\Images\\img_1.png", cv2.resize(self.ArrayDicom[:, :, self.horizontalScrollBar_1.value()], (200, 200)))
		cv2.imwrite(".\\Images\\img_2.png", cv2.resize(self.ArrayDicom[:, self.horizontalScrollBar_2.value(),:], (200, 200)))
		cv2.imwrite(".\\Images\\img_3.png", cv2.resize(self.ArrayDicom[self.horizontalScrollBar_3.value(), :, :], (200, 200)))
		self.img_1.setPixmap(QPixmap(".\\Images\\img_1.png"))
		self.img_2.setPixmap(QPixmap(".\\Images\\img_2.png"))
		self.img_3.setPixmap(QPixmap(".\\Images\\img_3.png"))

	def sliderval_Thresh(self):
		self.VTK_Render()

	def update_gui(self):
		self.clean_gui()
		self.VTK_Render()
		self.show()

	def clean_gui(self):
		self.ren = vtk.vtkRenderer()
		self.ren.SetBackground(0, 0, 0)
		self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
		self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

	def Apply_Threshold(self, reader, lower_bound, in_value, out_value):
		threshold = vtk.vtkImageThreshold()
		threshold.SetInputConnection(reader.GetOutputPort())
		threshold.ThresholdByLower(lower_bound)  # remove all soft tissue
		threshold.ReplaceInOn()
		threshold.SetInValue(in_value)  # set all values below 400 to 0
		threshold.ReplaceOutOn()
		threshold.SetOutValue(out_value)  # set all values above 400 to 1
		threshold.Update()
		return threshold

	def DMC(self, threshold):
		dmc = vtk.vtkDiscreteMarchingCubes()
		dmc.SetInputConnection(threshold.GetOutputPort())
		dmc.GenerateValues(1, 1, 1)
		dmc.Update()
		return dmc

	def VTK_Render(self):
		self.clean_gui()
		reader = vtk.vtkDICOMImageReader()
		reader.SetDirectoryName(self.PATH)
		reader.Update()
		threshold = self.Apply_Threshold(reader, self.ThreshScrollBar.value(), 0, 1)

		dmc = self.DMC(threshold)

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

		actor = vtk.vtkActor()
		actor.SetMapper(mapper)
		actor.GetProperty().SetColor(0.8,0.8,0.8) # (R,G,B)
		#actor.GetProperty().SetRepresentationToWireframe()  
		actor.GetProperty().SetRepresentationToSurface()

		self.ren.AddActor(actor)
		self.ren.ResetCamera()
		self.frame.setLayout(self.layout)
		self.setCentralWidget(self.frame)
		self.show()
		self.iren.Initialize()
		self.iren.Start()


if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	sys.exit(app.exec_())