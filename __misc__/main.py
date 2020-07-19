from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import numpy as np
import vtk
from vtk.util import numpy_support
import SimpleITK as sitk
import cv2
import time

reader = vtk.vtkDICOMImageReader()
reader.SetDirectoryName('G:\\BMU\\Research\\Bio-Mechanics\\Scans\\Rockland CT\\DICOM\\Abdomen 24Y\\S30')
reader.Update()

_extent = reader.GetDataExtent()
ConstPixelDims = [_extent[1]-_extent[0]+1, _extent[3]-_extent[2]+1, _extent[5]-_extent[4]+1]
ConstPixelSpacing = reader.GetPixelSpacing()
pointData = reader.GetOutput().GetPointData()
arrayData = pointData.GetArray(0)
ArrayDicom = numpy_support.vtk_to_numpy(arrayData)
ArrayDicom = ArrayDicom.reshape(ConstPixelDims, order='F')
#ArrayDicom = (ArrayDicom + 1024) / 3024 * 256
#ArrayDicom[ArrayDicom < 0] = 0
#ArrayDicom[ArrayDicom  > 255] = 255
#print(ArrayDicom.shape)
data = ArrayDicom[:, :, 100]
data[data < 300] = 0
data[data >= 300] = 200
dim = np.zeros((data.shape[1],data.shape[0]))
data = np.stack((dim,data, dim), axis=2)
data = data.astype("uint8")
#data = np.transpose(data, (1 , 0)).copy()
#cv2.imshow("i", data)
#cv2.waitKey(0)

class TrackingLabel(QGraphicsView):
	def __init__(self, parent):
		super(TrackingLabel, self).__init__(parent)
		self.setMouseTracking(True)
		self.last_move_x = None
		self.last_move_y = None
		self.window = parent
		self.image_index = 0
		self.x = 0
		self.y = 0
	
	def mouseLeaveEvent(self, event):
		pass

	def mouseMoveEvent(self, event):
		if (app.keyboardModifiers() == Qt.ControlModifier):
			if event.buttons() == QtCore.Qt.LeftButton:
				self.y += event.y() - self.last_move_y
				self.x += event.x() - self.last_move_x
				self._photo.setPos(QPoint(self.x/3, self.y/3))

		if event.buttons() == QtCore.Qt.RightButton:
			y = event.y() - self.last_move_y
			x = event.x() - self.last_move_x
			if y > 0:
				self.low_hu += 30
			elif y < 0:
				self.low_hu -= 30
			if x > 0:
				self.high_hu += 30
			elif x < 0:
				self.high_hu -= 30

		self.update_image()
		self.last_move_x = event.x()
		self.last_move_y = event.y()

	def mousePressEvent(self, event: QtGui.QMouseEvent):
		self.last_move_x = event.x()
		self.last_move_y = event.y()

	def mouseReleaseEvent(self, event):
		self.last_move_x = None
		self.last_move_y = None
	

	def wheelEvent(self, event: QWheelEvent):
		if (app.keyboardModifiers() == Qt.ControlModifier):
			if event.angleDelta().y() > 0:
				factor = 1.25
				self._zoom += 1
			else:
				factor = 0.8
				self._zoom -= 1
			if self._zoom > 0:
				self.scale(factor, factor)
			else:
				self.scale(factor, factor)

		else:
			numDegrees = event.angleDelta().y() / 8
			numSteps = -(numDegrees / 15.0)
			self.image_index += numSteps
			if self.image_index < 0:
				self.image_index = 0
			elif self.image_index > self.image_length-1:
				self.image_index = self.image_length-1

			self.photoClicked.emit(QPoint(int(self.image_index), 0))
			self.update_image()
	
	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key_R:
			self.low_hu = -1024
			self.high_hu = 3024
			#self.image_index = 0
			self._photo.setPos(QPoint(0, 0))
			self.fitInView()
			self.update_image()
	

class Dicom_Widget(TrackingLabel):
	""" DICOM Slice Viewing widget """
	photoClicked = QtCore.pyqtSignal(QtCore.QPoint)
	def __init__(self, parent):
		super(Dicom_Widget, self).__init__(parent)
		self._zoom = 0
		self.low_hu = -1024
		self.high_hu = 3024
		self.image_data = ArrayDicom[:, :, self.image_index]
		self.image_data = (self.image_data - self.low_hu) / self.high_hu * 256
		self.image_data[self.image_data < 0] = 0
		self.image_data[self.image_data > 255] = 255 
		self.image_data = self.image_data.astype("uint8")
		self.image_data = np.stack((self.image_data,self.image_data, self.image_data), axis=2)
		#self.image_data = cv2.addWeighted(self.image_data,1,data,1,0)
		self.image_data = self.image_data.copy()
		self.seg_data = []
		bytesPerLine = 3 * self.image_data.shape[1]
		#self.image_data = np.transpose(self.image_data, (1 , 0)).copy() 
		self.image_length = ArrayDicom.shape[-1]
		self._scene = QGraphicsScene(self)
		self._image = QImage(self.image_data, self.image_data.shape[1], self.image_data.shape[0], bytesPerLine, QImage.Format_RGB888)
		self._photo = QGraphicsPixmapItem()
		self._pixmap = QPixmap.fromImage(self._image)
		self._photo.setPixmap(self._pixmap)
		self._scene.addItem(self._photo)

		self.setAlignment(Qt.AlignCenter)
		#self.setMouseTracking(True)
		self.setScene(self._scene)
		self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
		self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
		self.setFrameShape(QtWidgets.QFrame.NoFrame)
		self.segment_slice()

	def segment_slice(self):
		self.seg_data = ArrayDicom.copy()
		self.seg_data[self.seg_data < 300] = 0
		self.seg_data[self.seg_data >= 300] = 200
		self.update_image()


	def remove_segmentation(self):
		self.seg_data = []
		self.update_image()

	def update_image(self):
		self.image_data = ArrayDicom[:, int(self.image_index), :]
		self.image_data = (self.image_data - self.low_hu) / self.high_hu * 256
		self.image_data[self.image_data < 0] = 0
		self.image_data[self.image_data > 255] = 255 
		self.image_data = self.image_data.astype("uint8")
		if len(self.seg_data) != 0:
			seg_slice = self.seg_data[:, int(self.image_index), :]
			dim = np.zeros((seg_slice.shape[0],seg_slice.shape[1]))
			print(dim.shape)
			seg_slice = np.stack((dim,seg_slice, dim), axis=2)
			seg_slice = seg_slice.astype("uint8")
			self.image_data = np.stack((self.image_data,self.image_data, self.image_data), axis=2)
			self.image_data = cv2.addWeighted(self.image_data,1,seg_slice,1,0)
		else:
			self.image_data = np.stack((self.image_data,self.image_data, self.image_data), axis=2)
		#self.image_data = np.transpose(self.image_data, (1 , 2, 0)).copy()
		self.image_data = self.image_data.copy()
		bytesPerLine = 3 * self.image_data.shape[1]
		self._image = QImage(self.image_data, self.image_data.shape[1], self.image_data.shape[0], bytesPerLine, QImage.Format_RGB888)
		self._pixmap = QPixmap.fromImage(self._image)
		self._photo.setPixmap(self._pixmap)

	def fitInView(self, scale=True):
		rect = QtCore.QRectF(self._photo.pixmap().rect())
		if not rect.isNull():
			self.setSceneRect(rect)
			unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
			self.scale(1 / unity.width(), 1 / unity.height())
			viewrect = self.viewport().rect()
			scenerect = self.transform().mapRect(rect)
			factor = min(viewrect.width() / scenerect.width(),
			             viewrect.height() / scenerect.height())
			self.scale(factor, factor)
			self._zoom = 0

class Mainwindow(QMainWindow):
	def __init__(self, parent = None):
		super().__init__()
		layout = QVBoxLayout()
		self.widget = Dicom_Widget(self)
		self.Scroll = QScrollBar(self)
		self.Scroll.setOrientation(Qt.Horizontal)
		self.Scroll.sliderMoved.connect(self.sliderval)
		self.Scroll.valueChanged.connect(self.sliderval)
		self.Scroll.setMaximum(self.widget.image_length - 1)
		self.widget.photoClicked.connect(self.photoClicked)
		self.editPixInfo = QtWidgets.QLabel(self)
		#self.editPixInfo.setReadOnly(True)
		layout.addWidget(self.Scroll)
		layout.addWidget(self.widget)
		layout.addWidget(self.editPixInfo)

		widget = QWidget()
		widget.setLayout(layout)
		self.setCentralWidget(widget)
		self.show()

	def photoClicked(self, pos):
		self.editPixInfo.setText('%d' % (pos.x()))
		self.Scroll.setValue(pos.x())

	def sliderval(self):
		self.widget.image_index = self.Scroll.value()
		self.widget.update_image()
		self.editPixInfo.setText('%d' % (self.Scroll.value()))

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = Mainwindow()
	sys.exit(app.exec_())