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
import sys
import time
import os

from GUI import Mainwindow
import Title_Bar


if __name__ == "__main__":
	app = QApplication(sys.argv)
	app.setStyleSheet(open('style.css').read())
	if os.sep=='\\':
		splash_pix = QPixmap('..\\Images\\splash.png')
	else:
		splash_pix = QPixmap('../Images/splash.png')

	splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
	splash.setMask(splash_pix.mask())
	splash.show()
	app.processEvents()

	time.sleep(2)
	splash.close()

	app_icon = QIcon()
	if os.sep=='\\':
		app_icon.addFile('..\\Images\\Logo.png', QSize(16,16))
	else:
		app_icon.addFile('../Images/Logo.png', QSize(16,16))
		
	app.setWindowIcon(app_icon)

	window = Mainwindow()
	Title_Bar.window = window
	sys.exit(app.exec_())