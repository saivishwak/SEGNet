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

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import numpy as np
import vtk
from vtk.util import numpy_support
import cv2

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
		if len(self.ArrayDicom) != 0:
			if (QApplication.keyboardModifiers() == Qt.ControlModifier):
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
		if len(self.ArrayDicom) != 0:
			if (QApplication.keyboardModifiers() == Qt.ControlModifier):
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
		if len(self.ArrayDicom) != 0:
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
	def __init__(self, parent, label = "Axial"):
		super(Dicom_Widget, self).__init__(parent)
		self.label = label
		self.hide_seg = False
		self.initialize = 0
		self._zoom = 0
		self.low_hu = -1024
		self.high_hu = 3024
		self.thresh_val = 300
		self.ArrayDicom = []
		self.image_data = np.zeros((512, 512, 3))
		self.image_data = self.image_data.astype("uint8")
		self.image_data = self.image_data.copy()
		self.seg_data = []
		bytesPerLine = 3 * self.image_data.shape[1]
		self.image_length = 0
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

	def remove_segemntation(self):
		self.seg_data = []
		self.image_index = 0
		self.initialize = 0

	def hide_segmentation(self):
		if self.hide_seg == False:
			self.hide_seg = True
			if self.label == "Axial":
				self.image_data = self.ArrayDicom[:, :, int(self.image_index)]
				self.image_data = cv2.rotate(self.image_data, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE) 
				self.image_length = self.ArrayDicom.shape[2]
			elif self.label == "Sagittal":
				self.image_data = self.ArrayDicom[int(self.image_index), :, :]
				self.image_data = cv2.rotate(self.image_data, cv2.cv2.ROTATE_90_CLOCKWISE)
				self.image_data = cv2.flip(self.image_data, 1)
				self.image_length = self.ArrayDicom.shape[0]
			else:
				self.image_data = self.ArrayDicom[:, int(self.image_index), :]
				self.image_data = cv2.rotate(self.image_data, cv2.cv2.ROTATE_90_CLOCKWISE)
				self.image_length = self.ArrayDicom.shape[1]
			self.image_data = (self.image_data - self.low_hu) / self.high_hu * 256
			self.image_data[self.image_data < 0] = 0
			self.image_data[self.image_data > self.thresh_val] = 255 
			self.image_data = self.image_data.astype("uint8")
			self.update_image()
		else:
			self.hide_seg = False
			self.update_image()

	def update_image(self):
		if self.label == "Axial":
			self.image_data = self.ArrayDicom[:, :, int(self.image_index)]
			self.image_data = cv2.rotate(self.image_data, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE) 
			self.image_length = self.ArrayDicom.shape[2]
		elif self.label == "Sagittal":
			self.image_data = self.ArrayDicom[int(self.image_index), :, :]
			self.image_data = cv2.rotate(self.image_data, cv2.cv2.ROTATE_90_CLOCKWISE)
			self.image_data = cv2.flip(self.image_data, 1)
			self.image_length = self.ArrayDicom.shape[0]
		else:
			self.image_data = self.ArrayDicom[:, int(self.image_index), :]
			self.image_data = cv2.rotate(self.image_data, cv2.cv2.ROTATE_90_CLOCKWISE)
			self.image_length = self.ArrayDicom.shape[1]
		self.image_data = (self.image_data - self.low_hu) / self.high_hu * 256
		self.image_data[self.image_data < 0] = 0
		self.image_data[self.image_data > self.thresh_val] = 255 
		self.image_data = self.image_data.astype("uint8")
		if len(self.seg_data) != 0 and self.hide_seg == False:
			if self.label == "Axial":
				seg_slice = self.seg_data[:, :, int(self.image_index)]
				seg_slice = cv2.rotate(seg_slice, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
				dim = np.zeros((seg_slice.shape[1],seg_slice.shape[0]))
				seg_slice = np.stack((dim,seg_slice, dim), axis=2)
			elif self.label == "Sagittal":
				seg_slice = self.seg_data[int(self.image_index), :, :]
				seg_slice = cv2.rotate(seg_slice, cv2.cv2.ROTATE_90_CLOCKWISE)
				seg_slice = cv2.flip(seg_slice, 1)
				dim = np.zeros((seg_slice.shape[0],seg_slice.shape[1]))
				seg_slice = np.stack((dim,seg_slice, dim), axis=2)
			else:
				seg_slice = self.seg_data[:, int(self.image_index), :]
				seg_slice = cv2.rotate(seg_slice, cv2.cv2.ROTATE_90_CLOCKWISE)
				dim = np.zeros((seg_slice.shape[0],seg_slice.shape[1]))
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
		self.initialize += 1
		if self.initialize == 1 and len(self.ArrayDicom) != 0:
			self.fitInView()

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