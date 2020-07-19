import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure  
import matplotlib.pyplot as plt
import numpy as np


class MainWindow(QMainWindow):

	def __init__(self):
		super().__init__()
		self.TITLE = "SegNet"
		self.WIDTH = 900
		self.HEIGHT = 500
		self.PATH = ""
		self.InitUI()

	def InitUI(self):
		self.setWindowTitle(self.TITLE)
		self.setMinimumSize(self.WIDTH, self.HEIGHT)
		self.setWindowIcon(QIcon('.\\Images\\Logo.png'))
		self.setStyleSheet("""QMainWindow{
			background-color: white;}""")
		self.frame = QFrame()
		layout = QGridLayout()
		layout.setSpacing(2)

		self.Title_Label_A, self.Dicom_Frame_A, self.sc_A, self.Max_Win_A, self.ScrollBar_A, self.axes_A = self.Panel("Axial Slice", "R", "L", "A", "P")

		layout.addWidget(self.Title_Label_A, 0, 0)
		layout.addWidget(self.Max_Win_A, 0, 1)
		layout.addWidget(self.Dicom_Frame_A, 1, 0)
		layout.addWidget(self.ScrollBar_A, 1, 1)

		self.Title_Label_S, self.Dicom_Frame_S, self.sc_S, self.Max_Win_S, self.ScrollBar_S, self.axes_S = self.Panel("Sagittal Slice", "P", "A", "T", "B")

		layout.addWidget(self.Title_Label_S, 0, 2)
		layout.addWidget(self.Max_Win_S, 0, 3)
		layout.addWidget(self.Dicom_Frame_S, 1, 2)
		layout.addWidget(self.ScrollBar_S, 1, 3)

		self.Title_Label_C, self.Dicom_Frame_C, self.sc_C, self.Max_Win_C, self.ScrollBar_C, self.axes_C = self.Panel("Coronal Slice", "R", "L", "T", "B")

		layout.addWidget(self.Title_Label_C, 2, 0)
		layout.addWidget(self.Max_Win_C, 2, 1)
		layout.addWidget(self.Dicom_Frame_C, 3, 0)
		layout.addWidget(self.ScrollBar_C, 3, 1)

		self.Title_Label_V, self.Dicom_Frame_V, self.sc_V, self.Max_Win_V, self.ScrollBar_V, self.axes_V = self.Panel("Volume", "", "", "", "")

		layout.addWidget(self.Title_Label_V, 2, 2)
		layout.addWidget(self.Max_Win_V, 2, 3)
		layout.addWidget(self.Dicom_Frame_V, 3, 2)
		layout.addWidget(self.ScrollBar_V, 3, 3)


		get_dic = QAction('&Import DICOM...', parent = self)
		get_dic.setShortcut('Ctrl+I')
		get_dic.setStatusTip('Select DICOM Folder')
		
		get_dic.triggered.connect(self.get_dic)
		
		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(get_dic)

		self.frame.setLayout(layout)
		self.setCentralWidget(self.frame)

		#self.update()
		self.show()


	def get_dic(self):
		options = QFileDialog.Options()
		fileName = str(QFileDialog.getExistingDirectory())
		if fileName:
			if os.sep=='\\':
			    fileName=fileName.replace('/', "\\")
		self.PATH = fileName
		print('Imported Files From:', self.PATH)
		#self.update()

	def update(self):
		self.axes_V.imshow(np.random.random((512, 512)))

	def Panel(self, title, text_1, text_2, text_3, text_4):
		Title_Label = QLabel("{}".format(title), self)
		Title_Label.setStyleSheet('QLabel { background: #b5b5b5; border-radius: 0px; font-size: 12px; padding: 5px; font-weight: 485}')
		figure = plt.figure(figsize=(10, 10), dpi=100, facecolor='black')
		axes = figure.add_subplot(1,1,1)
		#Dicom_Frame = QLabel(self)
		#Dicom_Frame.setStyleSheet('QLabel { background: #b5b5b5; border-radius: 0px; font-size: 12px; padding: 5px; font-weight: 485}')
		data = np.zeros((512, 512))
		sc = FigureCanvas(figure)
		axes.imshow(data, cmap = 'gray')
		axes.xaxis.set_visible(False)
		axes.yaxis.set_visible(False)
		axes.text(-280, 250, '{}'.format(text_1), fontsize=10, color = 'white')
		axes.text(700, 250, '{}'.format(text_2), fontsize=10, color = 'white')
		axes.text(260, 0, '{}'.format(text_3), fontsize=10, color = 'white')
		axes.text(260, 550, '{}'.format(text_4), fontsize=10, color = 'white')
		Dicom_Frame = sc
		Max_Win = QLabel(self)
		#self.pixmap = QPixmap()
		#self.pixmap_Win = QPixmap('.\\Images\\maximize-window.png')
		#self.Max_Win.setPixmap(self.pixmap_Win)
		#self.Max_Win.setScaledContents(True)
		Max_Win.setFixedSize(18, 25)
		Max_Win.setStyleSheet('QLabel { background: #b5b5b5; border-radius: 0px;}')
		ScrollBar = QScrollBar(self)
		ScrollBar.setOrientation(Qt.Vertical)
		ScrollBar.setObjectName("ScrollBar")

		return Title_Label, Dicom_Frame, sc, Max_Win, ScrollBar, axes


if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	sys.exit(app.exec_())