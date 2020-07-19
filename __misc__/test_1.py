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
import cv2
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.util import numpy_support


class DICOM_Widget(QLabel):
    def __init__(self, parent):
        super(DICOM_Widget, self).__init__(parent)
        #self._image = None
        #self._pixmap = None
        self.data = np.zeros((128, 128))
        self.data[self.data < 0] = 0
        self.data[self.data > 255] = 255
        self.data = self.data.astype("int8")
        self._image = QImage(self.data, self.data.shape[1], self.data.shape[0], QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(self._image)
        self._pixmap = pixmap
        self.setPixmap(self._pixmap)
        #self.setScaledContents(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAlignment(Qt.AlignCenter)

    def update(self):
        self._image = QImage(self.data, self.data.shape[1], self.data.shape[0], QImage.Format_Indexed8)
        pixmap = QPixmap.fromImage(self._image)
        self._pixmap = pixmap
        self.setPixmap(self._pixmap)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.TITLE = "SegNet"
        self.WIDTH = 1200
        self.HEIGHT = 700
        self.PATH = ""
        self.InitUI()

    def InitUI(self):
        self.setWindowTitle(self.TITLE)
        #self.setMinimumSize(self.WIDTH, self.HEIGHT)
        self.resize(self.WIDTH, self.HEIGHT)
        #self.setFixedWidth(self.WIDTH)
        #self.setFixedHeight(self.HEIGHT)
        self.setWindowIcon(QIcon('.\\Images\\Logo.png'))
        self.setStyleSheet("""QMainWindow{
            background-color: white;}""")
        self.frame = QFrame()
        self.frame.setStyleSheet("QFrame {background-color: black}")
        self.layout = QGridLayout()
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)
        self.layout.setRowStretch(2, 1)
        self.layout.setRowStretch(3, 1)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)
        self.layout.setColumnStretch(3, 1)
        self.layout.setSpacing(2)

        self.Vtk_Widget = QVTKRenderWindowInteractor(self.frame)
        self.Vtk_Widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(1, 1, 1)
        self.Vtk_Widget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.Vtk_Widget.GetRenderWindow().GetInteractor()

        self.Axial_Slice = DICOM_Widget(self)
        self.Sagittal_Slice = DICOM_Widget(self)
        self.Coronal_Slice = DICOM_Widget(self)

        Axial_label = QLabel("Axial Slice",self)
        Axial_label.setStyleSheet('QLabel { background: #b5b5b5; border-radius: 0px; font-size: 12px; padding: 5px; font-weight: 485}')

        Sagittal_label = QLabel("Sagittal Slice",self)
        Sagittal_label.setStyleSheet('QLabel { background: #b5b5b5; border-radius: 0px; font-size: 12px; padding: 5px; font-weight: 485}')

        Coronal_label = QLabel("Coronal Slice",self)
        Coronal_label.setStyleSheet('QLabel { background: #b5b5b5; border-radius: 0px; font-size: 12px; padding: 5px; font-weight: 485}')

        volume_label = QLabel("Volume",self)
        volume_label.setStyleSheet('QLabel { background: #b5b5b5; border-radius: 0px; font-size: 12px; padding: 5px; font-weight: 485}')

        self.ScrollBar_A = QScrollBar(self)
        self.ScrollBar_A.setOrientation(Qt.Vertical)
        self.ScrollBar_A.sliderMoved.connect(self.sliderval)
        self.ScrollBar_A.valueChanged.connect(self.sliderval)
        self.ScrollBar_A.setObjectName("ScrollBar Axial")
        self.ScrollBar_S = QScrollBar(self)
        self.ScrollBar_S.setOrientation(Qt.Vertical)
        self.ScrollBar_S.sliderMoved.connect(self.sliderval)
        self.ScrollBar_S.valueChanged.connect(self.sliderval)
        self.ScrollBar_S.setObjectName("ScrollBar Sagittal")
        self.ScrollBar_C = QScrollBar(self)
        self.ScrollBar_C.setOrientation(Qt.Vertical)
        self.ScrollBar_C.sliderMoved.connect(self.sliderval)
        self.ScrollBar_C.valueChanged.connect(self.sliderval)
        self.ScrollBar_C.setObjectName("ScrollBar Coronal")
        self.ScrollBar_V = QScrollBar(self)
        self.ScrollBar_V.setOrientation(Qt.Vertical)
        self.ScrollBar_V.setObjectName("ScrollBar Volume")

        extra_1 = QLabel(self)
        extra_1.setStyleSheet('QLabel { background: #b5b5b5; border-radius: 0px;}')
        extra_1.setFixedSize(18, 25)
        extra_2 = QLabel(self)
        extra_2.setStyleSheet('QLabel { background: #b5b5b5; border-radius: 0px;}')
        extra_2.setFixedSize(18, 25)
        extra_3 = QLabel(self)
        extra_3.setStyleSheet('QLabel { background: #b5b5b5; border-radius: 0px;}')
        extra_3.setFixedSize(18, 25)
        extra_4 = QLabel(self)
        extra_4.setStyleSheet('QLabel { background: #b5b5b5; border-radius: 0px;}')
        extra_4.setFixedSize(18, 25)


        self.layout.addWidget(Axial_label, 0, 0, 1, 1)
        self.layout.addWidget(extra_1, 0, 1, 1, 1)
        self.layout.addWidget(self.Axial_Slice, 1, 0, 1, 1)
        self.layout.addWidget(self.ScrollBar_A, 1, 1, 1, 1)

        self.layout.addWidget(Sagittal_label, 0, 2, 1, 1)
        self.layout.addWidget(extra_2, 0, 3, 1, 1)
        self.layout.addWidget(self.Sagittal_Slice, 1, 2, 1, 1)
        self.layout.addWidget(self.ScrollBar_S, 1, 3, 1, 1)

        self.layout.addWidget(Coronal_label, 2, 0, 1, 1)
        self.layout.addWidget(extra_3, 2, 1, 1, 1)
        self.layout.addWidget(self.Coronal_Slice, 3, 0, 1, 1)
        self.layout.addWidget(self.ScrollBar_C, 3, 1, 1 , 1)


        self.layout.addWidget(volume_label, 2, 2, 1, 1)
        self.layout.addWidget(extra_4, 2, 3, 1, 1)
        self.layout.addWidget(self.Vtk_Widget, 3, 2, 1, 2)
        #self.layout.addWidget(self.ScrollBar_V, 3, 3, 1, 1)

        self.frame.setLayout(self.layout)
        self.setCentralWidget(self.frame)

        source = vtk.vtkCylinderSource()
        source.SetCenter(0, 0, 0)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.ren.AddActor(actor)
        self.iren.Initialize()
        self.iren.Start()

        exitAct = QAction("&Exit", self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        get_dic = QAction('&Import DICOM...', self)
        get_dic.setShortcut('Ctrl+I')
        get_dic.setStatusTip('Select DICOM Folder')
        get_dic.triggered.connect(self.get_dir)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        toolsMenu = menubar.addMenu('&Tools')
        fileMenu.addAction(get_dic)
        fileMenu.addAction(exitAct)
        
        self.show()

    def get_dir(self):
        options = QFileDialog.Options()
        fileName = str(QFileDialog.getExistingDirectory())
        if fileName:
            if os.sep=='\\':
                fileName=fileName.replace('/', "\\")
        self.PATH = fileName
        print('Dicom Imported From:', self.PATH)
        self.read_dicom()
        self.update_images()

    def read_dicom(self):
        self.reader = vtk.vtkDICOMImageReader()
        self.reader.SetDirectoryName('G:\\BMU\\Research\\Bio-Mechanics\\Scans\\Rockland CT\\DICOM\\Abdomen 24Y\\S30')
        self.reader.Update()
        _extent = self.reader.GetDataExtent()
        self.ConstPixelDims = [_extent[1]-_extent[0]+1, _extent[3]-_extent[2]+1, _extent[5]-_extent[4]+1]
                # Load spacing values
        self.ConstPixelSpacing = self.reader.GetPixelSpacing()
        self.pointData = self.reader.GetOutput().GetPointData()
        self.arrayData = self.pointData.GetArray(0)
        self.ArrayDicom = numpy_support.vtk_to_numpy(self.arrayData)
        self.ArrayDicom = self.ArrayDicom.reshape(self.ConstPixelDims, order='F')
        self.ArrayDicom = (self.ArrayDicom + 1024) / 3024 * 256
        self.ArrayDicom[self.ArrayDicom < 0] = 0
        self.ArrayDicom[self.ArrayDicom > 255] = 255
        self.scroll_val_A = 0
        self.scroll_val_S = 0
        self.scroll_val_C = 0
        self.ScrollBar_A.setMaximum(len(self.ArrayDicom)-1)
        self.ScrollBar_S.setMaximum(len(self.ArrayDicom)-1)
        self.ScrollBar_C.setMaximum(len(self.ArrayDicom)-1)

    def update_images(self):
        self.Axial_Img = self.ArrayDicom[:, :, self.scroll_val_A]
        self.Axial_Img = self.Axial_Img.astype("uint8")
        self.Axial_Img = self.Axial_Img.copy()
        #cv2.imwrite('.\\Images\\Axial_img.png', self.Axial_Img)
        #self.Axial_Img = cv2.imread(".\\Images\\Axial_img.png", 0)
        #self.Axial_Img = cv2.resize(self.Axial_Img, (200, 200))
        #self.Axial_Img = cv2.rotate(self.Axial_Img, cv2.cv2.ROTATE_90_CLOCKWISE)
        #self.Axial_Img = cv2.copyMakeBorder(self.Axial_Img, 50 ,50 ,50 ,50, cv2.BORDER_CONSTANT, value= [0, 0, 0])
        #cv2.putText(self.Axial_Img, "R", (0,120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        #cv2.putText(self.Axial_Img, "R", (100,0), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        #added_image = cv2.addWeighted(background,0.4,overlay,0.1,0)        # For Overlay Image

        self.Sagittal_Img = self.ArrayDicom[:, self.scroll_val_S, :]
        cv2.imwrite('.\\Images\\Axial_img.png', self.Sagittal_Img)
        self.Sagittal_Img = cv2.imread(".\\Images\\Axial_img.png", 0)
        self.Sagittal_Img = cv2.resize(self.Sagittal_Img, (200, 200))
        self.Sagittal_Img = cv2.rotate(self.Sagittal_Img, cv2.cv2.ROTATE_90_CLOCKWISE)
        self.Sagittal_Img = cv2.copyMakeBorder(self.Sagittal_Img, 50 ,50 ,50 ,50, cv2.BORDER_CONSTANT, value= [0, 0, 0])

        self.Coronal_Img = self.ArrayDicom[self.scroll_val_C, :, :]
        cv2.imwrite('.\\Images\\Axial_img.png', self.Coronal_Img)
        self.Coronal_Img = cv2.imread(".\\Images\\Axial_img.png", 0)
        self.Coronal_Img = cv2.resize(self.Coronal_Img, (200, 200))
        self.Coronal_Img = cv2.rotate(self.Coronal_Img, cv2.cv2.ROTATE_90_CLOCKWISE)
        self.Coronal_Img = cv2.copyMakeBorder(self.Coronal_Img, 50 ,50 ,50 ,50, cv2.BORDER_CONSTANT, value= [0, 0, 0])

        self.Axial_Slice.data = self.Axial_Img
        self.Axial_Slice.update()

        self.Sagittal_Slice.data = self.Sagittal_Img
        self.Sagittal_Slice.update()

        self.Coronal_Slice.data = self.Coronal_Img
        self.Coronal_Slice.update()

    def sliderval(self):
        self.scroll_val_A = self.ScrollBar_A.value()
        self.scroll_val_S = self.ScrollBar_S.value()
        self.scroll_val_C = self.ScrollBar_C.value()
        self.update_images()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())