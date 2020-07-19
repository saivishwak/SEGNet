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
from PyQt5.QtCore import Qt
import os

class TitleBar(QDialog):
    """ Titile Bar Customized """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setWindowFlags(Qt.FramelessWindowHint);
        css = """
        QWidget{
            Background: #474747;
            color:#E8E8E8;
            font:12px bold;
            font-weight:bold;
            border-radius: 0px;
            height: 5px;
            padding: 0px;
        }

        QDialog{
            font-size:12px;
            color: black;

        }

        QToolButton{
            font-size:11px;
        }

        QToolButton:hover{
            background: rgba(170, 170, 170, 0.3);
            opacity: 0.5;
            font-size:11px;
        }
        """
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.Highlight)
        self.setStyleSheet(css) 
        self.minimize= QToolButton(self)
        if os.sep=='\\':
            self.minimize.setIcon(QIcon('..\\Images\\minimize.png'))
        else:
            self.minimize.setIcon(QIcon('../Images/minimize.png'))
        self.maximize= QToolButton(self)
        if os.sep=='\\':
            self.maximize.setIcon(QIcon('..\\Images\\maximize.png'))
        else:
            self.maximize.setIcon(QIcon('../Images/maximize.png'))
        close= QToolButton(self)
        if os.sep=='\\':
            close.setIcon(QIcon('..\\Images\\close.png'))
        else:
            close.setIcon(QIcon('../Images/close.png'))
        #close.setIconSize(QtCore.QSize(30, 30))
        self.minimize.setMinimumHeight(20)
        close.setMinimumHeight(20)
        self.maximize.setMinimumHeight(20)
        label= QLabel(self)
        label.setText("SEGNet")
        logolabel = QLabel(self)
        if os.sep=='\\':
            imglogo = QImage('..\\Images\\Logo.png')
        else:
            imglogo = QImage('../Images/Logo.png')
        logopixmap = QPixmap.fromImage(imglogo)
        logolabel.setPixmap(logopixmap)
        logolabel.setFixedSize(20, 20)
        logolabel.setScaledContents(True)

        hbox= QHBoxLayout(self)
        hbox.addWidget(logolabel)
        hbox.addWidget(label)
        hbox.addWidget(self.minimize)
        hbox.addWidget(self.maximize)
        hbox.addWidget(close)
        hbox.insertStretch(2,500)
        hbox.setSpacing(10)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.maxNormal=False
        close.clicked.connect(self.close)
        self.minimize.clicked.connect(self.showSmall)
        self.maximize.clicked.connect(self.showMaxRestore)

    def showSmall(self):
        window.showMinimized()

    def showMaxRestore(self):
        if(self.maxNormal):
            window.showNormal()
            self.maxNormal= False
            if os.sep=='\\':
                self.maximize.setIcon(QIcon('..\\Images\\maximize.png'))
            else:
                self.maximize.setIcon(QIcon('../Images/maximize.png'))
        else:
            window.showMaximized()
            self.maxNormal=  True
            if os.sep=='\\':
                self.maximize.setIcon(QIcon('..\\Images\\maximize.png'))
            else:
                self.maximize.setIcon(QIcon('../Images/maximize.png'))

    def close(self):
        window.close()

    def mousePressEvent(self,event):
        if event.button() == Qt.LeftButton:
            window.moving = True; window.offset = event.pos()

    def mouseMoveEvent(self,event):
        if window.moving: window.move(event.globalPos()-window.offset)